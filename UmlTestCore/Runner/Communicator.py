import subprocess
from typing import List
from enum import Enum

from ..Exceptions.BadBehaviorException import BadBehavior
from ..Exceptions.UnexpectedException import Unexpected

class Action(Enum):
    SendText = 1
    Continue = 2
    Terminate = 3


class Reaction:
    def __init__(self, action: Action, msg: str = "") -> None:
        self.action: Action = action
        self.msg: str = msg


def runner_core(args: List[str], callback, init_input: List[str], store_pattern: str):
    process = subprocess.Popen(
        args=args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdin = process.stdin
    stdout = process.stdout

    if stdin is None or stdout is None:
        return "Fail To Start!"

    fin = open(store_pattern.replace("%%", "input"), 'w', encoding="utf-8")
    fout = open(store_pattern.replace("%%", "output"), 'w', encoding="utf-8")

    for command in init_input:
        command += '\n'
        fin.write(command)
        stdin.write(command)
    stdin.flush()

    while True:
        output = stdout.readline().removesuffix('\n')
        fout.write(output + '\n')
        fout.flush()
        try:
            reaction: Reaction = callback(output)
        except AssertionError as e:
            return f"Output Syntax Error: {e}"
        except BadBehavior as e:
            return f"Wrong Behavior: {e}"
        except Unexpected as e:
            return f"Unexpected Situation: {e}"
        except Exception as e:
            return f"Rare Behavior: {e}"
        if reaction.action == Action.Continue:
            continue
        if reaction.action == Action.Terminate:
            break
        if reaction.action == Action.SendText:
            fin.write(reaction.msg + '\n')
            fin.flush()
            stdin.write(reaction.msg + '\n')
            stdin.flush()

    fin.close()
    fout.close()
    stdin.close()
    process.kill()

    return "Ok"
