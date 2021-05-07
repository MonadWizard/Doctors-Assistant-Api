"""For production we'll automatically generate settings from prod.py via ci/cd script"""

DEV = True

if DEV:
    from .local import *
else:
    from .prod import *