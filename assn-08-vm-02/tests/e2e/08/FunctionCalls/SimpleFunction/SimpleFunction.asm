(SimpleFunction.test)
@LCL
D=M
@0
D=D+A
M=0
@1
D=D+A
M=0
@0
D=A
@LCL
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@LCL
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
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
@SP
M=M-1
A=M
M=!M
@SP
M=M+1
@0
D=A
@ARG
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
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
@1
D=A
@ARG
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
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
@LCL
D=M
@END_FRAME
M=D
@END_FRAME
D=M
@5
A=D-A
D=M
@RETURN_ADDR_SimpleFunction.test
M=D
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
@END_FRAME
A=A-1
D=M
@THAT
M=D
@END_FRAME
D=A
@2
A=D-A
D=M
@THIS
M=D
@END_FRAME
D=A
@3
A=D-A
D=M
@ARG
M=D
@END_FRAME
D=A
@4
A=D-A
D=M
@LCL
M=D
@RETURN_ADDR_SimpleFunction.test
0;JMP
