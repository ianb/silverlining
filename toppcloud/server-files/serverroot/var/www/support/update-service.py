#!/usr/bin/env python
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tcsupport.common import services_config, load_service_module

def update_service(app_dir):
    for name, config in sorted(services_config(app_dir).items()):
        mod = load_service_module(name)
        mod.install(app_dir, config)

if __name__ == '__main__':
    import sys
    app_dir = sys.argv[1]
    update_service(app_dir)
