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


class Field(object):
    def __init__(self, value, size):
        self.value = value
        self.size = size

    def serialize(self):
        return format(self.value, f'0{self.size}b')

class FieldOp(Field):
    def __init__(self, value):
         super(FieldOp, self).__init__(value, 8)

class FieldRd(Field):
    def __init__(self, value):
         super(FieldRd, self).__init__(value, 4)

class FieldRs(Field):
    def __init__(self, value):
         super(FieldRs, self).__init__(value, 4)

class FieldRt(Field):
    def __init__(self, value):
         super(FieldRt, self).__init__(value, 4)

class CommandGeneral(ctypes.BigEndianStructure):
    _fields_ = [
        ("op", ctypes.c_uint32, 6),
        ("other", ctypes.c_uint32, 14),
    ]
class CommandRFormat(object):
    def __init__(self, op, rd, rs, rt):
        self.op = FieldOp(op)
        self.rd = FieldRd(op)
        self.rs = FieldRs(op)
        self.rt = FieldRt(op)

    def serialize(self):
        return "".join([
            self.op.serialize(),
            self.rd.serialize(),
            self.rs.serialize(),
            self.rt.serialize(),
        ])

class CommandIFormat(ctypes.BigEndianStructure):
    _fields_ = [
        ("op", ctypes.c_uint32, 8),
        ("rd", ctypes.c_uint32, 4),
        ("rs", ctypes.c_uint32, 4),
        ("rt", ctypes.c_uint32, 4),
        ("imm", ctypes.c_uint32, 20),
    ]


# class CommandRFormat(ctypes.BigEndianStructure):
#     _fields_ = [
#         ("op", ctypes.c_uint32, 8),
#         ("rd", ctypes.c_uint32, 4),
#         ("rs", ctypes.c_uint32, 4),
#         ("rt", ctypes.c_uint32, 4),
#     ]
    # _fields_ = [
    #     ("op", ctypes.c_uint32, 6),
    #     ("rs", ctypes.c_uint32, 5),
    #     ("rt", ctypes.c_uint32, 5),
    #     ("rd", ctypes.c_uint32, 5),
    #     ("shamt", ctypes.c_uint32, 5),
    #     ("funct", ctypes.c_uint32, 6),
    # ]

# class CommandJFormat(ctypes.BigEndianStructure):
#     _fields_ = [
#         ("op", ctypes.c_uint32, 6),
#         ("address", ctypes.c_uint32, 26),
#     ]
OPCODE_TO_NUMBER = {
    "add" : 0,
    "sub" : 1,
    "mul" : 2,
    "and" : 3,
    "or"  : 4,
    "xor"  : 5,
    "sll"  : 6,
    "sra"  : 7,
    "srl"  : 8,
    "beq"  : 9,
    "bne"  : 10,
    "blt"  : 11,
    "bgt"  : 12,
    "ble"  : 13,
    "bge"  : 14,
    "jal"  : 15,
    "lw"  : 16,
    "sw"  : 17,
    "reti"  : 18,
    "in"  : 19,
    "out"  : 20,
    "halt"  : 21,
}

REGISTER_TO_NUMBER = {
    "zero" : 0,
    "imm" : 1,
    "v0" : 2,
    "a0" : 3,
    "a1" : 4,
    "a2" : 5,
    "a3" : 6,
    "t0" : 7,
    "t1" : 8,
    "t2" : 9,
    "s0" : 10,
    "s1" : 11,
    "s2" : 12,
    "gp" : 13,
    "sp" : 14,
    "ra" : 15,
}






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

        aaa = self.pack()
        print(aaa)
        # import ipdb;ipdb.set_trace()

    def pack(self):
        packed_command = CommandRFormat(OPCODE_TO_NUMBER[self.opcode],
                                        REGISTER_TO_NUMBER[self.rd.strip(r"$")],
                                        REGISTER_TO_NUMBER[self.rs.strip(r"$")],
                                        REGISTER_TO_NUMBER[self.rt.strip(r"$")],
                                        )
        # packed_command.rd = REGISTER_TO_NUMBER[self.rd.strip(r"$")]
        # packed_command.rs = REGISTER_TO_NUMBER[self.rs.strip(r"$")]
        # packed_command.rt = REGISTER_TO_NUMBER[self.rt.strip(r"$")]
        # packed_value = struct.unpack_from('!I', packed_command)[0]
        import ipdb;ipdb.set_trace()
        # return format(packed_value, '08b')
        # return format(packed_value, '020b')

        # Return data without 0b prefix
        # return bin_data[2:]


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
