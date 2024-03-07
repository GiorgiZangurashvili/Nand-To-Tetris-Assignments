from __future__ import annotations

import os
from dataclasses import dataclass
from os import path
from typing import TextIO


@dataclass
class VmProgram:  # TODO: your work for Projects 7 and 8 starts here
    num_label: int = 1
    current_function_name: str = ""

    map = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}

    op_map = {"add": "+", "sub": "-", "and": "&", "or": "|", "neg": "-", "not": "!"}

    jump_map = {"gt": "JGT", "lt": "JLT", "eq": "JEQ"}

    segment_regs = ["LCL", "ARG", "THIS", "THAT"]

    def __init__(self, src: str, dest: str, filename: str, is_file: bool):
        if is_file:
            self.src = src
            self.dest = dest
            self.filename = filename
        else:
            self.directory = src
            self.src = src
            self.dest = dest
            self.filename = filename
        self.is_file = is_file

    @classmethod
    def load_from(cls, file_or_directory_name: str) -> VmProgram:
        if path.isfile(file_or_directory_name):
            src_path, filename = path.split(file_or_directory_name)
            dest_filename: str = path.splitext(filename)[0] + ".asm"
            dest: str = path.join(src_path, dest_filename)
            return cls(file_or_directory_name, dest, filename, True)
        else:
            dir_name: str = path.basename(file_or_directory_name)
            dest_filename: str = dir_name + ".asm"
            dest: str = path.join(file_or_directory_name, dest_filename)
            return cls(file_or_directory_name, dest, dir_name, False)

    def translate(self) -> None:
        dest_file: TextIO = open(self.dest, "w")
        if self.is_file:
            self.translate_file(dest_file)
        else:
            self.add_bootstrap(dest_file)
            self.translate_directory(dest_file)
        dest_file.close()

    def translate_file(self, dest_file: TextIO):
        with open(self.src, "r") as file_content:
            lines = file_content.readlines()
            for line in lines:
                line = self.strip_and_remove_comment(line)
                if self.is_comment(line) or self.is_whitespace(line):
                    continue
                else:
                    self.translate_line(line.split(), dest_file)

    def translate_directory(self, dest_file: TextIO):
        for filename in os.listdir(self.src):
            if filename.find(".vm") != -1:
                self.src = path.join(self.src, filename)
                self.filename = filename
                self.translate_file(dest_file)
                self.src, file_name = path.split(self.src)


    def strip_and_remove_comment(self, line: str) -> str:
        line = line.split("\n")[0].strip()
        return line.split("//")[0].strip()

    def is_comment(self, line: str) -> bool:
        return line.find("//") == 0

    def is_whitespace(self, line: str) -> bool:
        return len(line) == 0

    def translate_line(self, line: list[str], dest_file: TextIO) -> None:
        if len(line) == 1:
            self.one_arg_vm_command(line, dest_file)
        elif len(line) == 2:
            self.two_arg_vm_command(line, dest_file)
        elif len(line) == 3:
            self.three_arg_vm_command(line, dest_file)

    def one_arg_vm_command(self, line: list[str], dest_file: TextIO) -> None:
        if line[0] == "return":
            self.translate_return_command(dest_file)
        elif line[0] == "add" or line[0] == "sub" or line[0] == "and" or line[0] == "or":
            self.translate_two_arg_func(line, dest_file)
        elif line[0] == "neg" or line[0] == "not":
            self.translate_one_arg_func(line, dest_file)
        elif line[0] == "eq" or "gt" or "lt":
            self.translate_compare_func(line, dest_file)

    def translate_two_arg_func(self, line: list[str], dest_file: TextIO) -> None:
        dest_file.write("@SP\n")
        dest_file.write("M=M-1\n")
        dest_file.write("A=M\n")
        dest_file.write("D=M\n")
        dest_file.write("@SP\n")
        dest_file.write("M=M-1\n")
        dest_file.write("A=M\n")
        dest_file.write(f"M=M{self.op_map[line[0]]}D\n")
        dest_file.write("@SP\n")
        dest_file.write("M=M+1\n")

    def translate_one_arg_func(self, line: list[str], dest_file: TextIO) -> None:
        dest_file.write("@SP\n")
        dest_file.write("M=M-1\n")
        dest_file.write("A=M\n")
        dest_file.write(f"M={self.op_map[line[0]]}M\n")
        dest_file.write("@SP\n")
        dest_file.write("M=M+1\n")

    def translate_compare_func(self, line: list[str], dest_file: TextIO) -> None:
        dest_file.write("@SP\n")
        dest_file.write("M=M-1\n")
        dest_file.write("A=M\n")
        dest_file.write("D=M\n")
        dest_file.write("@SP\n")
        dest_file.write("M=M-1\n")
        dest_file.write("A=M\n")
        dest_file.write("D=M-D\n")
        dest_file.write(f"@IS_TRUE{self.num_label}\n")
        dest_file.write(f"D;{self.jump_map[line[0]]}\n")
        dest_file.write("D=0\n")
        dest_file.write(f"@IS_FALSE{self.num_label}\n")
        dest_file.write("0;JMP\n")
        dest_file.write(f"(IS_TRUE{self.num_label})\n")
        dest_file.write("D=-1\n")
        dest_file.write(f"(IS_FALSE{self.num_label})\n")
        dest_file.write("@SP\n")
        dest_file.write("A=M\n")
        dest_file.write("M=D\n")
        dest_file.write("@SP\n")
        dest_file.write("M=M+1\n")
        self.num_label += 1

    def two_arg_vm_command(self, line: list[str], dest_file: TextIO) -> None:
        if line[0] == "label":
            self.translate_label(line, dest_file)
        elif line[0] == "goto":
            self.translate_unconditional_jmp(line, dest_file)
        elif line[0] == "if-goto":
            self.translate_conditional_jmp(line, dest_file)

    def translate_label(self, line: list[str], dest_file: TextIO) -> None:
        dest_file.write(f"({line[1]})\n")

    def translate_unconditional_jmp(self, line: list[str], dest_file: TextIO) -> None:
        dest_file.write(f"@{line[1]}\n")
        dest_file.write("0;JMP\n")

    def translate_conditional_jmp(self, line: list[str], dest_file: TextIO) -> None:
        dest_file.write("@SP\n")
        dest_file.write("M=M-1\n")
        dest_file.write("A=M\n")
        dest_file.write("D=M\n")
        dest_file.write(f"@{line[1]}\n")
        dest_file.write("D;JNE\n")

    def three_arg_vm_command(self, line: list[str], dest_file: TextIO) -> None:
        if (
            line[1] == "local"
            or line[1] == "argument"
            or line[1] == "this"
            or line[1] == "that"
        ):
            self.translate_segment_register_vm_command(line, dest_file)
        elif line[1] == "constant":
            self.translate_constant_vm_command(line, dest_file)
        elif line[1] == "static":
            self.translate_static_vm_command(line, dest_file)
        elif line[1] == "pointer":
            self.translate_pointer_vm_command(line, dest_file)
        elif line[1] == "temp":
            self.translate_temp_vm_command(line, dest_file)
        elif line[0] == "function":
            self.translate_function_command(line, dest_file)
        elif line[0] == "call":
            self.translate_call_command(line, dest_file)

    def translate_segment_register_vm_command(
        self, line: list[str], dest_file: TextIO
    ) -> None:
        register: str = self.map[line[1]]
        if line[0] == "push":
            self.push_segment_reg(line, register, dest_file)
        elif line[0] == "pop":
            self.pop_segment_reg(line, register, dest_file)

    def push_segment_reg(
        self, line: list[str], register: str, dest_file: TextIO
    ) -> None:
        dest_file.write(f"@{line[2]}\n")
        dest_file.write("D=A\n")
        dest_file.write(f"@{register}\n")
        dest_file.write("A=M+D\n")
        dest_file.write("D=M\n")
        dest_file.write("@SP\n")
        dest_file.write("A=M\n")
        dest_file.write("M=D\n")
        dest_file.write("@SP\n")
        dest_file.write("M=M+1\n")

    def pop_segment_reg(
        self, line: list[str], register: str, dest_file: TextIO
    ) -> None:
        dest_file.write(f"@{register}\n")
        dest_file.write("D=M\n")
        dest_file.write(f"@{line[2]}\n")
        dest_file.write("D=D+A\n")
        dest_file.write("@R13\n")
        dest_file.write("M=D\n")
        dest_file.write("@SP\n")
        dest_file.write("AM=M-1\n")
        dest_file.write("D=M\n")
        dest_file.write("@R13\n")
        dest_file.write("A=M\n")
        dest_file.write("M=D\n")

    def translate_constant_vm_command(self, line: list[str], dest_file: TextIO) -> None:
        dest_file.write(f"@{line[2]}\n")
        dest_file.write("D=A\n")
        dest_file.write("@SP\n")
        dest_file.write("A=M\n")
        dest_file.write("M=D\n")
        dest_file.write("@SP\n")
        dest_file.write("M=M+1\n")

    def translate_static_vm_command(self, line: list[str], dest_file: TextIO) -> None:
        if line[0] == "push":
            self.push_static(line, dest_file)
        elif line[0] == "pop":
            self.pop_static(line, dest_file)

    def push_static(self, line: list[str], dest_file: TextIO) -> None:
        dest_file.write(f"@{self.filename}.{line[2]}\n")
        dest_file.write("D=M\n")
        dest_file.write("@SP\n")
        dest_file.write("A=M\n")
        dest_file.write("M=D\n")
        dest_file.write("@SP\n")
        dest_file.write("M=M+1\n")

    def pop_static(self, line: list[str], dest_file: TextIO) -> None:
        dest_file.write("@SP\n")
        dest_file.write("M=M-1\n")
        dest_file.write("A=M\n")
        dest_file.write("D=M\n")
        dest_file.write(f"@{self.filename}.{line[2]}\n")
        dest_file.write("M=D\n")

    def translate_pointer_vm_command(self, line: list[str], dest_file: TextIO) -> None:
        if line[0] == "push" and line[2] == "0":
            self.push_ptr("THIS", dest_file)
        elif line[0] == "pop" and line[2] == "0":
            self.pop_ptr("THIS", dest_file)
        elif line[0] == "push" and line[2] == "1":
            self.push_ptr("THAT", dest_file)
        elif line[0] == "pop" and line[2] == "1":
            self.pop_ptr("THAT", dest_file)

    def push_ptr(self, register: str, dest_file: TextIO) -> None:
        dest_file.write(f"@{register}\n")
        dest_file.write("D=M\n")
        dest_file.write("@SP\n")
        dest_file.write("A=M\n")
        dest_file.write("M=D\n")
        dest_file.write("@SP\n")
        dest_file.write("M=M+1\n")

    def pop_ptr(self, register: str, dest_file: TextIO) -> None:
        dest_file.write("@SP\n")
        dest_file.write("M=M-1\n")
        dest_file.write("A=M\n")
        dest_file.write("D=M\n")
        dest_file.write(f"@{register}\n")
        dest_file.write("M=D\n")

    def translate_temp_vm_command(self, line: list[str], dest_file: TextIO) -> None:
        index: int = 5 + int(line[2])
        if line[0] == "push":
            dest_file.write(f"@{index}\n")
            dest_file.write("D=M\n")
            dest_file.write("@SP\n")
            dest_file.write("A=M\n")
            dest_file.write("M=D\n")
            dest_file.write("@SP\n")
            dest_file.write("M=M+1\n")
        else:
            dest_file.write("@SP\n")
            dest_file.write("M=M-1\n")
            dest_file.write("A=M\n")
            dest_file.write("D=M\n")
            dest_file.write(f"@{index}\n")
            dest_file.write("M=D\n")

    def translate_call_command(self, line: list[str], dest_file: TextIO) -> None:
        # push RET_ADDR
        dest_file.write(f"@RETURN_ADDR_{line[1]}\n")
        dest_file.write("D=A\n")
        dest_file.write("@SP\n")
        dest_file.write("A=M\n")
        dest_file.write("M=D\n")
        dest_file.write("@SP\n")
        dest_file.write("M=M+1\n")

        for i in range(len(self.segment_regs)):
            self.push_segment_base_address(self.segment_regs[i], dest_file)
        self.set_argument_base_address(int(line[2]), dest_file)
        self.set_local_base_address(int(line[2]), dest_file)
        self.translate_unconditional_jmp(["goto", line[1]], dest_file)
        dest_file.write(f"(RETURN_ADDR_{line[1]})\n")

    def push_segment_base_address(self, segment: str, dest_file: TextIO) -> None:
        dest_file.write(f"@{segment}\n")
        dest_file.write("D=M\n")
        dest_file.write("@SP\n")
        dest_file.write("A=M\n")
        dest_file.write("M=D\n")
        dest_file.write("@SP\n")
        dest_file.write("M=M+1\n")

    def set_argument_base_address(self, num_args: int, dest_file: TextIO) -> None:
        offset: int = num_args + len(self.segment_regs) + 1

        dest_file.write("@SP\n")
        dest_file.write("D=M\n")
        dest_file.write(f"@{offset}\n")
        dest_file.write("D=D-A\n")
        dest_file.write("@ARG\n")
        dest_file.write("M=D\n")

    def set_local_base_address(self, num_args: int, dest_file: TextIO) -> None:
        dest_file.write("@SP\n")
        dest_file.write("D=M\n")
        dest_file.write("@LCL\n")
        dest_file.write("M=D\n")

    def translate_function_command(self, line: list[str], dest_file: TextIO) -> None:
        self.current_function_name = line[1]
        dest_file.write(f"({line[1]})\n")
        self.set_local_variables_to_zero(line, dest_file)

    def set_local_variables_to_zero(self, line: list[str], dest_file: TextIO) -> None:
        for i in range(int(line[2])):
            self.translate_constant_vm_command(["push", "constant", "0"], dest_file)

    def translate_return_command(self, dest_file: TextIO) -> None:
        dest_file.write("@LCL\n")
        dest_file.write("D=M\n")
        dest_file.write("@R13\n")
        dest_file.write("M=D\n")
        # retAddr = *(R13 – 5)
        dest_file.write("@5\n")
        dest_file.write("A=D-A\n")
        dest_file.write("D=M\n")
        dest_file.write(f"@RETURN_ADDR_{self.current_function_name}\n")
        dest_file.write("M=D\n")
        # *ARG = pop()
        dest_file.write("@SP\n")
        dest_file.write("M=M-1\n")
        dest_file.write("A=M\n")
        dest_file.write("D=M\n")
        dest_file.write("@ARG\n")
        dest_file.write("A=M\n")
        dest_file.write("M=D\n")
        # SP = ARG + 1
        dest_file.write("@ARG\n")
        dest_file.write("D=M+1\n")
        dest_file.write("@SP\n")
        dest_file.write("M=D\n")
        # THAT = *(LCL - 1)
        dest_file.write("@R13\n")
        dest_file.write("A=A-1\n")
        dest_file.write("D=M\n")
        dest_file.write("@THAT\n")
        dest_file.write("M=D\n")
        # THIS = *(endFrame – 2) // restores THIS
        dest_file.write("@R13\n")
        dest_file.write("D=A\n")
        dest_file.write("@2\n")
        dest_file.write("A=D-A\n")
        dest_file.write("D=M\n")
        dest_file.write("@THIS\n")
        dest_file.write("M=D\n")
        # ARG = *(endFrame – 3) // restores ARG
        dest_file.write("@R13\n")
        dest_file.write("D=A\n")
        dest_file.write("@3\n")
        dest_file.write("A=D-A\n")
        dest_file.write("D=M\n")
        dest_file.write("@ARG\n")
        dest_file.write("M=D\n")
        # LCL = *(endFrame – 4)
        dest_file.write("@R13\n")
        dest_file.write("D=A\n")
        dest_file.write("@4\n")
        dest_file.write("A=D-A\n")
        dest_file.write("D=M\n")
        dest_file.write("@LCL\n")
        dest_file.write("M=D\n")
        self.translate_unconditional_jmp(["goto", f"RETURN_ADDR_{self.current_function_name}"], dest_file)

    def add_bootstrap(self, dest_file: TextIO) -> None:
        dest_file.write("@256\n")
        dest_file.write("D=A\n")
        dest_file.write("@SP\n")
        dest_file.write("M=D\n")
        self.translate_call_command(["call", "Sys.init", "0"], dest_file)
