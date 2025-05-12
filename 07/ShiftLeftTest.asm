// push constant 4
// push constant 4
@4
D=A
@SP
A=M
M=D
@SP
M=M+1
// shiftleft
// Arithmetic: shiftleft
// shiftleft (*2)
@SP
A=M-1
D=M
M=D+M
// Infinite loop at end
(END)
@END
0;JMP
