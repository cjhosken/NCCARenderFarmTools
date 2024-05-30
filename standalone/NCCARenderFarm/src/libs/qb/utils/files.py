#=======================================
#  $Revision: #1 $
#  $Change: 22715 $
#=======================================


import os.path
import re
import logging

import qb
from qb.utils.exceptions import QubeUtilityGeneralError


class WorkerConfigFile(object):
    """
    A class to read and write the qbwrk.conf file on the supervisor; this file contains blocks
    herein referred to as "stanzas" for each template or host definition.

    An example qbwrk.conf that has 3 stanzas looks like:
        [default]
        worker_cpus = 0
        
        [test]:
        worker_description = 'this is a test host'

        [some-host-name] : test
        worker_resources = host.foo=4
        worker_path_map = {
            "/Users/sam" = "S:"
            "/Users/test" = "T:"
        }

    @ivar cfg: a dict of dicts to hold all the stanzas
        
        The top-level key is the stanza name, the string that appears between the square brackets.

        For each stanza dict, there will be a key for each parameter in the stanza, as well as the
        following reserved-word keys:
            - inherits: the list of templates that occurs after the ":" in the stanza definition
              line

            - index: the zero-based index which indicates the ordering of the stanzas in the cfgFile

        Any of the *_map type multi-line hash-like values are stored as lists of tuples, since the
        values are always C{src = target}
        
    """
    RGX_STANZA_DEF = re.compile('^\[([a-zA-Z0-9_\.\[\]-]+)\]\s*:?\s*([^#]*)#?.*$')  # match [template] : inherit inherit...  (template name can contain a '.' or a h[1-2] range)
    RGX_BLANK_LINE = re.compile('^\s*$')
    RGX_PARAM = re.compile('^(\w+)\s*=\s*(.*)#?.*$')                                # match foo = bar
    RGX_MAPPING_PARAM = re.compile('^(\w+map)\s*=\s*{(.*)}?$')                      # match *_map = { 
    RGX_PATH_MAPPING_DEF = re.compile('^\s*(.*)\s*=\s*(.*)\s*$')                         # match X: = /foo/bar    or   /foo/bar = Y:
    RGX_DRIVE_MAPPING_DEF = re.compile('^\s*([A-Z]{1}:|.*)\s*$')                         # match X: = /foo/bar    or   /foo/bar = Y:

    def __init__(self, cfgFile=None):
        '''
        @param cfgFile: file path to the central worker config file
        @type cfgFile: C{str}
        '''
        self.logging = logging.getLogger('%s' % self.__class__.__name__)
        self.cfgFileExists = True

        if cfgFile == None:
            cfgFile =  qb.supervisorconfig().get('supervisor_worker_configfile', qb.QB_SUPERVISOR_CONFIG_DEFAULT_WORKER_CONFIGFILE)

        self.cfgFile = cfgFile
        if not os.path.isfile(self.cfgFile):
            errMsg = 'Worker config file not found: %s, will be created.' % self.cfgFile
            self.logging.warning(errMsg)
            self.cfgFileExists = False

        # a dict to hold all the different "stanzas" in the qbwrk.conf
        self.cfg = {}

        # a list of keys in each stanza dictionary that should be culled when building the contents
        # of the config file for writing
        self.reservedKeyWords = ['index', 'inherits', 'delete']

    def read(self):
        '''
        Parse the cfgFile, turn it into a dictionary of dictionaries
        '''
        self.cfg = {} # re-init the config just in case this is called multiple times

        # bail if the cfgFile does not yet exist, we've already initialized the cfg dictionary
        if not self.cfgFileExists:
            return

        stanzaName = ''
        mapName = ''            # some worker_*_map parameters span multiple lines

        inMappingBlock = False
        commentWarningRaised = False

        for line in open(self.cfgFile).readlines():

            line.strip()
            if self.RGX_BLANK_LINE.search(line):
                continue

            if line.startswith('#'):
                if not commentWarningRaised:
                    self.logging.warning('Worker config file contains comments, these will be stripped out when the new file is written')
                    commentWarningRaised = True
                continue

            if line.startswith('}'):
                inMappingBlock = False
                continue

            stanzaMatch = self.RGX_STANZA_DEF.search(line)
            if stanzaMatch:
                # init a new stanza dict, set the stanzaName for the next iteration through the
                # readlines loop
                try:
                    stanzaOrder = len(self.cfg)
                    (stanzaName, inherits) = stanzaMatch.groups()

                    if stanzaName.count('['):
                        self.logging.warning('Worker config file utilizes a host range: %s.  It will be retained but not modified' % stanzaName)

                    self.cfg[stanzaName] = {
                        'index': stanzaOrder,
                        'inherits': inherits.strip(),
                        'delete': []
                    }

                except Exception as e:
                    print(e)
                continue

            if inMappingBlock:
                pathMapMatch = self.RGX_PATH_MAPPING_DEF.search(line)
                if pathMapMatch:
                    try:
                        # clean up whitespace and get rid of double-quotes
                        (src, target) = [y.replace('"', '') for y in [x.strip() for x in pathMapMatch.groups()] ]
                        self.cfg[stanzaName].get(mapName, []).append('"%s" = "%s"' % (src, target)) 

                    except Exception as e:
                        print(e)
                    continue
                else:
                    driveMapMatch = self.RGX_DRIVE_MAPPING_DEF.search(line)
                    if driveMapMatch:
                        try:
                            self.cfg[stanzaName].get(mapName, []).append( driveMapMatch.group(1) )
                        except Exception as e:
                            print(e)
                        continue

            mappingParamMatch = self.RGX_MAPPING_PARAM.search(line)
            if mappingParamMatch:
                inMappingBlock = True
                try:
                    (mapName, mapVal) = mappingParamMatch.groups()
                    self.cfg[stanzaName][mapName] = []
                    # only one mapping can defined in the first line, so split the value into
                    # a tuple
                    if mapVal.count('='):
                        mapVal = tuple( [x.strip() for x in mapVal.split('=')] )

                    # don't add blank lines
                    if mapVal:
                        self.cfg[stanzaName][mapName].append(mapVal)

                    if mapVal.count('}'):
                        # the map block is closed on the same line
                        inMappingBlock = False

                except Exception as e:
                    print(e)
                continue

            paramMatch  = self.RGX_PARAM.search(line)
            if paramMatch:
                try:
                    (paramName, paramVal) = paramMatch.groups()
                    self.cfg[stanzaName][paramName] = paramVal
                except Exception as e:
                    print(e)
                continue
        
        # now convert any of the mapping parameters from a list to string
        # and cull any empty lists
        for stanzaName in list(self.cfg.keys()):
            stanza = self.cfg[stanzaName]
            for paramName in [x for x in list(stanza.keys()) if x.endswith('_map')]:
                if stanza[paramName]:
                    stanza[paramName] = '\n'.join(stanza[paramName])
                else:
                    del stanza[paramName]
                
    def mergeConfigs(self, newCfg):
        '''
        @param newCfg: a dictionary containing all the config file parameters to update, keyed by hostname
        @type newCfg: C{dict}
        '''
        for stanzaName in newCfg:
            if stanzaName not in self.cfg:
                self.cfg[stanzaName] = {
                    'index': len(self.cfg),
                    'inherits': '',
                    'delete': []
                }

            self.cfg[stanzaName].update(newCfg[stanzaName])

    def write(self):
        '''
        @raise: raise QubeUtilityGeneralError on any failure to successfully update the worker config file
        '''
        data = []
        # write out the stanzas by the original order in which they appeared in the config file
        for (stanzaName, stanza) in sorted(iter(self.cfg.items()), key=lambda k_v: k_v[1]['index']):
            templateLine = '[%s]' % stanzaName
            if stanza['inherits']:
                templateLine += ' : %s' % stanza['inherits']
            data.append(templateLine)

            for paramName in sorted([x for x in stanza if x not in self.reservedKeyWords]):
                if paramName not in stanza['delete']:

                    if paramName.endswith('_map'):
                        stanza[paramName] = stanza[paramName].strip() 
                        if paramName.count('path_map'):
                            data.append('%s = {' % paramName)
                            for pathMapping in stanza[paramName].split('\n'):
                                data.append('  %s' % pathMapping.strip())
                        else:
                            # worker_drive_map needs the first mapping on the first line
                            mappings = stanza[paramName].split('\n')
                            data.append('%s = {%s' % (paramName, mappings[0]))
                            for driveMapping in mappings[1:]:
                                data.append('%s' % driveMapping.strip())
                        data.append('}')
                    else:
                        data.append('%s = %s' % (paramName, stanza[paramName]))

            data.append('')

        # blank line on the end
        data.append('')

        errMsg = qb.utils.sudoWrite('\n'.join(data), self.cfgFile)
        if errMsg:
            raise QubeUtilityGeneralError(errMsg)



if __name__ == '__main__':
    
    from pprint import pprint as pp
    import logging
    logging.basicConfig()

    testCfg = {
        'foobar': {'worker_description': 'the foobar host - v2', 'worker_cpus': '2'},
        #'default': {'worker_description': '"DEAFAULT DESCRIPTION"'}
    }

    wcf = WorkerConfigFile('/tmp/qbwrk.conf')
    wcf.read()
    wcf.mergeConfigs(testCfg)
    wcf.write()

