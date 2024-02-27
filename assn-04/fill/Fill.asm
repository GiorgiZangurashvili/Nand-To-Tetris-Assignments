// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// Pseudocode:
// words=8192
// LOOP:
//     goto FILL
// FILL:
//     i=0
//     FILL_LOOP:
//         if(i == pixels) goto LOOP
//         if(KBD == 0) goto SET_WHITE
//         SCREEN + i = -1
//         goto END_OF_LOOP
//         SET_WHITE:
//             SCREEN + i = 0
//         END_OF_LOOP:
//             i = i + 1
//             goto FILL_LOOP

@8192       //there are 256 rows of 32 16 bit registers. 32 * 256 = 8192
D=A
@words
M=D
(LOOP)
    @FILL
    0;JMP
(FILL)
    @i      //initialize i variable
    M=0
    (FILL_LOOP)
        @i
        D=M
        @words
        D=D-M
        @LOOP
        D;JEQ       //if i equals words: jumps back to LOOP (infinite loop)
        @KBD
        D=M
        @SET_WHITE
        D;JEQ       //if KBD equals 0, it means none of the key is pressed and screen should be filled with white pixels (jumps to SET_WHITE)
        @i
        D=M
        @SCREEN
        A=A+D       //sets the address register A, so that we can access M[A+D]
        M=-1        //with two's complement -1 (decimal) -> 111...111 (binary). so if we want to set 1s to 16 bits, we can do it by M=-1
        @END_OF_LOOP //jumps to END_OF_LOOP, which increments i and jumps back to FILL_LOOP
        0;JMP
        (SET_WHITE)
            @i
            D=M
            @SCREEN
            A=A+D
            M=0     //sets 16 bits to 0
        (END_OF_LOOP)
            @i
            M=M+1
            @FILL_LOOP
            0;JMP 