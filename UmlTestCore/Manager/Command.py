class CommandInfo:
    def __init__(self, command: str, output: str) -> None:
        self.input: str = command
        self.output: str = output
    
    def __str__(self) -> str:
        return f"{{<stdout>: {self.output}, <stdin>: {self.input}}}"
