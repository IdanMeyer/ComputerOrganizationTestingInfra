from collections import OrderedDict
import os




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
    def __init__(self, input_data=None):
        self.input_data = input_data
        self.assembly_lines = OrderedDict()

    def set_input_data(self, input_data):
        self.input_data = input_data


    def _get_label_from_line(self, line):
        potential_label = None
        # Check if there is a label at line
        if ":" in line:
            potential_label = line.split(":")[0]
        return potential_label

    def is_word_command(self, line):
        line = _remove_comments_from_line(line).strip()
        split_line = line.split()
        if split_line[0] in ["word", ".word"] and len(split_line) == 3:
            return True
        return False

    def handle_word_commands(self, original_output):
        output_split_lines = original_output.splitlines()

        for line in self.input_data.splitlines():
            if not self.is_word_command(line):
                continue

            # Get address and data
            line = _remove_comments_from_line(line).strip()
            address, data = line.split()[1:3]
            address, data = int(address), f"{int(data):05x}".upper()

            # TODO: Check address not already set?

            # Fill empty lines with zeros if needed
            while len(output_split_lines) < int(address):
                output_split_lines.append(f"{int(0):05x}".upper())
            output_split_lines.append(data)


        return os.linesep.join(output_split_lines) + os.linesep


    def first_phase(self):
        current_address = 0
        label_to_address = {}

        for line in self.input_data.splitlines():
            if self.is_word_command(line):
                continue

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


    def remove_blank_lines(self):
        input_data_without_blank_lines = []
        previous_line_label = ""

        for line in self.input_data.splitlines():
            line = _remove_comments_from_line(line).strip()
            # If line is blank, continue
            if line == "":
                continue

            # Add label from previous line if needed
            if previous_line_label != "":
                if len(line.split()) == 6:
                    raise AssemblerException("Trying to set 2 labels for the same line")
                line = f"{previous_line_label}: {line}"
                previous_line_label = ""

            # If line contains only a label, add it to the next line
            potential_label = self._get_label_from_line(line)
            if potential_label is not None:
                parts = line.split()
                if len(parts) == 1:
                    # Should save label to the next line
                    previous_line_label = potential_label
                    continue

            input_data_without_blank_lines.append(line)

        self.input_data = os.linesep.join(input_data_without_blank_lines)

        return self.input_data

    def run(self):
        self.remove_blank_lines()
        # Returns memin.txt file
        label_to_address = self.first_phase()
        output = self.second_phase(label_to_address)
        output = self.handle_word_commands(output)
        print("Output:")
        print(output)
        return output


class AssemblerTestRunner(object):
    def __init__(self, assembler_path, should_compile=False):
        self.assembler = Assembler()
        self.input_data = None

    def set_input_data_from_str(self, input_data):
        self.input_data = input_data
        self.assembler.set_input_data(self.input_data)

    def set_input_data_from_file(self, file_path):
        with open(file_path, "r") as f:
            input_data = f.read()
        self.set_input_data_from_str(input_data)

    def set_expected_output_from_str(self, expected_output):
        self.expected_output = expected_output

    def set_expected_output_from_file(self, file_path):
        with open(file_path, "r") as f:
            expected_output = f.read()
        self.set_expected_output_from_str(expected_output)

    def run(self, input_data):
        raise AssemblerException("Not implemented yet")


class PythonAssemblerTestRunner(AssemblerTestRunner):
    def __init__(self, assembler_path, should_compile=False):
        self.assembler = Assembler()
        self.input_data = ""
        self.expected_output = ""

    def run(self):
        python_assembler_output = self.assembler.run()
        assert self.expected_output == python_assembler_output


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


def _remove_comments_from_line(line):
    return line.split('#', 1)[0]


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

    def _replace_tabs_with_spaces(self, line):
        return line.replace("\t", " ")

    def _parse_line(self, raw_line):
        line_without_comments = _remove_comments_from_line(raw_line)
        line_without_tabs = self._replace_tabs_with_spaces(line_without_comments)

        parts = line_without_tabs.split()

        if len(parts) not in [5, 6]:
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
        s += str(self.command)
        return s

    def __repr__(self):
        return self.__str__()
