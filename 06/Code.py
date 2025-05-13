"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class Code:
    """Translates Hack assembly language mnemonics into binary codes."""
    
    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a dest mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        dest_codes = {
            "": "000",      # No destination
            "M": "001",     # Memory[A]
            "D": "010",     # D register
            "MD": "011",    # Memory[A] and D register
            "A": "100",     # A register
            "AM": "101",    # A register and Memory[A]
            "AD": "110",    # A register and D register
            "AMD": "111"    # A register, Memory[A], and D register
        }

        return dest_codes.get(mnemonic, "000")  # Default to "000" if mnemonic not found

    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: 7-bit long binary code of the given mnemonic.
        """
        # 1. clean up whitespace (both leading/trailing and internal)
        m = mnemonic.strip()
        m = ''.join(m.split())  # Remove all whitespace

        # 2. handle the 6 shift ops
        if Code.is_shift(m):
            return Code.shift_comp(m)

        # 3. standard ALU ops
        comp_codes = {
            '0':   '0101010', '1':   '0111111', '-1':  '0111010',
            'D':   '0001100', 'A':   '0110000', 'M':   '1110000',
            '!D':  '0001101', '!A':  '0110001', '!M':  '1110001',
            '-D':  '0001111', '-A':  '0110011', '-M':  '1110011',
            'D+1': '0011111', 'A+1': '0110111', 'M+1': '1110111',
            'D-1': '0001110', 'A-1': '0110010', 'M-1': '1110010',
            'D+A': '0000010', 'D+M': '1000010',
            'D-A': '0010011', 'D-M': '1010011',
            'A-D': '0000111', 'M-D': '1000111',
            'D&A': '0000000', 'D&M': '1000000',
            'D|A': '0010101', 'D|M': '1010101',
        }

        # 4. lookup
        return comp_codes.get(m, "0000000")  # Default to "0000000" if mnemonic not found

    @staticmethod
    def is_shift(mnemonic: str) -> bool:
        """
        Check if the mnemonic is a shift operation.
        
        Args:
            mnemonic (str): A comp mnemonic string.
            
        Returns:
            bool: True if it's a shift operation, False otherwise.
        """
        shifts = {'A<<', 'D<<', 'M<<', 'A>>', 'D>>', 'M>>'}
        return mnemonic in shifts
    
    @staticmethod
    def jump(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a jump mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        jump_codes = {
            "": "000",     # No jump
            "JGT": "001",  # If out > 0, jump
            "JEQ": "010",  # If out = 0, jump
            "JGE": "011",  # If out >= 0, jump
            "JLT": "100",  # If out < 0, jump
            "JNE": "101",  # If out != 0, jump
            "JLE": "110",  # If out <= 0, jump
            "JMP": "111"   # Unconditional jump
        }
        return jump_codes.get(mnemonic.strip(), "000")  # Default to "000" if mnemonic not found, and strip whitespace

    @staticmethod
    def shift_comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a shift operation mnemonic string.
            
        Returns:
            str: 7-bit long binary code for the given shift operation.
        """
        shift_codes = {
            'A<<': '0100000',
            'D<<': '0110000',
            'M<<': '1100000',
            'A>>': '0000000',
            'D>>': '0010000',
            'M>>': '1000000',
        }
        return shift_codes.get(mnemonic, "0000000")  # Default to "0000000" if mnemonic not found
