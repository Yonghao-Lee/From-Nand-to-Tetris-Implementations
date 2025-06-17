import typing


class VMWriter:
    """Writes VM commands into a file. Encapsulates the VM command syntax."""

    # Segment name mapping: aliases → canonical VM segment keywords
    _SEGMENT_MAP = {
        "CONST": "constant",
        "CONSTANT": "constant",
        "ARG": "argument",
        "ARGUMENT": "argument",
        "LOCAL": "local",
        "VAR": "local",       # CompilationEngine may emit "VAR"
        "STATIC": "static",
        "FIELD": "this",      # fields live in the "this" segment
        "THIS": "this",
        "THAT": "that",
        "POINTER": "pointer",
        "TEMP": "temp",
    }

    @staticmethod
    def _vm_segment(seg: str) -> str:
        """Return legal VM segment keyword for seg. Raises KeyError if unrecognized."""
        return VMWriter._SEGMENT_MAP[seg.upper()]

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Create a new VMWriter with given output stream."""
        self.output_stream: typing.TextIO = output_stream

    # Memory access commands
    def write_push(self, segment: str, index: int) -> None:
        """Write VM push command."""
        self.output_stream.write(f"push {self._vm_segment(segment)} {index}\n")

    def write_pop(self, segment: str, index: int) -> None:
        """Write VM pop command."""
        self.output_stream.write(f"pop {self._vm_segment(segment)} {index}\n")

    # Arithmetic/logical commands
    def write_arithmetic(self, command: str) -> None:
        """Write VM arithmetic command (add, neg, eq, etc.)."""
        self.output_stream.write(f"{command.lower()}\n")

    # Program flow commands
    def write_label(self, label: str) -> None:
        """Write VM label command."""
        self.output_stream.write(f"label {label}\n")

    def write_goto(self, label: str) -> None:
        """Write VM goto command."""
        self.output_stream.write(f"goto {label}\n")

    def write_if(self, label: str) -> None:
        """Write VM if-goto command."""
        self.output_stream.write(f"if-goto {label}\n")

    # Function calling commands
    def write_call(self, name: str, n_args: int) -> None:
        """Write VM call command."""
        self.output_stream.write(f"call {name} {n_args}\n")

    def write_function(self, name: str, n_locals: int) -> None:
        """Write VM function command."""
        self.output_stream.write(f"function {name} {n_locals}\n")

    def write_return(self) -> None:
        """Write VM return command."""
        self.output_stream.write("return\n")
