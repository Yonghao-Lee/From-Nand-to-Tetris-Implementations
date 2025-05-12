// push constant 111
// push constant 111
@111
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 333
// push constant 333
@333
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 888
// push constant 888
@888
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop static 8
// pop static 8
@SP
M=M-1
A=M
D=M
@StaticTest.8
M=D
// pop static 3
// pop static 3
@SP
M=M-1
A=M
D=M
@StaticTest.3
M=D
// pop static 1
// pop static 1
@SP
M=M-1
A=M
D=M
@StaticTest.1
M=D
// push static 3
// push static 3
@StaticTest.3
D=M
@SP
A=M
M=D
@SP
M=M+1
// push static 1
// push static 1
@StaticTest.1
D=M
@SP
A=M
M=D
@SP
M=M+1
// sub
// Arithmetic command: sub
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M-D
@SP
M=M+1
// push static 8
// push static 8
@StaticTest.8
D=M
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
