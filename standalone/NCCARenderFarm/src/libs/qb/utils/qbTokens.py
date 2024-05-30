'''
   QB_* token regular expressions and functions
'''

#=======================================
#  $Revision: #1 $
#  $Change: 22715 $
#=======================================

import re
import qb


# only compile the cmdrange regex objects once
QB_FRAME_TOKEN_RGX = [
    re.compile('QB_FRAME_NUMBER'),
    re.compile('QB_FRAME_START'),
    re.compile('QB_FRAME_END'),
    re.compile('QB_FRAME_STEP'),
    re.compile('QB_FRAME_RANGE'),
]

def evaluateQBTokens(cmd, fRange, padding=1):
    '''
    Replace all QB_* tokens with the appropriate values from the object's frame range or job stage

    fRange is either the job's frame range value, or the agenda item's specific frame range

    @return: Both the cmd with all QB_FRAME* tokens evaluted, and a dictionary of all tokens and their values.

    @rtype: C{tuple}
    '''
    padding = int(padding)
    fStep = 1
    
    if not re.search('[-,]', fRange):
        # find the trivial single-frame case, with neither a '-' nor a ','
        fEnd = fStart = fRange

    elif fRange.count('-') and not fRange.count(','):
        if not fRange.startswith('-'):
            # most common case, simple frame range beginning with a positive number
            (fStart, fEnd) = fRange.split('-', 1)
        elif fRange.count('-') == 1:
            # a single negative number
            fStart = fEnd = fRange
        else:
            # rare, a frame range whose start is a negative number
            m = re.search('(-\d+)-(-?\d+.*)', fRange)
            (fStart, fEnd) = m.groups()

        if fEnd.count('x'):
            (fEnd, fStep) = fEnd.split('x')
    else:
        # a disjointed frame range containing a comma
        fList = qb.rangesplit(fRange)
        fStart = fList[0]
        fEnd = fList[-1]

    tokens = {}
    tokens['QB_FRAME_START'] = tokens['QB_FRAME_NUMBER'] = str('%0*d' % (padding, int(fStart)))
    tokens['QB_FRAME_END'] = str('%0*d' % (padding, int(fEnd)))
    tokens['QB_FRAME_STEP'] = str(fStep)
    tokens['QB_FRAME_RANGE'] = fRange

    for rgx in QB_FRAME_TOKEN_RGX:
        cmd = rgx.sub(tokens[rgx.pattern], cmd)

    return (cmd, tokens)


