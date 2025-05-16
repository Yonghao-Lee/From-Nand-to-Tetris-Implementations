"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_stream = output_stream
        self.current_file = ""
        self.label_counter = 0
        self.current_function = ""
        self.return_counter = 0
        
    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.current_file = filename
        self.current_function = ""  # Reset function context when changing files
        
    def write_init(self) -> None:
        """Writes the assembly code that effects the bootstrap code that
        initializes the VM. This code must be placed at the beginning of the 
        output file.
        """
        # Initialize SP to 256
        self.output_stream.write("// Bootstrap code\n")
        self.output_stream.write("@256\n")
        self.output_stream.write("D=A\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=D\n")
        
        # Call Sys.init
        self.write_call("Sys.init", 0)

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        self.output_stream.write(f"// {command}\n")
        
        if command == "add":
            self._write_binary_op("D+M")
        elif command == "sub":
            self._write_binary_op("M-D")
        elif command == "and":
            self._write_binary_op("D&M")
        elif command == "or":
            self._write_binary_op("D|M")
        elif command == "neg":
            self._write_unary_op("-M")
        elif command == "not":
            self._write_unary_op("!M")
        elif command == "shiftleft":
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("M=M+M\n")  # M + M is equivalent to M << 1
            
        elif command == "shiftright":
            # Right shift implementation using direct bit-shifting in Hack assembly
            # Create labels for this operation
            shift_label = f"SHIFT_{self.label_counter}"
            self.label_counter += 1
            
            # Get the value from the stack
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("D=M\n")  # D = value to shift
            
            # Check if negative and handle appropriately
            self.output_stream.write("@R13\n")  # Use R13 to store sign bit
            self.output_stream.write("M=0\n")   # Default to positive
            self.output_stream.write(f"@{shift_label}_CHECK_NEG\n")
            self.output_stream.write("D;JGE\n") # Skip if positive
            
            # It's negative, set sign flag
            self.output_stream.write("@R13\n")
            self.output_stream.write("M=-1\n") 
            
            self.output_stream.write(f"({shift_label}_CHECK_NEG)\n")
            
            # Get absolute value
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write("@R13\n")
            self.output_stream.write("D=D&M\n") # If negative, D is negative, else 0
            self.output_stream.write("@R14\n")
            self.output_stream.write("M=D\n")   # R14 = sign adjustment
            
            # Get absolute value
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write("@R14\n")
            self.output_stream.write("D=D+M\n") # If was negative, adding neg sign makes positive
            
            # Shift right by dividing by 2
            self.output_stream.write("D=D/2\n") # Divide by 2
            
            # Store result temporarily
            self.output_stream.write("@R14\n")
            self.output_stream.write("M=D\n")
            
            # Check if originally negative to restore sign
            self.output_stream.write("@R13\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write(f"@{shift_label}_END\n")
            self.output_stream.write("D;JGE\n") # Skip if was positive
            
            # It was negative, negate the result
            self.output_stream.write("@R14\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write("D=-D\n")
            self.output_stream.write("@R14\n")
            self.output_stream.write("M=D\n")
            
            self.output_stream.write(f"({shift_label}_END)\n")
            
            # Put result back on stack
            self.output_stream.write("@R14\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("M=D\n")
        elif command == "eq":
            self._write_comparison("JEQ")
        elif command == "gt":
            self._write_comparison("JGT")
        elif command == "lt":
            self._write_comparison("JLT")
    
    def _write_binary_op(self, operation: str) -> None:
        """Helper method for binary operations (add, sub, and, or)."""
        # Pop the top value from the stack into D
        self.output_stream.write("@SP\n")
        self.output_stream.write("AM=M-1\n")
        self.output_stream.write("D=M\n")
        
        # Get the second value from the stack
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M-1\n")
        
        # Perform the operation and store result in the stack
        self.output_stream.write(f"M={operation}\n")
    
    def _write_unary_op(self, operation: str) -> None:
        """Helper method for unary operations (neg, not, shiftleft, shiftright)."""
        # Get the top value from the stack, apply operation, store back
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M-1\n")
        self.output_stream.write(f"M={operation}\n")
    
    def _write_comparison(self, jump_type: str) -> None:
        """Helper method for comparison operations (eq, gt, lt)."""
        self.label_counter += 1
        label_true = f"LABEL_TRUE_{self.label_counter}"
        label_end = f"LABEL_END_{self.label_counter}"
        
        # Pop the top value from the stack into D
        self.output_stream.write("@SP\n")
        self.output_stream.write("AM=M-1\n")
        self.output_stream.write("D=M\n")
        
        # Get the second value from the stack and subtract
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("D=M-D\n")
        
        # Jump if condition is met
        self.output_stream.write(f"@{label_true}\n")
        self.output_stream.write(f"D;{jump_type}\n")
        
        # If condition is not met, set to false (0)
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("M=0\n")
        
        # Jump to end
        self.output_stream.write(f"@{label_end}\n")
        self.output_stream.write("0;JMP\n")
        
        # If condition is met, set to true (-1)
        self.output_stream.write(f"({label_true})\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("M=-1\n")
        
        # End label
        self.output_stream.write(f"({label_end})\n")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        self.output_stream.write(f"// {command} {segment} {index}\n")
        
        if command == "C_PUSH":
            if segment == "constant":
                # Push constant value onto the stack
                self.output_stream.write(f"@{index}\n")
                self.output_stream.write("D=A\n")
                self._push_d_to_stack()
            
            elif segment == "static":
                # Push static variable onto the stack
                self.output_stream.write(f"@{self.current_file}.{index}\n")
                self.output_stream.write("D=M\n")
                self._push_d_to_stack()
            
            elif segment == "temp":
                # Temp segment starts at RAM[5]
                self.output_stream.write(f"@{5 + index}\n")
                self.output_stream.write("D=M\n")
                self._push_d_to_stack()
            
            elif segment == "pointer":
                # Pointer 0 is THIS, pointer 1 is THAT
                base = "THIS" if index == 0 else "THAT"
                self.output_stream.write(f"@{base}\n")
                self.output_stream.write("D=M\n")
                self._push_d_to_stack()
            
            else:
                # Handle local, argument, this, that segments
                segment_symbol = self._get_segment_symbol(segment)
                self.output_stream.write(f"@{segment_symbol}\n")
                self.output_stream.write("D=M\n")
                self.output_stream.write(f"@{index}\n")
                self.output_stream.write("A=D+A\n")
                self.output_stream.write("D=M\n")
                self._push_d_to_stack()
        
        elif command == "C_POP":
            if segment == "static":
                # Pop to static variable
                self._pop_stack_to_d()
                self.output_stream.write(f"@{self.current_file}.{index}\n")
                self.output_stream.write("M=D\n")
            
            elif segment == "temp":
                # Temp segment starts at RAM[5]
                self._pop_stack_to_d()
                self.output_stream.write(f"@{5 + index}\n")
                self.output_stream.write("M=D\n")
            
            elif segment == "pointer":
                # Pointer 0 is THIS, pointer 1 is THAT
                base = "THIS" if index == 0 else "THAT"
                self._pop_stack_to_d()
                self.output_stream.write(f"@{base}\n")
                self.output_stream.write("M=D\n")
            
            else:
                # Handle local, argument, this, that segments
                segment_symbol = self._get_segment_symbol(segment)
                
                # Calculate address and store in R13
                self.output_stream.write(f"@{segment_symbol}\n")
                self.output_stream.write("D=M\n")
                self.output_stream.write(f"@{index}\n")
                self.output_stream.write("D=D+A\n")
                self.output_stream.write("@R13\n")
                self.output_stream.write("M=D\n")
                
                # Pop value from stack
                self._pop_stack_to_d()
                
                # Store value at the calculated address
                self.output_stream.write("@R13\n")
                self.output_stream.write("A=M\n")
                self.output_stream.write("M=D\n")
    
    def _push_d_to_stack(self) -> None:
        """Helper method to push the value in D register onto the stack."""
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=D\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M+1\n")
    
    def _pop_stack_to_d(self) -> None:
        """Helper method to pop the top value from the stack into D register."""
        self.output_stream.write("@SP\n")
        self.output_stream.write("AM=M-1\n")
        self.output_stream.write("D=M\n")
    
    def _get_segment_symbol(self, segment: str) -> str:
        """Helper method to get the base address symbol for a segment."""
        if segment == "local":
            return "LCL"
        elif segment == "argument":
            return "ARG"
        elif segment == "this":
            return "THIS"
        elif segment == "that":
            return "THAT"
        else:
            raise ValueError(f"Invalid segment: {segment}")

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command."""
        # Generate label in the context of the current function
        full_label = f"{self.current_function}${label}" if self.current_function else label
        self.output_stream.write(f"// label {label}\n")
        self.output_stream.write(f"({full_label})\n")
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command."""
        # Jump to the label in the context of the current function
        full_label = f"{self.current_function}${label}" if self.current_function else label
        self.output_stream.write(f"// goto {label}\n")
        self.output_stream.write(f"@{full_label}\n")
        self.output_stream.write("0;JMP\n")
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command."""
        # Pop the top stack value and jump to the label if it's not zero
        full_label = f"{self.current_function}${label}" if self.current_function else label
        self.output_stream.write(f"// if-goto {label}\n")
        
        # Pop the top value from the stack into D
        self._pop_stack_to_d()
        
        # Jump to the label if D is not 0
        self.output_stream.write(f"@{full_label}\n")
        self.output_stream.write("D;JNE\n")
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command.
        
        Defines the function entry point and initializes local variables to 0.
        
        Args:
            function_name (str): The name of the function.
            n_vars (int): The number of local variables.
        """
        self.output_stream.write(f"// function {function_name} {n_vars}\n")
        
        # Update the current function context
        self.current_function = function_name
        
        # Generate the function entry label
        self.output_stream.write(f"({function_name})\n")
        
        # Initialize local variables to 0
        for _ in range(n_vars):
            # Push constant 0
            self.output_stream.write("@0\n")
            self.output_stream.write("D=A\n")
            self._push_d_to_stack()
    
    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command.
        
        This follows the VM calling convention:
        1. Push return address
        2. Push LCL, ARG, THIS, THAT
        3. Set ARG = SP-n-5
        4. Set LCL = SP
        5. goto function
        6. Define return address label
        
        Args:
            function_name (str): The name of the function to call.
            n_args (int): The number of arguments pushed before the call.
        """
        # Generate a unique return address label
        self.return_counter += 1
        return_address = f"RETURN_{self.return_counter}"
        
        self.output_stream.write(f"// call {function_name} {n_args}\n")
        
        # Push return address
        self.output_stream.write(f"@{return_address}\n")
        self.output_stream.write("D=A\n")
        self._push_d_to_stack()
        
        # Save caller's LCL, ARG, THIS, THAT
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            self.output_stream.write(f"@{segment}\n")
            self.output_stream.write("D=M\n")
            self._push_d_to_stack()
        
        # Reposition ARG
        self.output_stream.write("@SP\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@5\n")
        self.output_stream.write("D=D-A\n")
        self.output_stream.write(f"@{n_args}\n")
        self.output_stream.write("D=D-A\n")
        self.output_stream.write("@ARG\n")
        self.output_stream.write("M=D\n")
        
        # Reposition LCL
        self.output_stream.write("@SP\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@LCL\n")
        self.output_stream.write("M=D\n")
        
        # Jump to the called function
        self.output_stream.write(f"@{function_name}\n")
        self.output_stream.write("0;JMP\n")
        
        # Generate return address label
        self.output_stream.write(f"({return_address})\n")
    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command.
        
        This follows the VM return protocol:
        1. Store LCL in frame temp variable (R13)
        2. Get return address from *(frame-5) and store it in R14
        3. *ARG = pop() - reposition return value for caller
        4. Restore SP = ARG+1 for caller
        5. Restore THAT, THIS, ARG, LCL from saved values
        6. Jump to return address
        """
        self.output_stream.write("// return\n")
        
        # Store LCL in R13 (frame)
        self.output_stream.write("@LCL\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@R13\n")  # R13 is frame
        self.output_stream.write("M=D\n")
        
        # Save return address in R14
        self.output_stream.write("@5\n")
        self.output_stream.write("D=A\n")
        self.output_stream.write("@R13\n")
        self.output_stream.write("D=M-D\n")  # frame-5 in D register
        self.output_stream.write("A=D\n")    # Set A to the calculated address
        self.output_stream.write("D=M\n")    # Get the value at that address
        self.output_stream.write("@R14\n")  # R14 is return address
        self.output_stream.write("M=D\n")
        
        # Reposition the return value for the caller
        self._pop_stack_to_d()
        self.output_stream.write("@ARG\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=D\n")
        
        # Reposition SP for the caller (ARG+1)
        self.output_stream.write("@ARG\n")
        self.output_stream.write("D=M+1\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=D\n")
        
        # Restore THAT (frame-1)
        self.output_stream.write("@R13\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@1\n")
        self.output_stream.write("D=D-A\n")
        self.output_stream.write("A=D\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@THAT\n")
        self.output_stream.write("M=D\n")
        
        # Restore THIS (frame-2)
        self.output_stream.write("@R13\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@2\n")
        self.output_stream.write("D=D-A\n")
        self.output_stream.write("A=D\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@THIS\n")
        self.output_stream.write("M=D\n")
        
        # Restore ARG (frame-3)
        self.output_stream.write("@R13\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@3\n")
        self.output_stream.write("D=D-A\n")
        self.output_stream.write("A=D\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@ARG\n")
        self.output_stream.write("M=D\n")
        
        # Restore LCL (frame-4)
        self.output_stream.write("@R13\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@4\n")
        self.output_stream.write("D=D-A\n")
        self.output_stream.write("A=D\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@LCL\n")
        self.output_stream.write("M=D\n")
        
        # Jump to return address
        self.output_stream.write("@R14\n")  # R14 is return address
        self.output_stream.write("A=M\n")
        self.output_stream.write("0;JMP\n")