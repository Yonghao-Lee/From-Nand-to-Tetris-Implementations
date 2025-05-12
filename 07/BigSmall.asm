// push constant 30000
// push constant 30000
@30000
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant -20000
// push constant -20000
@-20000
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
// Arithmetic: gt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@GT_TRUE_0
D;JGT
@SP
A=M
M=0
@GT_END_0
0;JMP
(GT_TRUE_0)
@SP
A=M
M=-1
(GT_END_0)
@SP
M=M+1
// push constant -30000
// push constant -30000
@-30000
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 20000
// push constant 20000
@20000
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
// Arithmetic: gt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@GT_TRUE_1
D;JGT
@SP
A=M
M=0
@GT_END_1
0;JMP
(GT_TRUE_1)
@SP
A=M
M=-1
(GT_END_1)
@SP
M=M+1
// push constant 30000
// push constant 30000
@30000
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant -20000
// push constant -20000
@-20000
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
// Arithmetic: lt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@LT_TRUE_2
D;JLT
@SP
A=M
M=0
@LT_END_2
0;JMP
(LT_TRUE_2)
@SP
A=M
M=-1
(LT_END_2)
@SP
M=M+1
// push constant -30000
// push constant -30000
@-30000
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 20000
// push constant 20000
@20000
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
// Arithmetic: lt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@LT_TRUE_3
D;JLT
@SP
A=M
M=0
@LT_END_3
0;JMP
(LT_TRUE_3)
@SP
A=M
M=-1
(LT_END_3)
@SP
M=M+1
// Infinite loop at end
(END)
@END
0;JMP
