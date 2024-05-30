## -----------------------------------------------------------------------------
##   
##      Module defining expected default installation paths for some common
##      3d-party applications
##
##      Copyright: Pipelinefx L.L.C. 
##
## -----------------------------------------------------------------------------

#======================================
#  $Revision: #1 $
#  $Change: 22715 $
#======================================

import os.path
import platform
import logging
import socket

from qb.backend import QubeBackEndError


installPath = {
    'AE': {
        # expected to have 1, 2 or 3 values; 5->(5), 5.5->(5,5), 6->(6), CC, CC 2014, CC 2015.3
        'Darwin':       [
            '/Applications/Adobe After Effects %(v1)s/aerender',
            '/Applications/Adobe After Effects %(v1)s %(v2)s/aerender',
            '/Applications/Adobe After Effects %(v1)s %(v2)s.%(v3)s/aerender',
            '/Applications/Adobe After Effects CS%(v1)s/aerender',
            '/Applications/Adobe After Effects CS%(v1)s.%(v2)s/aerender'
        ],
        'Windows':      [
            'C:/Program Files/Adobe/Adobe After Effects %(v1)s/Support Files/aerender.exe',
            'C:/Program Files/Adobe/Adobe After Effects %(v1)s %(v2)s/Support Files/aerender.exe',
            'C:/Program Files/Adobe/Adobe After Effects %(v1)s %(v2)s.%(v3)s/Support Files/aerender.exe',
            'C:/Program Files/Adobe/Adobe After Effects CS%(v1)s/Support Files/aerender.exe',
            'C:/Program Files/Adobe/Adobe After Effects CS%(v1)s.%(v2)s/Support Files/aerender.exe',
            #
            'C:/Program Files (x86)/Adobe/Adobe After Effects %(v1)s/Support Files/aerender.exe',
            'C:/Program Files (x86)/Adobe/Adobe After Effects %(v1)s %(v2)s/Support Files/aerender.exe',
            'C:/Program Files (x86)/Adobe/Adobe After Effects %(v1)s %(v2)s.%(v3)s/Support Files/aerender.exe',
            'C:/Program Files (x86)/Adobe/Adobe After Effects CS%(v1)s/Support Files/aerender.exe',
            'C:/Program Files (x86)/Adobe/Adobe After Effects CS%(v1)s.%(v2)s/Support Files/aerender.exe',
        ],
    },
    'C4D': {
        # expected to have 1 or 2 values; R12->(12), R13.5->(13,5)
        # Maxon installs the 32- and 64-bit exe's in the same dir on 64-bit OS's...
        'Darwin':       [
            '/Applications/MAXON/CINEMA 4D R%(v1)s/CINEMA 4D.app/Contents/MacOS/CINEMA 4D',
            '/Applications/MAXON/CINEMA 4D R%(v1)s.%(v2)s/CINEMA 4D.app/Contents/MacOS/CINEMA 4D',
        ],
        'Windows':      [
            'C:\\Program Files\\MAXON\\CINEMA 4D R%(v1)s\\CINEMA 4D 64 Bit.exe',
            'C:\\Program Files\\MAXON\\CINEMA 4D R%(v1)s.%(v2)s\\CINEMA 4D 64 Bit.exe',
            #
            'C:\\Program Files\\MAXON\\CINEMA 4D R%(v1)s\\CINEMA 4D.exe',
            'C:\\Program Files\\MAXON\\CINEMA 4D R%(v1)s.%(v2)s\\CINEMA 4D.exe',
            #
            'C:\\Program Files (x86)\\MAXON\\CINEMA 4D R%(v1)s\\CINEMA 4D.exe',
            'C:\\Program Files (x86)\\MAXON\\CINEMA 4D R%(v1)s.%(v2)s\\CINEMA 4D.exe',
        ],
    },
    'C4DCL': {
        # Since R16 MAXON renders with Commandline instead of C4D executable
        'Darwin':       [
            '/Applications/MAXON/CINEMA 4D R%(v1)s/Commandline.app/Contents/MacOS/Commandline',
            '/Applications/MAXON/CINEMA 4D R%(v1)s.%(v2)s/Commandline.app/Contents/MacOS/Commandline',
            #
            '/Applications/Maxon CINEMA 4D R%(v1)s/Commandline.app/Contents/MacOS/Commandline',
            '/Applications/Maxon CINEMA 4D R%(v1)s.%(v2)s/Commandline.app/Contents/MacOS/Commandline',
        ],
        'Windows':      [
            'C:\\Program Files\\MAXON\\CINEMA 4D R%(v1)s\\Commandline.exe',
            'C:\\Program Files\\MAXON\\CINEMA 4D R%(v1)s.%(v2)s\\Commandline.exe',
            #
            'C:\\Program Files\\Maxon CINEMA 4D R%(v1)s\\Commandline.exe',
            'C:\\Program Files\\Maxon CINEMA 4D R%(v1)s.%(v2)s\\Commandline.exe',
        ],
    },
    'NUKE': {
        # expected to have 3 values; 6.4v2 -> (6,4,2)
        'Darwin':   ['/Applications/Nuke%(v1)s.%(v2)sv%(v3)s/Nuke%(v1)s.%(v2)sv%(v3)s.app/Contents/MacOS/Nuke%(v1)s.%(v2)sv%(v3)s'],
        'Linux':    ['/usr/local/Nuke%(v1)s.%(v2)sv%(v3)s/Nuke%(v1)s.%(v2)s'],
        'Windows':  ['C:/Program Files/Nuke%(v1)s.%(v2)sv%(v3)s/Nuke%(v1)s.%(v2)s.exe'],
    },
    'MAYA': { 
        'Darwin': [
            '/Applications/Autodesk/maya%(v1)s/Maya.app/Contents/bin/Render',                   # Maya XXXX, eg. 2012
            '/Applications/Autodesk/maya%(v1)s.%(v2)s/Maya.app/Contents/bin/Render',            # Maya X.X, eg 8.5
        ],
        'Linux':        [
            '/usr/autodesk/maya%(v1)s-x64/bin/Render',
            '/usr/autodesk/maya%(v1)s/bin/Render',
        ],
        'Windows': [
            'C:/Program Files/Autodesk/Maya%(v1)s/bin/Render.exe',                              # Maya XXXX, eg. 2012
            'C:/Program Files/Autodesk/Maya%(v1)s.%(v2)s/bin/Render.exe',                       # Maya X.X, eg 8.5
            'C:/Program Files/Autodesk/Maya%(v1)s Subscription Advantage Pack/bin/Render.exe',  # Subscription Packs are always year-based
            # 32-bit
            'C:/Program Files (x86)/Autodesk/Maya%(v1)s/bin/Render.exe',
            'C:/Program Files (x86)/Autodesk/Maya%(v1)s.%(v2)s/bin/Render.exe',
            'C:/Program Files (x86)/Autodesk/Maya%(v1)s Subscription Advantage Pack/bin/Render.exe',
        ],
    },
    'XSI': {
        'Linux': [
            '/usr/Softimage/XSI_%(v1)s.%(v2)s_x64/Application/bin/xsibatch',                    # XSI 7.0
            '/usr/Softimage/Softimage_%(v1)s/Application/bin/xsibatch',                         # Softimage 2011
            '/usr/Softimage/XSI_%(v1)s.%(v2)s/Application/bin/xsibatch',                        
        ],
        'Windows': [
            'C:/Softimage/XSI_%(v1)s.%(v2)s_x64/Application/bin/XSIBatch.bat',
            'C:/Softimage/Softimage_%(v1)s_x64/Application/bin/XSIBatch.bat',
            #
            'C:/Program Files/Autodesk/Softimage %(v1)s/Application/bin/XSIBatch.bat',
            'C:/Program Files/Autodesk/Softimage %(v1)s Subscription Advantage Pack/Application/bin/XSIBatch.bat',
            #
            'C:/Program Files (x86)/Autodesk/Softimage %(v1)s/Application/bin/XSIBatch.bat',
            'C:/Program Files (x86)/Autodesk/Softimage %(v1)s Subscription Advantage Pack/Application/bin/XSIBatch.bat',
        ],
    },
    'SKETCHUP': {
        'Windows': [
            'C:/Program Files/SketchUp/SketchUp %(v1)s/SketchUp.exe',
            'C:/Program Files (x86)/SketchUp/SketchUp %(v1)s/SketchUp.exe'
        ],
        'Darwin': [
            '/Applications/SketchUp %(v1)s/SketchUp.app/Contents/MacOS/SketchUp'
        ]

    },
}


