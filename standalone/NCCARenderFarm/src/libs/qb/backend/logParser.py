"""
Implement a grep-like mechanism to extract information out of the log files.
"""
#======================================
#  $Revision: #1 $
#  $Change: 22715 $
#  $File: //depot/rel-7.5/qube/src/api/python/qb/backend/logParser.py $
#======================================

import sys
import re
import logging

import qb
import qb.backend.utils as backendUtils

RGX_QUBE_RETRY_MSG = re.compile('qube! - retry/requeue|work\[.*auto-retry\[')
RGX_QUBE_PREEMPT_MSG = re.compile('preempt order received - job should exit')


class LogParser(object):
    """
    The base class for log parsers in Qube, it provides all the functionality needed with the
    exception of calculating in-frame progress.

    Since calculating in-frame progress requires interpreting the extracted string from the logs,
    derived methods should override this class' calcProgress() method.  See the docstring for this
    class' calcProgress()
    """
    def __init__(self, job):
        """
        @type job: qb.Job
        """
        self.logging = logging.getLogger('%s' % self.__class__.__name__)

        self.regex = {}

        self.dev = backendUtils.getDevBoolean(job)
        if self.dev:
            self.logging.warning('Running in "dev" mode, all log matches are skipped.')

        # these regex's are actually just looking for a match, not trying to extract a sub-string,
        # so we'll push the entire matched string into the "matches" dictionary in self.parse()
        rgxMatchesEntireString = ['regex_highlights', 'regex_errors']

        # put all the job's regex's into a dict keyed by the job regex's name
        for jobRegex in [x for x in job.get('package', {}) if x.startswith('regex') and isinstance(job['package'][x], str)]:
            
            # handle multi-line regex patterns from the GUI
            patterns = []
            for pattern in [x.strip() for x in job['package'][jobRegex].splitlines()]:
                # catch empty lines in the regex_* boxes in the GUI
                if len(pattern):
                    patterns.append(pattern)

            rgxPattern = '|'.join(patterns)

            # tweak the rgx pattern if we're simply looking for a match and not extracting a substring
            if jobRegex in rgxMatchesEntireString:
                rgxPattern = '(%s)' % rgxPattern

            self.regex[jobRegex] = re.compile(rgxPattern, re.MULTILINE | re.IGNORECASE)

    def parse(self, data, qbTokens=None):
        """
        Scan the log stream for matches to the job's various regexes.

        Return a dict of lists, key is the regex name as specificied in the job package with the
        leading 'regex_' stripped, the list is all matches for the regex.  Only return non-empty
        lists.

        @type data: str

        @param qbTokens: a dictionary containing all the QB_FRAME* values to aid in calculation the
        in-chunk progress.

        @type qbTokens: C{dict}

        @rtype: dict of lists
        """
        matches = {}
        
        # toss everything that precedes a 'retry/requeue' match
        # it's from a previous run of this instance, don't bother matching it again
        if RGX_QUBE_RETRY_MSG.search(data):
            self.logging.debug('Log parsing skipping sections that precede a "retry"')
            self.logging.debug('BEFORE: data length: %s' % len(data))

            data = RGX_QUBE_RETRY_MSG.split(data)[-1]

            self.logging.debug('AFTER: data length: %s' % len(data))

        if RGX_QUBE_PREEMPT_MSG.search(data):
            self.logging.debug('Log parsing skipping sections that precede a "preemption"')
            self.logging.debug('BEFORE: data length: %s' % len(data))
    
            data = RGX_QUBE_PREEMPT_MSG.split(data)[-1]
    
            self.logging.debug('AFTER: data length: %s' % len(data))

        for jobRegex in list(self.regex.keys()):
            rgxName = jobRegex.replace('regex_', '')
            matches[rgxName] = []

        # find all the matches for each regex
        for (rgxName, rgx) in list(self.regex.items()):
            # trim the leading 'regex_' from the name, maintains b-ward compatibility with the
            # original resultpackage keys
            rgxName = rgxName.replace('regex_', '')

            self.logging.debug('rgx name:%s  pattern: %s' % (rgxName, rgx.pattern))

            for m in rgx.finditer(data):
                if m.groups():
                    for grp in m.groups():
                        if grp is not None and len(grp) > 0 and not self.dev:
                            matches[rgxName].append(grp)

        self.logging.debug('Regex matches: %s' % matches)

        # cull the empty lists
        for rgxName in list(matches.keys()):
            if len(matches[rgxName]) == 0:
                del matches[rgxName]
            elif rgxName == 'outputPaths':
                # outputPaths is unique in the resultpackage, as it's a comma-delimited string, not a list.
                matches[rgxName] = ','.join(matches[rgxName])

        # the 'progress' only uses the last match, and it is necessary to compute the amount of
        # the work that is done when the work is in a chunk or partition.
        if 'progress' in matches:
            if qbTokens:
                matches['progress'] = self.calcProgress(matches['progress'][-1], qbTokens)
            else:
                matches['progress'] = self.calcProgress(matches['progress'][-1])

        return matches
    
    def calcProgress(self, progressMatchStr, *args):
        """
        Calculate the internal progress of a piece of work (or a cmdline job) and return it as
        a float between 0 and 1.  
        
        The extraction of the progress value via the job's "progress" regular expression is only the
        first aspect of determining how close a particular chunk is to completing; the other part is
        figuring out what to do with the frame or the "% complete" string that's been pulled out of
        the log stream and converting it into the expected numerical range so that the QubeGUI knows
        what to do with it.

        2-digit precision is preferred, more precision will be truncated in the QubeGUI.

        It is expected that this method be overridden for any log parser that is expected to
        calculate a "done" value from the log contents.

        @param progressMatchStr: the value used to derive the progress within the chunk.  It is
        simply the progress percentage integer matched in the application output.

        @type progressMatchStr: C{str}

        @return: The amount of work complete for the item, expressed as a float between 0 and 1.0, 1.0 being completely done.
        @rtype: C{float}
        """
        pass


