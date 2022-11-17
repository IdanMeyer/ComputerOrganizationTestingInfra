import struct
import ctypes



class AssemblerException(Exception):
    pass


class Assembler(object):
    def __init__(self, assembler_path, should_compile=False):
        if should_compile:
            raise AssemblerException("Not implemented yet!")
        self.assembler_path = assembler_path

    def run(self, input__asm_file_path):
        # Returns memin.txt file
        pass


class AssemblerTestRunner(object):
    def __init__(self, assembler_path, should_compile=False):
        self.assembler = Assembler(assembler_path, should_compile=should_compile)


class CStruct(ctypes.BigEndianStructure):
    _fields_ = [
        ("op", ctypes.c_uint32, 6),  # 6 bit wide
        ("other", ctypes.c_uint32, 26), # 25 bits wide
    ]



class AssemblyLine(object):
    def __init__(self, line):
        self.raw_line = line
        self.label = None
        self.assemble_line(line)

    def _parse_line(self, raw_line):
        parts = raw_line.split()

        if len(parts) not in [5,6]:
            raise AssemblerException(f"Invalid amount of parts in assembly line: {self.raw_line}")

        # Check if there is a label
        if len(parts) == 6:
            self.label = parts[0].strip(":")
            parts = parts[1:]


        # Remove commas from command
        parts = [x.strip(',') for x in parts]
        self.opcode, self.rd, self.rs, self.rt, self.imm = tuple(parts)





    def assemble_line(self, raw_line):
        self._parse_line(raw_line)

    def __str__(self):
        s = ""
        s += f"label = {self.label}\n"
        s += f"opcode = {self.opcode}\n"
        s += f"rd = {self.rd}\n"
        s += f"rs = {self.rs}\n"
        s += f"rt = {self.rt}\n"
        s += f"imm = {self.imm}\n"
        return s

    def __repr__(self):
        return self.__str__()