def buildAppPath(appToken, appVerTuple):
    '''
    Determine a good guess at where an app will be for a particular OS and word-size

    @param appToken: An all-caps short name for the application, must be a key in the L{installPath} dictionary.
    @type appToken: C{str} 

    @param appVerTuple: A tuple containing the application version components, the last value may be
    an optional architecture; B{x86} or B{x64} 

    @type appVerTuple: C{tuple}

    @raise AppVersionNotFoundError: Raised when the requested version of the application is not
    found in any of the paths specified in the L{installPath} dictionary. 

    @return: Return the path to the specified version and app on the local worker
    @rtype: C{str}
    '''
    appPath = ''

    if appToken in installPath:
        plat = platform.system()

        if isinstance(appVerTuple[-1], str) and appVerTuple[-1] in ['x86', 'x64']:
            plat = '%s-%s' % (plat, appVerTuple[-1])
            appVerTuple = appVerTuple[:-1]

        #==========================================================================
        # build a dict with version components like {'v1': 6, 'v2': 5, 'v3':3}
        #
        # this will be used to evaluate the formatting tokens (%(v1)s, etc) in the
        # appPathTemplate
        #==========================================================================
        appVer = {}
        for i in range(len(appVerTuple)):
            appVer['v%s' % str(i+1)] = appVerTuple[i]
        
        invalidPaths = []
        if plat in installPath[appToken]:
            for pth in installPath[appToken][plat]:
                try:
                    #================================================================
                    # evaluate the path template against the version dictionary
                    # ensuring we have enough version components in the path template
                    #================================================================
                    if '%%(v%i)s' % len(appVer) in pth:
                        appPath = pth % appVer
                        if os.path.isfile(appPath):
                            break
                        else:
                            invalidPaths.append(appPath)
                            appPath = ''
                    else:
                        continue

                except KeyError:
                    # got a path with a different number of version components than the version
                    # dictionary, expected.  eg. "CS5.5" vs "CS6"
                    continue
    else:
        logging.error('%s is not a recognized application token, the only recognized tokens are: %s' % (appToken, list(installPath.keys()).__repr__()))
        raise QubeBackEndError('unrecognized application token')

    if appPath == '':
        logging.error('Looked for application in:\n%s' % '\n'.join(['\t%s' % x for x in invalidPaths]))
        raise AppVersionNotFoundError(appToken, appVerTuple)

    appPath = '"%s"' % appPath

    return appPath


#===========================================================
# a couple of functions used by the AppVersionNotFoundError
# Exception class, but don't need to be class methods
#===========================================================
def appName(appToken):
    '''
    Return a human-readable name for an appToken, one of the keys in L{installPath}

    @param appToken: the all-caps application name token that's present in the submitted command; eg: "AE", "C4D", "MAYA"
    @type appToken: C{str}

    @return: a human-readable application name
    @rtype: C{str}
    '''
    appNameMap = {
        'AE': 'After Effects',
        'C4D': 'Cinema 4D',
        'XSI': 'XSI'
    }

    appName = appNameMap.get(appToken, appToken.capitalize())

    return appName

def appVerAsStr(appVer):
    '''
    Return an arbitrary-length tuple of integers as a dotted string 

    @param appVer: A tuple of integers
    @type appVer: {tuple}

    @return: a version number as a dotted string
    @rtype: C{str}
    '''
    return '.'.join([str(x) for x in appVer])

class AppVersionNotFoundError(QubeBackEndError):
    def __init__(self, appToken, appVer):
        self.value = '%s: Unable to locate a local installation of %s %s' % (socket.gethostname(), appName(appToken), appVerAsStr(appVer))



        
