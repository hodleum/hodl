"""
Messages:

1) requests:
  --> Without connections
  --> You know real address
  --> Low level interaction

2) message:
  --> Connection required
  --> You don't know real address

"""


import logging
from .config import *
from .models import Message


log = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO,
                        format='%(name)s.%(funcName)-20s [LINE:%(lineno)-3s]# [{}] %(levelname)-8s [%(asctime)s]'
                               '  %(message)s'.format('<Bob>'))
