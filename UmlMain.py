from UmlTestCore.Configure.ConfigInteraction import read_config, interactor, fisrt_time
from UmlTestCore.Runner.Communicator import runner_core
from UmlTestCore.Core import Core

import sys
import shutil
import time
from pathlib import Path

def main():
    Path("TestCases/").mkdir(exist_ok=True)

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

    test_num_s = input("Test Count, 0 for endless tests.\n> ")
    if not test_num_s.isnumeric():
        print("Invalid.")
        sys.exit(3)
    test_num = int(test_num_s)
    if test_num < 0:
        print("Invalid.")
        sys.exit(3)
    if test_num == 0:
        print("Launch end-less tests")

    i = 1
    wa = 0
    while i <= test_num or test_num == 0:
        print(f"#({i}/{str(test_num) if test_num > 0 else 'endless'}) WA: {wa} cases\n...", end='')
        sys.stdin.flush()
        core = Core(config)
        ret = runner_core([java_path, '-jar', jar_path], core.command_callback, core.gen_init_command(), 'TestCases/%%.txt')
        print(ret)
        if ret != "Ok":
            dump_core = core.library.core_dump()
            time_s = time.strftime('%m-%d-%H-%M-%S', time.localtime())
            wa += 1
            shutil.copy('TestCases/input.txt', f'TestCases/{time_s}.in.txt')
            shutil.copy('TestCases/output.txt', f'TestCases/{time_s}.out.txt')
            Path(f'TestCases/{time_s}.dump.txt').write_text(dump_core)
            Path(f'TestCases/{time_s}.check.txt').write_text(ret)
            time.sleep(1)
        i += 1

    if wa == 0:
        print("All Accepted!")
    else:
        print(f"Wa {wa} cases")

try:
    main()
except KeyboardInterrupt:
    print("\n\nYou are going to terminate me now?")
    print("Farewell!")
