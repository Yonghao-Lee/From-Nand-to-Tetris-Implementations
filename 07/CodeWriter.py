import typing
import os

class CodeWriter:
    """Translates VM commands into Hack assembly code for the Hack computer."""

    # ────────────────── initialisation ──────────────────
    def __init__(self, output_stream: typing.TextIO) -> None:
        self.output: typing.TextIO = output_stream
        self.label_counter: int = 0        # for generating unique labels
        self.current_vm_filename: str = "" # current .vm file being translated
        # Project 8 bookkeeping (ignored by Project 7)
        self.current_function_name: str = ""
        self.call_counter: int = 0

    # ────────────────── low‑level helpers ──────────────────
    def _write_comment(self, text: str) -> None:
        self.output.write(f"// {text}\n")

    def _write_lines(self, lines: list[str]) -> None:
        """Write several assembly lines at once."""
        for line in lines:
            self.output.write(line + "\n")

    # stack‑pointer helpers
    def _increment_sp(self) -> None:
        self._write_lines(["@SP", "M=M+1"])

    def _decrement_sp(self) -> None:
        self._write_lines(["@SP", "M=M-1"])

    # push / pop helpers
    def _push_D_to_stack(self) -> None:
        self._write_lines([
            "@SP", "A=M", "M=D"
        ])
        self._increment_sp()

    def _pop_stack_to_D(self) -> None:
        self._decrement_sp()
        self._write_lines(["A=M", "D=M"])

    # file‑scope helpers
    def set_file_name(self, filename: str) -> None:
        """Called once for every .vm file to reset bookkeeping."""
        self.current_vm_filename = os.path.splitext(os.path.basename(filename))[0]
        self.current_function_name = ""
        self.call_counter = 0
        
    def close(self):
        self._write_comment("Infinite loop at end")
        self._write_lines(["(END)", "@END", "0;JMP"])
        self.output.close()    

    # ────────────────── arithmetic / logical commands ──────────────────
    def write_arithmetic(self, command: str) -> None:
        self._write_comment(f"Arithmetic: {command}")

        # binary ops
        if command in ("add", "sub", "and", "or"):
            self._pop_stack_to_D()   # y
            self._decrement_sp()     # x
            op = {"add": "+", "sub": "-", "and": "&", "or": "|"}[command]
            self._write_lines(["A=M", f"M=M{op}D"])
            self._increment_sp()
            return

        # unary ops
        if command in ("neg", "not"):
            op = {"neg": "-", "not": "!"}[command]
            self._write_lines(["@SP", "A=M-1", f"M={op}M"])
            return

        # comparisons
        if command in ("eq", "gt", "lt"):
            self._pop_stack_to_D()   # y
            self._decrement_sp()     # x
            self._write_lines(["A=M", "D=M-D"])
            true_lbl = f"{command.upper()}_TRUE_{self.label_counter}"
            end_lbl  = f"{command.upper()}_END_{self.label_counter}"
            jump = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}[command]
            self.label_counter += 1
            self._write_lines([
                f"@{true_lbl}", f"D;{jump}",
                "@SP", "A=M", "M=0",
                f"@{end_lbl}", "0;JMP",
                f"({true_lbl})",
                "@SP", "A=M", "M=-1",
                f"({end_lbl})"
            ])
            self._increment_sp()
            return

        # shift left (*2)
        if command == "shiftleft":
            self._write_comment("shiftleft (*2)")
            self._write_lines(["@SP", "A=M-1", "D=M", "M=D+M"])
            return

        # arithmetic shift right (/2)
        if command == "shiftright":
            lbl = self.label_counter
            self.label_counter += 1
            self._write_comment("shiftright (/2, arithmetic)")
            self._write_lines([
                # load operand
                "@SP", "A=M-1", "D=M",
                # flag sign
                "@R15", "M=0",
                f"@SHR_POS_{lbl}", "D;JGE",
                "@R15", "M=-1", "D=-D",
                f"(SHR_POS_{lbl})",
                # set dividend & quotient
                "@R13", "M=0",      # quotient
                "@R14", "M=D",      # dividend
                f"(SHR_LOOP_{lbl})",
                "@R14", "D=M", "@2", "D=D-A",
                f"@SHR_DONE_{lbl}", "D;JLT",
                "@2", "D=A", "@R14", "M=M-D",  # dividend -= 2
                "@R13", "M=M+1",                     # quotient++
                f"@SHR_LOOP_{lbl}", "0;JMP",
                f"(SHR_DONE_{lbl})",
                # apply sign
                "@R15", "D=M",
                f"@SHR_APPLY_{lbl}", "D;JNE",
                "@R13", "D=M",
                f"@SHR_END_{lbl}", "0;JMP",
                f"(SHR_APPLY_{lbl})",
                "@R13", "D=M", "D=-D",
                f"(SHR_END_{lbl})",
                "@SP", "A=M-1", "M=D"
            ])
            return

        raise ValueError(f"Unknown arithmetic command: {command}")

    # ────────────────── push / pop commands ──────────────────
    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        self._write_comment(f"{'push' if command == 'C_PUSH' else 'pop'} {segment} {index}")
        seg = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}

        if command == "C_PUSH":
            if segment == "constant":
                self._write_lines([f"@{index}", "D=A"])
                self._push_D_to_stack()
                return
            if segment in seg:
                base = seg[segment]
                self._write_lines([
                    f"@{index}", "D=A", f"@{base}", "A=M+D", "D=M"
                ])
                self._push_D_to_stack()
                return
            if segment == "temp":
                if not 0 <= index <= 7:
                    raise ValueError("Temp index out of bounds (0‑7)")
                self._write_lines([f"@{5+index}", "D=M"])
                self._push_D_to_stack()
                return
            if segment == "pointer":
                if index not in (0, 1):
                    raise ValueError("Pointer index must be 0 or 1")
                self._write_lines([f"@{3+index}", "D=M"])
                self._push_D_to_stack()
                return
            if segment == "static":
                var = f"{self.current_vm_filename}.{index}"
                self._write_lines([f"@{var}", "D=M"])
                self._push_D_to_stack()
                return
            raise ValueError(f"Unknown PUSH segment: {segment}")

        if command == "C_POP":
            if segment == "constant":
                raise ValueError("Cannot pop to constant segment")
            if segment in seg:
                base = seg[segment]
                self._write_lines([
                    f"@{index}", "D=A", f"@{base}", "D=M+D", "@R13", "M=D"
                ])
                self._pop_stack_to_D()
                self._write_lines(["@R13", "A=M", "M=D"])
                return
            if segment == "temp":
                if not 0 <= index <= 7:
                    raise ValueError("Temp index out of bounds (0‑7)")
                self._pop_stack_to_D()
                self._write_lines([f"@{5+index}", "M=D"])
                return
            if segment == "pointer":
                if index not in (0, 1):
                    raise ValueError("Pointer index must be 0 or 1")
                self._pop_stack_to_D()
                self._write_lines([f"@{3+index}", "M=D"])
                return
            if segment == "static":
                var = f"{self.current_vm_filename}.{index}"
                self._pop_stack_to_D()
                self._write_lines([f"@{var}", "M=D"])
                return
            raise ValueError(f"Unknown POP segment: {segment}")

        raise ValueError("Invalid push/pop command type")