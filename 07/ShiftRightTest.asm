// push constant 10
// push constant 10
@10
D=A
@SP
A=M
M=D
@SP
M=M+1
// shiftright
// Arithmetic: shiftright
// shiftright (/2, arithmetic)
@SP
A=M-1
D=M
@R15
M=0
@SHR_POS_0
D;JGE
@R15
M=-1
D=-D
(SHR_POS_0)
@R13
M=0
@R14
M=D
(SHR_LOOP_0)
@R14
D=M
@2
D=D-A
@SHR_DONE_0
D;JLT
@2
D=A
@R14
M=M-D
@R13
M=M+1
@SHR_LOOP_0
0;JMP
(SHR_DONE_0)
@R15
D=M
@SHR_APPLY_0
D;JNE
@R13
D=M
@SHR_END_0
0;JMP
(SHR_APPLY_0)
@R13
D=M
D=-D
(SHR_END_0)
@SP
A=M-1
M=D
// Infinite loop at end
(END)
@END
0;JMP