class ProgressPercentageLogParser(LogParser):
    """
    This LogParser class on of calcProgress() is for the most trivial case: 
            
            A render returns a "% complete" string between 1 and 100.  The portion of the string
            containing the integer is passed to calcProgress as the progressMatchStr.

    This class converts that percentage value to a float between 0 and 1 and returns that float.
    """
    def calcProgress(self, progressMatchStr, *args):
        """
        Calculate the internal progress of a piece of work (or a cmdline job) and return it as
        a float between 0 and 1.  
        
        eg: A progressMatchStr of "23" is converted to 0.23.

        @param progressMatchStr: the value used to derive the progress within the chunk.  It is
        simply the progress percentage integer matched in the application output.

        @type progressMatchStr: C{str}

        @return: The amount of work complete for the item, expressed as a float between 0 and 1.0, 1.0 being completely done.
        @rtype: C{float}
        """
        progress = 0.0
        try:
            progress = '%0.2f' % (float(progressMatchStr) / 100,)
            self.logging.debug('progress = %s' % progress)
        except:
            backendUtils.flushPrint('WARNING: the logParser %s did not extract a progress % value: "%s"' % (self.__class__.__name__, progressMatchStr), fhList=sys.stderr)
            backendUtils.flushPrint(backendUtils.formatExc(), fhList=[sys.stderr])

        return progress


class CmdRangeChunkLogParser(LogParser):
    """
    This LogParser class is expected to be used for jobs whose agenda contains frame chunks or
    partitions.  It returns the value of currentFrame/chunkLength as a float between 0 and 1.
    """
    def calcProgress(self, progressMatchStr, qbTokens):
        """
        Calculate the internal progress of a frame chunk or partition.

        This particular example expects to have only a frame number in the progressMatchStr, and
        compare it to the frame range for the individual work item that was passed to the parse()
        method. 
    
        Determine the extent to which the chunk has progressed by determining the index of the current
        frame (QB_FRAME_NUMBER) in a list comprised of all frames for the chunk, then comparing that
        index against the size of the chunk.

        eg: progressMatchStr = "23", and the frame range for this piece of work (as determined from
        the qbTokens dict) is 21-30.  So the index for this frame would be 3, and 3/10 = 0.3

        @param progressMatchStr: the value used to derive the progress within the chunk.  It is
        simply the progress percentage integer matched in the application output.

        @type progressMatchStr: C{str}

        @param qbTokens: a dictionary containing all the QB_FRAME* values to aid in calculation the
        in-chunk progress.

        @type qbTokens: C{dict}

        @return: The amount of work complete for the item, expressed as a float between 0 and 1.0,
        1.0 being completely done.

        @rtype: C{float}
        """
        progress = 0.0

        try:
            chunkFrames = [ x['name'] for x in qb.genframes( qbTokens['QB_FRAME_RANGE']) ]
            idx = chunkFrames.index(progressMatchStr) + 1
            progress = float(idx) / len(chunkFrames)
            progress = '%0.2f' % progress
        except ValueError:
            backendUtils.flushPrint('WARNING: the logParser %s did not extract a valid frame number: "%s"' % (self.__class__.__name__, progressMatchStr), fhList=sys.stderr)
            backendUtils.flushPrint('WARNING: Traceback from error:', fhList=[sys.stderr])
            backendUtils.flushPrint(backendUtils.formatExc(), fhList=[sys.stderr])

        return progress
    

