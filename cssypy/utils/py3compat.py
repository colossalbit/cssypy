import sys

if sys.version_info[0] <= 2:
    range = xrange  # permits using  for x in range()
    uchr = unichr
    PYTHON3 = False
else:
    uchr = chr
    PYTHON3 = True

# from http://docs.python.org/py3k/howto/pyporting.html
class UnicodeMixin(object):
    """Mixin class to handle defining the proper __str__/__unicode__
       methods in Python 2 or 3."""

    if sys.version_info[0] >= 3:
        def __str__(self):
            return self.__unicode__()
    else:
        def __str__(self):
            return self.__unicode__().encode('utf8')



