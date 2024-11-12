
from .hexpos import HexPos

try:
    from .cyhexpos import CyHexPos
except ImportError:
    pass

#try: # if CyHexPos was not compiled, use HexPos as HexPos
#    from .cyhexposition import CyHexPos
#    from .cyhexposition import CyHexPos as HexPos
#except ModuleNotFoundError:
#    pass
    