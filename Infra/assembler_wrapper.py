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
        current_address = 0
        label_to_address = {}
        for line in self.input_data.splitlines():
            assembly_line = AssemblyLine(line)
            if assembly_line.label is not None:
                label_to_address[assembly_line.label] = current_address
            self.assembly_lines[current_address] = assembly_line
            current_address += assembly_line.length_lines()
        return label_to_address


    def second_phase(self, label_to_address):
        output = ""
        for _, line in self.assembly_lines.items():
            line.convert_label_to_address(label_to_address)
            line_bytes = line.serialize_to_bytes()
            if len(line_bytes) == 5:
                output += f"{line_bytes}\n"
            elif len(line_bytes) == 10:
                output += f"{line_bytes[0:5]}\n{line_bytes[5:10]}\n"
            else:
                raise AssemblerException(f"Invalid amount of bytes in line: {line}")

        return output


    def run(self):
        # Returns memin.txt file
        label_to_address = self.first_phase()
        output = self.second_phase(label_to_address)
        print("Output:")
        print(output)
        # self.finalize()


class AssemblerTestRunner(object):
    def __init__(self, assembler_path, should_compile=False):
        # input_data = "L1: sub $t0, $t2, $t1, 0\n"
        # input_data += "mul $a0, $t2, $t1, 0\n"
        # input_data += "jal $ra, $imm, $zero, L1\n"
        input_data = '''add $t2, $zero, $imm, 1
	out $t2, $zero, $imm, 2
	sll $sp, $t2, $imm, 11
	add $t2, $zero, $imm, L3 # 1234
	out $t2, $zero, $imm, 6
	lw $a0, $zero, $imm, 256
	jal $ra, $imm, $zero, fib
	sw $v0, $zero, $imm, 257
	halt $zero, $zero, $zero, 0
fib: add $sp, $sp, $imm, -3				# adjust stack for 3 items
	sw $s0, $sp, $imm, 2				# save $s0
	sw $ra, $sp, $imm, 1				# save return address
	sw $a0, $sp, $imm, 0				# save argument
	add $t2, $zero, $imm, 1				# $t2 = 1
	bgt $imm, $a0, $t2, L1				# jump to L1 if x > 1
	add $v0, $a0, $zero, 0				# otherwise, fib(x) = x, copy input
	beq $imm, $zero, $zero, L2			# jump to L2
    L1: sub $a0, $a0, $imm, 1				# calculate x - 1
	jal $ra, $imm, $zero, fib			# calc $v0=fib(x-1)
	add $s0, $v0, $zero, 0				# $s0 = fib(x-1)
	lw $a0, $sp, $imm, 0				# restore $a0 = x
	sub $a0, $a0, $imm, 2				# calculate x - 2
	jal $ra, $imm, $zero, fib			# calc fib(x-2)
	add $v0, $v0, $s0, 0				# $v0 = fib(x-2) + fib(x-1)
	lw $a0, $sp, $imm, 0				# restore $a0
	lw $ra, $sp, $imm, 1				# restore $ra
	lw $s0, $sp, $imm, 2				# restore $s0
    L2: add $sp, $sp, $imm, 3				# pop 3 items from stack
	add $t0, $a0, $zero, 0				# $t0 = $a0
	sll $t0, $t0, $imm, 16				# $t0 = $t0 << 16
	add $t0, $t0, $v0, 0				# $t0 = $t0 + $v0
	out $t0, $zero, $imm, 10			# write $t0 to display
	beq $ra, $zero, $zero, 0			# and return
    L3: in $t1, $zero, $imm, 9				# read leds register into $t1
	sll $t1, $t1, $imm, 1				# left shift led pattern to the left
	or $t1, $t1, $imm, 1				# lit up the rightmost led
	out $t1, $zero, $imm, 9				# write the new led pattern
	add $t1, $zero, $imm, 255			# $t1 = 255
	out $t1, $zero, $imm, 21			# set pixel color to white
	add $t1, $zero, $imm, 1				# $t1 = 1
	out $t1, $zero, $imm, 22			# draw pixel
	in $t1, $zero, $imm, 20				# read pixel address
	add $t1, $t1, $imm, 257				# $t1 += 257
	out $t1, $zero, $imm, 20			# update address
	out $zero, $zero, $imm, 5			# clear irq2 status
	reti $zero, $zero, $zero, 0			# return from interrupt'''
        self.assembler = Assembler(input_data)
        self.assembler.run()

def num_to_bin(num, wordsize):
    if num < 0:
        num = 2**wordsize+num
    base = bin(num)[2:]
    padding_size = wordsize - len(base)
    return '0' * padding_size + base

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

