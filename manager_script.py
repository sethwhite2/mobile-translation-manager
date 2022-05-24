import getopt
import sys

from manager import init, save, deploy, sync

# todo: add verbose option to log output or action
# todo: implement tqdm for progress


def main(argv):
    help_message =  """
usage: manager.py [-h] -c <path to config file> [init, -s, --save, -d]

optional arguments:
        init\t\tcreate a strings index file based on the current project files
        -h, --help\t\tshow this help message and exit
        -c, --config\t\tpath to config file
        -s, --sync\t\sync the values in index file with google sheet and project files
        -d, --update\t\tdeploy index file to google sheet
        --save\t\tsave values from index file into the project files
    """
    try:
        opts, args = getopt.getopt(argv, "hc:d", ["init", "sync", "save"])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    config_path = None
    should_init = False
    should_save = False
    should_deploy = False
    should_sync = False
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(help_message)
            sys.exit()
        elif opt in ("-c", "--config"):
            config_path = arg
        elif opt in ("--save"):
            should_save = True
        elif opt in ("-d", "--deploy"):
            should_deploy = True
        elif opt in ("--sync"):
            should_sync = True
        elif opt in ("--init"):
            should_init = True
    
    if not config_path:
        print(help_message)
        sys.exit(2)

    if should_init:
        init(config_path)
        return
    if should_sync:
        sync(config_path)
    if should_save:
        save(config_path)
    if should_deploy:
        deploy(config_path)


if __name__ == '__main__':
    main(sys.argv[1:])
    exit(0)
