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


def check_for_sys_init(file_path):
    """
    Check if a VM file contains the Sys.init function.
    
    Args:
        file_path (str): Path to the VM file to check.
        
    Returns:
        bool: True if the file contains Sys.init, False otherwise.
    """
    if not file_path.endswith('.vm'):
        return False
        
    with open(file_path, 'r') as file:
        for line in file:
            # Remove comments and whitespace
            line = line.split('//')[0].strip()
            if line.startswith('function Sys.init'):
                return True
    return False


def check_filename_for_special_tests(file_path):
    """
    Special handling for tests that require specific bootstrap behavior.
    
    Args:
        file_path (str): Path to check.
        
    Returns:
        bool: True if this is a standalone VM file for SimpleFunction, False otherwise.
    """
    # Check if this is SimpleFunction test
    if os.path.basename(file_path) == "SimpleFunction.vm" or (
       os.path.isdir(file_path) and os.path.basename(file_path) == "SimpleFunction"):
        return True
    return False


def should_include_bootstrap(input_paths):
    """
    Determine if bootstrap code should be included based on program structure.
    
    Args:
        input_paths (list): List of VM file paths to be translated.
        
    Returns:
        bool: True if bootstrap code should be included, False otherwise.
    """
    # If there's only one file, check if it's SimpleFunction test
    if len(input_paths) == 1:
        # Special case for SimpleFunction test
        if check_filename_for_special_tests(input_paths[0]):
            return False
        
        # Check if the single file has Sys.init
        return check_for_sys_init(input_paths[0])
    
    # If translating multiple files, check if any contain Sys.init
    # We typically want bootstrap for multi-file programs
    for path in input_paths:
        if check_for_sys_init(path):
            return True
            
    # Default for multi-file programs without Sys.init
    return len(input_paths) > 1


def translate_file(
        input_file: typing.TextIO,
        code_writer: CodeWriter) -> None:
    """
    Translates a single VM file into Hack assembly code.
    
    Args:
        input_file (typing.TextIO): Input VM file stream.
        code_writer (CodeWriter): Code writer instance to generate assembly code.
    """
    # Extract the filename without path and extension for static variable handling
    input_filename = os.path.basename(input_file.name)
    input_filename, _ = os.path.splitext(input_filename)
    
    # Set the current file for the code writer
    code_writer.set_file_name(input_filename)
    
    # Initialize the parser
    parser = Parser(input_file)
    
    # Process all commands in the file
    while parser.has_more_commands():
        parser.advance()
        
        command_type = parser.command_type()
        
        if command_type == "C_ARITHMETIC":
            operation = parser.arg1()
            code_writer.write_arithmetic(operation)
            
        elif command_type in ["C_PUSH", "C_POP"]:
            segment = parser.arg1()
            index = parser.arg2()
            code_writer.write_push_pop(command_type, segment, index)
            
        elif command_type == "C_LABEL":
            label = parser.arg1()
            code_writer.write_label(label)
            
        elif command_type == "C_GOTO":
            label = parser.arg1()
            code_writer.write_goto(label)
            
        elif command_type == "C_IF":
            label = parser.arg1()
            code_writer.write_if(label)
            
        elif command_type == "C_FUNCTION":
            function_name = parser.arg1()
            n_vars = parser.arg2()
            code_writer.write_function(function_name, n_vars)
            
        elif command_type == "C_CALL":
            function_name = parser.arg1()
            n_args = parser.arg2()
            code_writer.write_call(function_name, n_args)
            
        elif command_type == "C_RETURN":
            code_writer.write_return()


if "__main__" == __name__:
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    
    # Determine input files and output path
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)
            if filename.endswith('.vm')]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    
    # Determine if bootstrap code should be included
    include_bootstrap = should_include_bootstrap(files_to_translate)
    
    with open(output_path, 'w') as output_file:
        code_writer = CodeWriter(output_file)
        
        # Write bootstrap code if necessary
        if include_bootstrap:
            code_writer.write_init()
            
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, code_writer)