class FieldImm(Field):
    def __init__(self, value):
        try:
            value = int(value)
        except ValueError:
            pass
        super(FieldImm, self).__init__(value, 20)

    def serialize(self):
        return num_to_bin(self.value, 20)


class CommandRFormat(object):
    def __init__(self, op, rd, rs, rt):
        self.op = FieldOp(op)
        self.rd = FieldRd(rd)
        self.rs = FieldRs(rs)
        self.rt = FieldRt(rt)
        self.imm = None
        self.should_label_be_replaced = False

    def update_label(self, address):
        raise AssemblerException("Cannot update label on R format")

    def serialize(self):
        return "".join([
            self.op.serialize(),
            self.rd.serialize(),
            self.rs.serialize(),
            self.rt.serialize(),
        ])

    def __str__(self):
        packed_data = self.serialize()
        s = ""
        s+= "|"
        s+= packed_data[0:8]
        s+= "|"
        s+= packed_data[8:12]
        s+= "|"
        s+= packed_data[12:16]
        s+= "|"
        s+= packed_data[16:20]
        s+= "|\n"
        s+= "|opcode  |rd  |rs  |rt  |\n"
        return s

class CommandIFormat(object):
    def __init__(self, op, rd, rs, rt, imm):
        self.op = FieldOp(op)
        self.rd = FieldRd(rd)
        self.rs = FieldRs(rs)
        self.rt = FieldRt(rt)
        self.imm = FieldImm(imm)
        self.should_label_be_replaced = False

        if type(self.imm.value) is str:
            if self.imm.value[0].isalpha():
                self.should_label_be_replaced = True


    def update_label(self, address):
        self.imm.value = address
        self.should_label_be_replaced = False

    def serialize(self):
        return "".join([
            self.op.serialize(),
            self.rd.serialize(),
            self.rs.serialize(),
            self.rt.serialize(),
            self.imm.serialize(),
        ])

    def __str__(self):
        packed_data = self.serialize()
        s = ""
        s+= "|"
        s+= packed_data[0:8]
        s+= "|"
        s+= packed_data[8:12]
        s+= "|"
        s+= packed_data[12:16]
        s+= "|"
        s+= packed_data[16:20]
        s+= "|"
        s+= packed_data[20:40]
        s+= "|\n"
        s+= "|opcode  |rd  |rs  |rt  |imm                 |\n"
        return s




class AssemblyLine(object):
    def __init__(self, line):
        self.raw_line = line
        self.label = None

        self._parse_line(line)

    def is_I_format(self):
        # TODO: Is there a situation where this is an I command without imm in one of the regs?
        return any([
            self.rd == "$imm",
            self.rs == "$imm",
            self.rt == "$imm"
        ])

    def length_lines(self):
        if self.is_I_format():
            return 2
        return 1

    def _parse_line(self, raw_line):
        line_without_comments = raw_line.split('#', 1)[0]
        parts = line_without_comments.split()

        if len(parts) not in [5,6]:
            raise AssemblerException(f"Invalid amount of parts in assembly line: {self.raw_line}")

        # Check if there is a label
        if len(parts) == 6:
            self.label = parts[0].strip(":")
            parts = parts[1:]


        # Remove commas from command
        parts = [x.strip(',') for x in parts]
        self.opcode, self.rd, self.rs, self.rt, self.imm = tuple(parts)

        self._pack(self.opcode, self.rd, self.rs, self.rt, self.imm)

    def _pack(self, opcode, rd, rs, rt, imm):
        if r"$imm" in [rd, rs, rt]:
            self.command = CommandIFormat(opcode, rd, rs, rt, imm)
        else:
            self.command = CommandRFormat(opcode, rd, rs, rt)

    def serialize_to_bits(self):
        return self.command.serialize()

    def serialize_to_bytes(self):
        hex_command = int(self.serialize_to_bits(), 2)
        if self.is_I_format():
            return f"{hex_command:010x}".upper()
        else:
            return f"{hex_command:05x}".upper()

    def convert_label_to_address(self, label_to_address):
        if self.command.should_label_be_replaced:
            label_name = self.command.imm.value
            if label_name not in label_to_address:
                raise AssemblerException(f"Cannot find address of label: {label_name}")
            self.command.update_label(int(label_to_address[label_name]))

    def __str__(self):
        s = ""
        # s += f"label = {self.label}\n"
        # s += f"opcode = {self.opcode}\n"
        # s += f"rd = {self.rd}\n"
        # s += f"rs = {self.rs}\n"
        # s += f"rt = {self.rt}\n"
        # s += f"imm = {self.imm}\n"

        s += str(self.command)
        return s

    def __repr__(self):
        return self.__str__()
