// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

//Pseudocode:
// i = 0
// R2 = 0
// LOOP:
//     if(i == R1) goto END
//     R2 = R2 + R0
//     i = i + 1
//     goto LOOP    
// END:
//     goto END

@i      //initialize i variable and R2 register to 0
M=0
@R2
M=0
(LOOP)
    @i
    D=M
    @R1
    D=D-M
    @END
    D;JEQ       //if i equals value of R1 register, jumps to END which is an infinite loop to terminate asm program
    @R0
    D=M
    @R2
    M=M+D       //if i doesn't equal value of R1 register, we need to add R0 to R2 at least once more
    @i
    M=M+1       //increments i
    @LOOP
    0;JMP       //jumps to LOOP, because we are not done yet
(END)
    @END
    0;JMP    