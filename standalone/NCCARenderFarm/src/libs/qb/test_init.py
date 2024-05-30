#!/usr/bin/env python
"""
Qube Python API Module Tests

These are the unit and functional tests used to validate the qb python module.

:Note: They are written to be used with "nose" unit testing (http://www.somethingaboutorange.com/mrl/projects/nose/)
       Usage is "nosetests -v 3 <this file>" to run the tests for this file.
       Nose can also work on entire recursed directories.

:Note: This documentation is formatted for use with `epydoc <http://epydoc.sourceforge.net>`__
       using reStructuredText as the format.
       See `epydoc alternate markup languages <http://epydoc.sourceforge.net/manual-othermarkup.html#restructuredtext>`__
       and `Quick reStructuredText <http://docutils.sourceforge.net/docs/user/rst/quickref.html>`__ for more information on the structure and format.

:Copyright: PipelineFX.  All rights reserved.  
"""
__docformat__ = "restructuredtext en"


# ===================================================
# Imports
#   The imports should be kept to a minimum
# ===================================================
# Note: import __init__ directly to make sure using the local version of the module
from . import __init__ as qb

# ===================================================
# Binary Sort Testing
# ===================================================
def test_binarySort_order1():
    """Check sort order"""
    origList = list(range(1,21))
    sortedList = qb.binarySort(origList)
    assert(sortedList == [1, 20, 10, 5, 15, 3, 7, 12, 17, 2, 4, 6, 8, 11, 13, 16, 18, 9, 14, 19])
    return (origList, sortedList)

def test_binarySort_order2():
    """Check sort order if < 2 items"""
    # 2 items
    sortedList = qb.binarySort([1,2])
    assert(sortedList == [1,2])
    # 1 item
    sortedList = qb.binarySort([1])
    assert(sortedList == [1])
    # 0 items
    sortedList = qb.binarySort([])
    assert(sortedList == [])

def test_binarySort_newlist1():
    """Verify not overwriting original list"""
    origList = list(range(1,21))
    qb.binarySort(origList)
    assert(origList == list(range(1,21)))  # confirm not overwriting original list

def test_binarySort_newlist2():
    """Verify not overwriting original list if < 2 items"""
    origList = [1,2]
    qb.binarySort(origList)
    assert(origList == [1,2])  # confirm not overwriting original list

if __name__ == '__main__':
    print("Using qb python module", qb)

    print("Testing Binary Sorting")
    print(test_binarySort_order1())
    test_binarySort_order2()
    test_binarySort_newlist1()
    test_binarySort_newlist2()