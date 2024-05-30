

class QubeUtilityGeneralError(Exception):
    '''
    An exception class used to indicate an error condition not handled by the qb.utils package.
    '''
    def __init__(self, value):
        '''
        @param value: an error message
        @type value: C{str}
        '''
        self.value = value

    def __str__(self):
        '''
        @return: The string representation of the error message that was passed when raising this exception
        @rtype: C{str}
        '''
        return repr(self.value)

