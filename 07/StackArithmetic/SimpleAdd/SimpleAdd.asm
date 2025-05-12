// push constant 7
// push constant 7
@7
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 8
// push constant 8
@8
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
// Arithmetic command: add
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M+D
@SP
M=M+1
