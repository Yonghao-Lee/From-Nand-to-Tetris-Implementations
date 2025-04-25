"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # A good place to start is to initialize a new Parser object:
    # parser = Parser(input_file)
    # Note that you can write to output_file like so:
    # output_file.write("Hello world! \n")
    parser = Parser(input_file)
    symbol_table = SymbolTable()
    instruction_address = 0

    # process each command
    while parser.has_more_commands():
        command_type = parser.command_type()

        if command_type == "A_COMMAND" or command_type == "C_COMMAND":
            instruction_address += 1
        
        elif command_type == "L_COMMAND":
            symbol = parser.symbol()
            symbol_table.add_entry(symbol, instruction_address)
        
        parser.advance()
    
    # second pass
    input_file.seek(0)

    parser = Parser(input_file)
    code = Code()
    next_var_address = 16

    while parser.has_more_commands():
        command_type = parser.command_type()

        if command_type == "A_COMMAND":
            symbol = parser.symbol()
            if symbol.isdigit():
                # convert to int
                address = int(symbol)
            else:
                if not symbol_table.contains(symbol):
                    # add to symbol table
                    symbol_table.add_entry(symbol, next_var_address)
                    next_var_address += 1
                
                address = symbol_table.get_address(symbol)
            
            # write to output file
            binary = format(address, '016b')
            output_file.write(binary + "\n")
        
        elif command_type == "C_COMMAND":
            dest = parser.dest()
            comp = parser.comp()
            jump = parser.jump()

            # Check if this is a shift operation
            if comp in ["A<<", "D<<", "M<<", "A>>", "D>>", "M>>"]:
                # For shift operations, encode specially
                comp_bits = code.comp(comp)
                
                # For shift operations, all destination bits should be 000
                dest_bits = "010" if dest == "D" else "000"
                binary = "101" + comp_bits + dest_bits + "000"  # Fixed jump bits for shift
            else:
                # Standard C-command encoding
                dest_bits = code.dest(dest)
                comp_bits = code.comp(comp)
                jump_bits = code.jump(jump)
                binary = "111" + comp_bits + dest_bits + jump_bits
                
            output_file.write(binary + '\n') 
        parser.advance()






if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)