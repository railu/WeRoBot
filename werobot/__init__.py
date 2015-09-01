__version__ = '0.6.1'
__author__ = 'whtsky'
__license__ = 'MIT'

__all__ = ["WeRoBotBiz"]

try:
    from werobot.robot import WeRoBotBiz
except ImportError:
    pass
