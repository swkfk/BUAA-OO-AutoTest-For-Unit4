from .ConfigFs import write_config, read_config
from .Defaults import *

import sys

def interactor():
    config = read_config()
    if config is None:
        print("Cannot read the config! Abort")
        sys.exit(1)
    print("Configs are as follows:")
    for i, (k, v) in enumerate(config.items()):
        print(f"  {i+1}> {k} = {v}")
    print("Enter the number to modify the config, 0 to exit")
    while True:
        try:
            index = input("> ")
        except EOFError:
            print("Bye~")
            break
        try:
            index = int(index)
            if index == 0:
                print("Bye~")
                break
            key = list(config.keys())[index - 1]
        except ValueError:
            print("Invalid number, try again!")
            continue
        except IndexError:
            print("Number our of range, try again!")
        try:
            v = input(f"New value for '{key}': ")
            yn = input(f"Are you sure to apply '{key}={v}'? [y/n] ")
        except EOFError:
            print("Config file untouched\nBye~")
            break
        if yn == 'y':
            config[key] = v
            write_config(config)
            print("Applied!")
        else:
            print("Discard!")

def gen_default_config():
    write_config(DEFAULT_CONFIG)

def fisrt_time():
    print("Generate Config File...")
    gen_default_config()
    print(f"<< You can run as 'python {sys.argv[0]} config' to amend the config! >>")
    print()
    interactor()
