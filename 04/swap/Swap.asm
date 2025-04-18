// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.

// Algorithm steps:
// 1. Initialize min and max values and their addresses
// 2. Loop through the array
// 3. For each element, compare with current min/max
// 4. Update min/max values and addresses as needed
// 5. After the loop, swap the values at min/max addresses

// Initialize variables
// R0 will store min value
// R1 will store max value
// R2 will store min address
// R3 will store max address
// R4 will be loop counter
// R5 will be current address
// R6 will store current value

// Initialize with first element
@R14
D=M
@R5
M=D         // R5 = R14 (starting address)

A=D // Now A register holds the starting address of the array
D=M // Now D holds the value of the start of the array
@R0
M=D // R0 = min = first element
@R1
M=D // R1 = max = first element

@R14
D=M
@R2 
M=D // R2 = min address = first element address
@R3 
M=D // Likewise for R3 = max address = first ...

// Counter init
@0
D=A
@R4
M=D // R4 = 0 

(LOOP)
@R4
D=M
@R15
D=D-M
@SWAP
D;JGE

// Get current element address
@R14
D=M
@R4 // Counter 
D=D+M
@R5
M=D

// Get current element value
A=D
D=M
@R6
M=D 

// Comparison with min
@R0
D=M
@R6
D=D-M
@UPDATE_MIN
D;JGT

(CHECK_MAX)
// Comparison with max
@R6
D=M
@R1
D=D-M
@UPDATE_MAX
D;JGT

(CONTINUE)
// Increment counter and continue the loop
@R4
M=M+1
@LOOP
0;JMP

(UPDATE_MIN)
// Update min value and min address
@R6
D=M
@R0
M=D // R0 = new min

@R5
D=M
@R2 
M=D
@CHECK_MAX
0;JMP

(UPDATE_MAX)
// Update max value and address
@R6
D=M
@R1
M=D         // R1 = current value (new max)

@R5
D=M
@R3
M=D         // R3 = current address (new max address)
@CONTINUE
0;JMP

(SWAP)
// Swap min and max
@R2
D=M
@R3
D=D-M
@END
D;JEQ // If both addresses are equal, no need

// Load max value
@R1
D=M
@temp
M=D

// Store min value at max address
@R0
D=M
@R3
A=M
M=D

// Store max value at min address
@temp
D=M
@R2
A=M
M=D

(END)
@END
0;JMP