from UmlTestCore.Configure.ConfigInteraction import read_config, interactor, fisrt_time

import sys

if __name__ == "__main__":
    # Handle the config
    config = read_config()
    if config is None:
        fisrt_time()
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == 'config':
        interactor()
        sys.exit(0)
    java_path = config["Java-Path"]
    jar_path = config["Jar-Path"]

