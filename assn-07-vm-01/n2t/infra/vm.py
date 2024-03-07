from __future__ import annotations

from dataclasses import dataclass
from os import path
from typing import TextIO


@dataclass
class VmProgram:  # TODO: your work for Projects 7 and 8 starts here
    num_label: int = 1

    map = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}

    op_map = {"add": "+", "sub": "-", "and": "&", "or": "|", "neg": "-", "not": "!"}

    jump_map = {"gt": "JGT", "lt": "JLT", "eq": "JEQ"}

    def __init__(self, src: str, dest: str, filename: str):
        self.src = src
        self.dest = dest
        self.filename = filename

    @classmethod
    def load_from(cls, file_or_directory_name: str) -> VmProgram:
        src_path, filename = path.split(file_or_directory_name)
        dest_filename: str = path.splitext(filename)[0] + ".asm"
        dest: str = path.join(src_path, dest_filename)
        return cls(file_or_directory_name, dest, filename)

    def translate(self) -> None:
        with open(self.src, "r") as file_content:
            lines = file_content.readlines()
            dest_file: TextIO = open(self.dest, "w")
            for line in lines:
                line = self.strip_and_remove_comment(line)
                if self.is_comment(line) or self.is_whitespace(line):
                    continue
                else:
                    self.translate_line(line.split(), dest_file)

        dest_file.close()

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
        elif len(line) == 3:
            self.three_arg_vm_command(line, dest_file)

    def one_arg_vm_command(self, line: list[str], dest_file: TextIO) -> None:
        if line[0] == "add" or line[0] == "sub" or line[0] == "and" or line[0] == "or":
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
