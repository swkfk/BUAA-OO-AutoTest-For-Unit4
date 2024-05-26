from UmlTestCore.Configure.ConfigInteraction import read_config, interactor, fisrt_time
from UmlTestCore.Runner.Communicator import runner_core
from UmlTestCore.Core import Core

import sys
from pathlib import Path


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

    if not Path(jar_path).exists():
        print(f"Cannit find the Jar: {jar_path}")
        sys.exit(2)

    core = Core(config)
    ret = runner_core([java_path, '-jar', jar_path], core.command_callback, core.gen_init_command(), '%%.txt')
    print(ret)
