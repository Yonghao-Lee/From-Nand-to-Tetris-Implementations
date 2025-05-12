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
from Parser import Parser
from CodeWriter import CodeWriter


def translate_file(input_file, output_file, writer=None) -> CodeWriter:
    """
    Translates a single VM file to Hack assembly.
    Returns the CodeWriter instance used for translation.
    """
    input_filename, _ = os.path.splitext(os.path.basename(input_file.name))
    
    # If no writer is provided, create a new one
    if writer is None:
        writer = CodeWriter(output_file)
        
    writer.set_file_name(input_filename)

    # Create a parser for this input file
    parser = Parser(input_file)
    
    # 1) advance → 2) inspect → 3) emit
    while parser.has_more_commands():
        parser.advance()                            # ← move to the next command
        writer._write_lines([f"// {parser.current_command}"])        
        ctype = parser.command_type()
        if ctype is parser.C_ARITHMETIC:
            # use arg1() (just the operation name, e.g. "add", "eq")
            writer.write_arithmetic(parser.arg1())
        elif ctype in (parser.C_PUSH, parser.C_POP):
            # parser.arg2() is already an int if your Parser returns it so
            # you can pass it directly rather than casting again
            writer.write_push_pop(ctype, parser.arg1(), parser.arg2())
    
    return writer

if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    with open(output_path, 'w') as output_file:
        writer = None  # Initialize writer variable to track the CodeWriter
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                writer = translate_file(input_file, output_file, writer)
        
        # Call close() on the CodeWriter to add the infinite loop
        if writer:
            writer.close()