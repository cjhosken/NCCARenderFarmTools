#======================================
#  $Revision: #1 $
#  $Change: 22715 $
#======================================
import sys

import qb.backend.logParser
import qb.backend.utils as backendUtils

class AERenderLogParser(qb.backend.logParser.LogParser):
    '''
    This LogParser class is for AfterEffects sequence renders.
    '''
    def calcProgress(self, progressMatchStr, qbTokens):
        '''
        Calculate the internal progress of an AfterEffects sequence render.

        AfterEffects progress output does not include the frame number, but rather the 1-based index
        of the frame in the chunk.

        eg: if rendering a 5 frame chunk from frames 6-10, the output will contain:
            
            PROGRESS:  0:00:09:05 (1): 0 Seconds
            PROGRESS:  0:00:09:05 (2): 0 Seconds
            PROGRESS:  0:00:09:05 (3): 0 Seconds
            PROGRESS:  0:00:09:05 (4): 0 Seconds
            PROGRESS:  0:00:09:05 (5): 0 Seconds

        So this method finds the AE frame number (1-5 in this case), then determines how many frames
        are in the chunk, and then calculates the completion value for the chunk. 

        @param progressMatchStr: the value used to derive the progress within the chunk.  It is
        simply the progress percentage integer matched in the application output.

        @type progressMatchStr: C{str}

        @param qbTokens: a dictionary containing all the QB_FRAME* values to aid in calculation the
        in-chunk progress.

        @type qbTokens: C{dict}

        @return: The amount of work complete for the item, expressed as a float between 0 and 1.0, 1.0 being completely done.
        @rtype: C{float}
        '''
        progress = 0.0
        chunkLen = len(qb.genframes(qbTokens['QB_FRAME_RANGE']))

        try:
            progress = '%0.2f' % (float(progressMatchStr) / chunkLen,)
        except ValueError:
            backendUtils.flushPrint('WARNING: the logParser %s did not extract a valid frame number: "%s"' % (self.__class__.__name__, progressMatchStr), fhList=sys.stderr)
            backendUtils.flushPrint(backendUtils.formatExc(), fhList=[sys.stderr])

        return progress


