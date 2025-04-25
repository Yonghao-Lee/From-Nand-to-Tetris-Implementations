"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """
    
    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.
        
        Args:
            input_file (typing.TextIO): input file.
        """
        # Read all lines from the input file
        self.lines = input_file.read().splitlines()
        
        # Initialize variables
        self.current_command = ""
        self.current_index = -1  # We'll advance to the first command
        
        # Advance to the first command
        self.advance()
    
    def has_more_commands(self) -> bool:
        """Are there more commands in the input?
        
        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # If current_command is not empty, we have a current command
        # Otherwise, we've reached the end of the file
        return self.current_command != ""
    
    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        # Initialize current_command to empty
        self.current_command = ""
        
        # Look for the next valid command
        while self.current_index < len(self.lines) - 1:
            self.current_index += 1
            line = self.lines[self.current_index]
            
            # Remove comments (anything after //)
            comment_index = line.find('//')
            if comment_index != -1:
                line = line[:comment_index]
            
            # Remove whitespace
            line = line.strip()
            
            # If the line is not empty after removing comments and whitespace, it's a valid command
            if line:
                self.current_command = line
                return
        
        # If we get here, we've reached the end of the file without finding another command
        self.current_command = ""
    
    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if not self.current_command:
            return ""
        
        # Check if it's an A-command (starts with @)
        if self.current_command.startswith('@'):
            return "A_COMMAND"
        
        # Check if it's an L-command (enclosed in parentheses)
        if self.current_command.startswith('(') and self.current_command.endswith(')'):
            return "L_COMMAND"
        
        # Otherwise, it's a C-command
        return "C_COMMAND"
    
    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        cmd_type = self.command_type()
        
        if cmd_type == "A_COMMAND":
            # Extract symbol from @Xxx (remove the @ symbol)
            return self.current_command[1:]
            
        elif cmd_type == "L_COMMAND":
            # Extract symbol from (Xxx) (remove the parentheses)
            return self.current_command[1:-1]
        
        return ""
    
    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() != "C_COMMAND":
            return ""
        
        # Check if there's a destination (contains =)
        if '=' in self.current_command:  # THIS IS WRONG! Should check for ';'
            return self.current_command.split('=')[0].strip()
        
        # No destination
        return ""
    
    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() != "C_COMMAND":
            return ""
        
        # Start with the full command
        cmd = self.current_command
        
        # Remove dest= if present
        if '=' in cmd:
            _, cmd = cmd.split('=', 1)
        
        # Remove ;jump if present
        if ';' in cmd:
            cmd, _ = cmd.split(';', 1)
        
        # Strip off any stray whitespace
        return cmd.strip()
     
    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() != "C_COMMAND":
            return ""
        
        # Check if there's a jump (contains ;)
        if ';' in self.current_command:
            return self.current_command.split(';')[1]
        
        # No jump
        return ""