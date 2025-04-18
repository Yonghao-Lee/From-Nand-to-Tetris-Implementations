// This file is part of nand2tetris, as taught in The Hebrew University, and 
// was written by Aviv Yaish. It is an extension to the specifications given 
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017), 
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// This program illustrates low-level handling of the screen and keyboard
// devices, as follows.
//
// The program runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
// 
// Assumptions:
// Your program may blacken and clear the screen's pixels in any spatial/visual
// Order, as long as pressing a key continuously for long enough results in a
// fully blackened screen, and not pressing any key for long enough results in a
// fully cleared screen.
//
// Test Scripts:
// For completeness of testing, test the Fill program both interactively and
// automatically.
// 
// The supplied FillAutomatic.tst script, along with the supplied compare file
// FillAutomatic.cmp, are designed to test the Fill program automatically, as 
// described by the test script documentation.
//
// The supplied Fill.tst script, which comes with no compare file, is designed
// to do two things:
// - Load the Fill.hack program
// - Remind you to select 'no animation', and then test the program
//   interactively by pressing and releasing some keyboard keys

// Put your code here.

// The screen memory starts at address 16384 (SCREEN)
// The keyboard status is at address 24576 (KBD)
// The screen is 512×256 pixels = 131,072 bits, need 8192 registers to represent the screen
// black when the pixel is 1, 0 else

@color    // declare color variable
M=0      // by default is white

(LOOP)

  @SCREEN
  D=A
  @pixels
  M=D         // pixel address, goes from 16384 to 16384 + 8192 == 24576

  @KBD    // keyboard address
  D=M
  @BLACK
  D;JGT     // if(keyboard > 0) goto BLACK
  
  @color
  M=0       // set to white
  @COLOR_SCREEN
  0;JMP     // jump to subroutine that colors the screen
  
  (BLACK)
    @color
    M=-1    // set to black (2's complement 111111111...)

  (COLOR_SCREEN)
    @color
    D=M
    @pixels
    A=M         // VERY IMPORTANT! indirect address
    M=D         // color M[pixels] with @color
    
    @pixels
    M=M+1
    D=M
        
    @24576
    D=D-A
    @COLOR_SCREEN
    D;JLT

@LOOP
0;JMP // infinite loop