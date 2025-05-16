"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import os

class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output = output_stream
        self.current_file_name = ""
        self.label_counter = 0
        self.write_init()
        
    def write_init(self) -> None:
        """Writes the initial VM initialization code."""
        self._write_comment("VM Translator - Project 7")
        
    def _write_comment(self, comment: str) -> None:
        """Writes a comment line to the output file.
        
        Args:
            comment (str): The comment to write.
        """
        self.output.write(f"// {comment}\n")
        
    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.current_file_name = filename
        
    def _write_push_to_stack(self) -> None:
        """Writes assembly code to push the value in D register onto the stack."""
        # Store D in *SP and increment SP
        self.output.write("@SP\n")
        self.output.write("A=M\n")
        self.output.write("M=D\n")
        self.output.write("@SP\n")
        self.output.write("M=M+1\n")
        
    def _write_pop_from_stack(self) -> None:
        """Writes assembly code to pop a value from the stack into D register."""
        # Decrement SP and load value into D
        self.output.write("@SP\n")
        self.output.write("M=M-1\n")
        self.output.write("A=M\n")
        self.output.write("D=M\n")
        
    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        self._write_comment(f"Arithmetic: {command}")
        
        # Binary operations: add, sub, and, or
        if command in ["add", "sub", "and", "or"]:
            # Pop the top two values from the stack
            self._write_pop_from_stack()  # D = y (second operand)
            self.output.write("@R13\n")   # Store y in R13
            self.output.write("M=D\n")
            self._write_pop_from_stack()  # D = x (first operand)
            
            # Perform operation based on command
            if command == "add":
                self.output.write("@R13\n")
                self.output.write("D=D+M\n")  # D = x + y
            elif command == "sub":
                self.output.write("@R13\n")
                self.output.write("D=D-M\n")  # D = x - y
            elif command == "and":
                self.output.write("@R13\n")
                self.output.write("D=D&M\n")  # D = x & y
            elif command == "or":
                self.output.write("@R13\n")
                self.output.write("D=D|M\n")  # D = x | y
                
            # Push result back to stack
            self._write_push_to_stack()
             
        # Unary operations: neg, not
        elif command in ["neg", "not"]:
            self._write_pop_from_stack()  # D = top of stack
            
            if command == "neg":
                self.output.write("D=-D\n")  # D = -D
            elif command == "not":
                self.output.write("D=!D\n")  # D = !D
                
            # Push result back to stack
            self._write_push_to_stack()
            
        # Comparison operations: eq, gt, lt
        elif command in ["eq", "gt", "lt"]:
            # Specially handle comparisons to properly handle overflow
            self._write_comment(f"Special handling for {command} comparison")
            
            # Pop y and x from stack
            self._write_pop_from_stack()  # D = y (second operand)
            self.output.write("@R14\n")   # Store y in R14
            self.output.write("M=D\n")
            self._write_pop_from_stack()  # D = x (first operand)
            self.output.write("@R13\n")   # Store x in R13
            self.output.write("M=D\n")
            
            # Create unique labels
            true_label = f"{command.upper()}_TRUE_{self.label_counter}"
            false_label = f"{command.upper()}_FALSE_{self.label_counter}"
            end_label = f"{command.upper()}_END_{self.label_counter}"
            self.label_counter += 1
            
            if command == "eq":
                # Check if x == y directly
                self.output.write("@R13\n")  # Load x
                self.output.write("D=M\n")
                self.output.write("@R14\n")  # Compare with y
                self.output.write("D=D-M\n") # D = x - y
                self.output.write(f"@{true_label}\n")
                self.output.write("D;JEQ\n") # If x == y, jump to true
                self.output.write(f"@{false_label}\n")
                self.output.write("0;JMP\n") # Otherwise, jump to false
                
            elif command == "gt":
                # Check if x and y have different signs
                self.output.write("@R13\n")
                self.output.write("D=M\n")      # D = x
                self.output.write("@X_POS_GT_{}\n".format(self.label_counter))
                self.output.write("D;JGE\n")    # If x >= 0, jump to X_POS
                
                # x < 0
                self.output.write("@R14\n")
                self.output.write("D=M\n")      # D = y
                self.output.write("@SAME_SIGN_GT_{}\n".format(self.label_counter))
                self.output.write("D;JLT\n")    # If y < 0 too, both negative, check normally
                
                # x < 0, y >= 0: clearly x < y
                self.output.write(f"@{false_label}\n")
                self.output.write("0;JMP\n")
                
                # x >= 0
                self.output.write("(X_POS_GT_{})\n".format(self.label_counter))
                self.output.write("@R14\n")
                self.output.write("D=M\n")      # D = y
                self.output.write("@SAME_SIGN_GT_{}\n".format(self.label_counter))
                self.output.write("D;JGE\n")    # If y >= 0 too, both positive, check normally
                
                # x >= 0, y < 0: clearly x > y
                self.output.write(f"@{true_label}\n")
                self.output.write("0;JMP\n")
                
                # Same sign case: can safely use subtraction
                self.output.write("(SAME_SIGN_GT_{})\n".format(self.label_counter))
                self.output.write("@R13\n")
                self.output.write("D=M\n")      # D = x
                self.output.write("@R14\n") 
                self.output.write("D=D-M\n")    # D = x - y
                self.output.write(f"@{true_label}\n")
                self.output.write("D;JGT\n")    # If x > y, result is true
                self.output.write(f"@{false_label}\n")
                self.output.write("0;JMP\n")    # Otherwise, result is false
                
            elif command == "lt":
                # Check if x and y have different signs
                self.output.write("@R13\n")
                self.output.write("D=M\n")      # D = x
                self.output.write("@X_POS_LT_{}\n".format(self.label_counter))
                self.output.write("D;JGE\n")    # If x >= 0, jump to X_POS
                
                # x < 0
                self.output.write("@R14\n")
                self.output.write("D=M\n")      # D = y
                self.output.write("@SAME_SIGN_LT_{}\n".format(self.label_counter))
                self.output.write("D;JLT\n")    # If y < 0 too, both negative, check normally
                
                # x < 0, y >= 0: clearly x < y
                self.output.write(f"@{true_label}\n")
                self.output.write("0;JMP\n")
                
                # x >= 0
                self.output.write("(X_POS_LT_{})\n".format(self.label_counter))
                self.output.write("@R14\n")
                self.output.write("D=M\n")      # D = y
                self.output.write("@SAME_SIGN_LT_{}\n".format(self.label_counter))
                self.output.write("D;JGE\n")    # If y >= 0 too, both positive, check normally
                
                # x >= 0, y < 0: clearly x > y, so x < y is false
                self.output.write(f"@{false_label}\n")
                self.output.write("0;JMP\n")
                
                # Same sign case: can safely use subtraction
                self.output.write("(SAME_SIGN_LT_{})\n".format(self.label_counter))
                self.output.write("@R13\n")
                self.output.write("D=M\n")      # D = x
                self.output.write("@R14\n") 
                self.output.write("D=D-M\n")    # D = x - y
                self.output.write(f"@{true_label}\n")
                self.output.write("D;JLT\n")    # If x < y, result is true
                self.output.write(f"@{false_label}\n")
                self.output.write("0;JMP\n")    # Otherwise, result is false
                
            # False case - push 0
            self.output.write(f"({false_label})\n")
            self.output.write("@0\n")
            self.output.write("D=A\n")
            self._write_push_to_stack()
            self.output.write(f"@{end_label}\n")
            self.output.write("0;JMP\n")
            
            # True case - push -1
            self.output.write(f"({true_label})\n")
            self.output.write("@1\n")
            self.output.write("D=A\n")
            self.output.write("D=-D\n")  # D = -1
            self._write_push_to_stack()
            
            # End label
            self.output.write(f"({end_label})\n")
            
        # Shift operations
        elif command == "shiftleft":
            # Left shift is equivalent to adding the number to itself
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("D=M\n")    # Load value into D
            self.output.write("M=D+M\n")  # Double it (equivalent to left shift)
                    
        elif command == "shiftright":
            # Right shift = division by 2
            # We need to use proper bit manipulation for Hack assembly
            
            # Simple implementation using subtraction and counter
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("D=M\n")    # D = value on top of stack
            
            # Store sign bit (for restoring later if negative)
            self.output.write("@R13\n")
            self.output.write("M=0\n")    # Initialize R13 to 0 (positive)
            
            # Check if negative
            self.output.write(f"@NEG_CHECK_{self.label_counter}\n")
            self.output.write("D;JGE\n")  # Skip if positive
            
            # Handle negative number - set flag
            self.output.write("@R13\n")
            self.output.write("M=-1\n")   # Mark as negative in R13
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("M=-M\n")   # Make value positive for division
            
            self.output.write(f"(NEG_CHECK_{self.label_counter})\n")
            
            # Get the value for division
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("D=M\n")    # D = value (positive now)
            
            # Divide by 2 using a loop
            self.output.write("@R14\n")   # R14 will hold the result
            self.output.write("M=0\n")    # Initialize result to 0
            self.output.write("@R15\n")   # R15 will be our counter
            self.output.write("M=D\n")    # Initialize counter to original value
            
            # Division loop
            self.output.write(f"(DIV_LOOP_{self.label_counter})\n")
            self.output.write("@R15\n")
            self.output.write("D=M\n")    # D = counter
            self.output.write("@2\n")
            self.output.write("D=D-A\n")  # D = counter - 2
            self.output.write(f"@DIV_END_{self.label_counter}\n")
            self.output.write("D;JLT\n")  # If counter < 2, division is done
            
            # Still dividing
            self.output.write("@R15\n")
            self.output.write("M=D\n")    # Update counter = counter - 2
            self.output.write("@R14\n")
            self.output.write("M=M+1\n")  # Increment result
            self.output.write(f"@DIV_LOOP_{self.label_counter}\n")
            self.output.write("0;JMP\n")  # Continue loop
            
            self.output.write(f"(DIV_END_{self.label_counter})\n")
            self.output.write("@R14\n")
            self.output.write("D=M\n")    # D = result of division
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("M=D\n")    # Store division result
            
            # Check if we need to restore negative sign
            self.output.write("@R13\n")
            self.output.write("D=M\n")    # Get sign flag
            self.output.write(f"@END_SHIFT_{self.label_counter}\n")
            self.output.write("D;JEQ\n")  # Jump if was positive
            
            # Was negative, restore negative sign
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("M=-M\n")   # Make negative again
            
            self.output.write(f"(END_SHIFT_{self.label_counter})\n")
            self.label_counter += 1
            
        else:
            raise ValueError(f"Unknown arithmetic command: {command}")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if command == "C_PUSH":
            self._write_comment(f"push {segment} {index}")
            
            # Constant segment - push a constant value onto the stack
            if segment == "constant":
                self.output.write(f"@{index}\n")
                self.output.write("D=A\n")
                self._write_push_to_stack()
                
            # Local, argument, this, that segments
            elif segment in ["local", "argument", "this", "that"]:
                # Map segment name to base address
                segment_map = {
                    "local": "LCL",
                    "argument": "ARG",
                    "this": "THIS",
                    "that": "THAT"
                }
                base = segment_map[segment]
                
                # Get the value from segment[index]
                self.output.write(f"@{index}\n")
                self.output.write("D=A\n")
                self.output.write(f"@{base}\n")
                self.output.write("A=M+D\n")
                self.output.write("D=M\n")
                self._write_push_to_stack()
                
            # Temp segment - fixed memory locations 5 to 12
            elif segment == "temp":
                if index < 0 or index > 7:
                    raise ValueError(f"Temp segment index must be 0-7, got {index}")
                    
                self.output.write(f"@{5 + index}\n")
                self.output.write("D=M\n")
                self._write_push_to_stack()
                
            # Pointer segment - THIS (0) or THAT (1)
            elif segment == "pointer":
                if index not in [0, 1]:
                    raise ValueError(f"Pointer segment index must be 0 or 1, got {index}")
                    
                self.output.write(f"@{3 + index}\n")  # THIS is at 3, THAT is at 4
                self.output.write("D=M\n")
                self._write_push_to_stack()
                
            # Static segment - file-specific variables
            elif segment == "static":
                static_var = f"{self.current_file_name}.{index}"
                self.output.write(f"@{static_var}\n")
                self.output.write("D=M\n")
                self._write_push_to_stack()
                
            else:
                raise ValueError(f"Unknown push segment: {segment}")
                
        elif command == "C_POP":
            self._write_comment(f"pop {segment} {index}")
            
            # Cannot pop to constant segment
            if segment == "constant":
                raise ValueError("Cannot pop to constant segment")
                
            # Local, argument, this, that segments
            elif segment in ["local", "argument", "this", "that"]:
                # Map segment name to base address
                segment_map = {
                    "local": "LCL",
                    "argument": "ARG",
                    "this": "THIS",
                    "that": "THAT"
                }
                base = segment_map[segment]
                
                # Calculate the destination address and store it in R13
                self.output.write(f"@{index}\n")
                self.output.write("D=A\n")
                self.output.write(f"@{base}\n")
                self.output.write("D=M+D\n")  # D = base + index
                self.output.write("@R13\n")
                self.output.write("M=D\n")     # R13 = base + index
                
                # Pop the stack value and store it at the destination address
                self._write_pop_from_stack()  # D = popped value
                self.output.write("@R13\n")
                self.output.write("A=M\n")     # A = destination address
                self.output.write("M=D\n")     # Memory[address] = D
                
            # Temp segment - fixed memory locations 5 to 12
            elif segment == "temp":
                if index < 0 or index > 7:
                    raise ValueError(f"Temp segment index must be 0-7, got {index}")
                    
                self._write_pop_from_stack()  # D = popped value
                self.output.write(f"@{5 + index}\n")
                self.output.write("M=D\n")
                
            # Pointer segment - THIS (0) or THAT (1)
            elif segment == "pointer":
                if index not in [0, 1]:
                    raise ValueError(f"Pointer segment index must be 0 or 1, got {index}")
                    
                self._write_pop_from_stack()  # D = popped value
                self.output.write(f"@{3 + index}\n")  # THIS is at 3, THAT is at 4
                self.output.write("M=D\n")
                
            # Static segment - file-specific variables
            elif segment == "static":
                static_var = f"{self.current_file_name}.{index}"
                self._write_pop_from_stack()  # D = popped value
                self.output.write(f"@{static_var}\n")
                self.output.write("M=D\n")
                
            else:
                raise ValueError(f"Unknown pop segment: {segment}")
                
        else:
            raise ValueError(f"Unknown command type: {command}")
            
    def close(self) -> None:
        """Writes termination code."""
        self._write_comment("End of program")
        self.output.write("(END)\n")
        self.output.write("@END\n")
        self.output.write("0;JMP\n")

    # Project 8 functions (placeholders for now)
    def write_label(self, label: str) -> None:
        pass
    
    def write_goto(self, label: str) -> None:
        pass
    
    def write_if(self, label: str) -> None:
        pass
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        pass
    
    def write_call(self, function_name: str, n_args: int) -> None:
        pass
    
    def write_return(self) -> None:
        pass