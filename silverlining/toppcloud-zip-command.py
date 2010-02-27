#!/usr/bin/env python
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(here, 'lib'))

for path in list(sys.path):
    if os.path.abspath(path) == here and path in sys.path:
        sys.path.remove(path)

from toppcloud.runner import main

if __name__ == '__main__':
    main()
