import sys
import os
from silversupport.appconfig import AppConfig

def main():
    app_dir, config = sys.argv[1:]
    app = AppConfig(os.path.join(app_dir, 'app.ini'))
    app.activate_path()
    app.check_config(config)

if __name__ == '__main__':
    main()
