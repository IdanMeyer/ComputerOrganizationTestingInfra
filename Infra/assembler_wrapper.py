from collections import OrderedDict




class AssemblerException(Exception):
    pass


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
    "$zero" : 0,
    "$imm" : 1,
    "$v0" : 2,
    "$a0" : 3,
    "$a1" : 4,
    "$a2" : 5,
    "$a3" : 6,
    "$t0" : 7,
    "$t1" : 8,
    "$t2" : 9,
    "$s0" : 10,
    "$s1" : 11,
    "$s2" : 12,
    "$gp" : 13,
    "$sp" : 14,
    "$ra" : 15,
}


class Assembler(object):
    def __init__(self, input_data):
        self.input_data = input_data
        self.assembly_lines = OrderedDict()

    def first_phase(self):
        self.current_index = 0
        for line in self.input_data.splitlines():
            self.assembly_lines[self.current_index] = AssemblyLine(line)
            self.current_index += 4

    def second_phase(self):
        pass

    def finalize(self):
        output = ""
        for _, asm_line in self.assembly_lines.items():
            output += asm_line.packed_data + "\n"

        # Fill rest of file with zeros
        while self.current_index < 4096:
            output += 20*"0" + "\n"
            self.current_index += 4

        return output


    def run(self):
        # Returns memin.txt file
        self.first_phase()
        self.second_phase()
        self.finalize()

class AssemblerTestRunner(object):
    def __init__(self, assembler_path, should_compile=False):
        input_data = "L1: sub $t0, $t2, $t1, 0\n"
        input_data += "mul $a0, $t2, $t1, 0"
        self.assembler = Assembler(input_data)
        self.assembler.run()


class Field(object):
    def __init__(self, value, size):
        self.value = value
        self.size = size

    def serialize(self):
        return format(self.value, f'0{self.size}b')

class FieldOp(Field):
    def __init__(self, value):
        value = OPCODE_TO_NUMBER[value]
        super(FieldOp, self).__init__(value, 8)

class FieldRd(Field):
    def __init__(self, value):
        value = REGISTER_TO_NUMBER[value]
        super(FieldRd, self).__init__(value, 4)

class FieldRs(Field):
    def __init__(self, value):
        value = REGISTER_TO_NUMBER[value]
        super(FieldRs, self).__init__(value, 4)

class FieldRt(Field):
    def __init__(self, value):
        value = REGISTER_TO_NUMBER[value]
        super(FieldRt, self).__init__(value, 4)

class CommandRFormat(object):
    def __init__(self, op, rd, rs, rt):
        self.op = FieldOp(op)
        self.rd = FieldRd(rd)
        self.rs = FieldRs(rs)
        self.rt = FieldRt(rt)

    def serialize(self):
        return "".join([
            self.op.serialize(),
            self.rd.serialize(),
            self.rs.serialize(),
            self.rt.serialize(),
        ])




class AssemblyLine(object):
    def __init__(self, line):
        self.raw_line = line
        self.label = None
        self.packed_data = None

        self._parse_line(line)

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

        self.packed_data = self._pack()

    def _pack(self):
        packed_command = CommandRFormat(self.opcode,
                                        self.rd,
                                        self.rs,
                                        self.rt)
        return packed_command.serialize()

    def __str__(self):
        s = ""
        s += f"label = {self.label}\n"
        s += f"opcode = {self.opcode}\n"
        s += f"rd = {self.rd}\n"
        s += f"rs = {self.rs}\n"
        s += f"rt = {self.rt}\n"
        s += f"imm = {self.imm}\n"

        if self.packed_data is not None:
            s+= "|"
            s+= self.packed_data[0:8]
            s+= "|"
            s+= self.packed_data[8:12]
            s+= "|"
            s+= self.packed_data[12:16]
            s+= "|"
            s+= self.packed_data[16:20]
            s+= "|\n"
            s+= "|opcode  |rd  |rs  |rt  |\n"
        return s

    def __repr__(self):
        return self.__str__()
