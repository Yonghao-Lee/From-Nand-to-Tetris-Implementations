import typing

class Parser:
    # Define constants as class attributes
    C_ARITHMETIC = 'C_ARITHMETIC'
    C_PUSH       = 'C_PUSH'
    C_POP        = 'C_POP'
    C_LABEL      = 'C_LABEL'
    C_GOTO       = 'C_GOTO'
    C_IF         = 'C_IF'
    C_FUNCTION   = 'C_FUNCTION'
    C_RETURN     = 'C_RETURN'
    C_CALL       = 'C_CALL'

    # Define commands as class attribute
    ARITHMETIC_COMMANDS = {
        'add', 'sub', 'neg',
        'eq', 'gt', 'lt',
        'and', 'or', 'not',
        'shiftleft', 'shiftright'
    }

    def __init__(self, input_stream: typing.TextIO) -> None:
        # strip out comments/blank lines up front
        raw = input_stream.readlines()
        self.lines = []
        for line in raw:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            self.lines.append(line.split('//')[0].strip())
        self.current_command = ''
        self.index = -1

    def has_more_commands(self) -> bool:
        return self.index + 1 < len(self.lines)

    def advance(self) -> None:
        self.index += 1
        self.current_command = self.lines[self.index]

    def command_type(self) -> str:
        cmd = self.current_command.split()[0]
        if cmd in self.ARITHMETIC_COMMANDS:  # Use self.ARITHMETIC_COMMANDS
            return self.C_ARITHMETIC  # Use self.C_ARITHMETIC
        elif cmd == 'push':
            return self.C_PUSH  # Use self.C_PUSH
        elif cmd == 'pop':
            return self.C_POP  # Use self.C_POP
        # ... and so on with all the other command types
        # ...
        else:
            raise ValueError(f"Unknown command type: {cmd}")

    def arg1(self) -> str:
        t = self.command_type()
        if t == self.C_ARITHMETIC:  # Use self.C_ARITHMETIC
            return self.current_command.split()[0]
        return self.current_command.split()[1]

    def arg2(self) -> int:
        return int(self.current_command.split()[2])