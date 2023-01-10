import pytest
import pathlib
import random
import os

from Infra.assembler_wrapper import AssemblerTestRunner, AssemblyLine, PythonAssemblerTestRunner, OPCODE_TO_NUMBER, REGISTER_TO_NUMBER
from Infra import utils

ASSEMBLER_PATH = "../ComputerOrganizationProcessor/build/assembler"
# ASSEMBLER_PATH =  r"..\ComputerOrganizationProcessor\VisualStudio\Assembler\x64\Debug\Assembler.exe"

TESTS_BASE_FOLDER = pathlib.Path(__file__).parent.resolve()


@pytest.mark.sanity
@pytest.mark.assembler
def test_python_assembler():
    runner = PythonAssemblerTestRunner(ASSEMBLER_PATH)
    runner.set_input_data_from_file(f"{TESTS_BASE_FOLDER}/resources/fib.asm")
    runner.set_expected_output_from_file(f"{TESTS_BASE_FOLDER}/resources/memin.txt")
    runner.run()

@pytest.mark.sanity
@pytest.mark.assembler
def test_assembler_sanity_custom_expected_output(tmp_path):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str("halt $zero, $zero, $zero, 0")
    runner.set_expected_output("15000\n")
    runner.run()

@pytest.mark.sanity
@pytest.mark.assembler
def test_assembler_sanity_compare_from_python(tmp_path):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str("add $zero, $zero, $zero, 0")
    runner.run()

@pytest.mark.sanity
@pytest.mark.assembler
@pytest.mark.parametrize("opcode", [op for op in OPCODE_TO_NUMBER.keys()])
def test_assembler_all_opcodes(tmp_path, opcode):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str(f"{opcode} $zero, $zero, $zero, 0")
    runner.run()

@pytest.mark.sanity
@pytest.mark.assembler
@pytest.mark.parametrize("rt", [rt for rt in REGISTER_TO_NUMBER.keys()])
def test_assembler_all_registers_rt(tmp_path, rt):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str(f"add {rt}, $zero, $zero, 0")
    runner.run()

@pytest.mark.sanity
@pytest.mark.assembler
@pytest.mark.parametrize("rs", [rs for rs in REGISTER_TO_NUMBER.keys()])
def test_assembler_all_registers_rs(tmp_path, rs):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str(f"add $zero, {rs}, $zero, 0")
    runner.run()

@pytest.mark.sanity
@pytest.mark.assembler
@pytest.mark.parametrize("rd", [rd for rd in REGISTER_TO_NUMBER.keys()])
def test_assembler_all_registers_rd(tmp_path, rd):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str(f"add $zero, $zero, {rd}, 0")
    runner.run()

@pytest.mark.stress
@pytest.mark.assembler
@pytest.mark.parametrize("opcode", [op for op in OPCODE_TO_NUMBER.keys()])
@pytest.mark.parametrize("rt", [rt for rt in REGISTER_TO_NUMBER.keys()])
@pytest.mark.parametrize("rs", [rs for rs in REGISTER_TO_NUMBER.keys()])
@pytest.mark.parametrize("rd", [rd for rd in REGISTER_TO_NUMBER.keys()])
def test_assembler_all_ops_and_regs(tmp_path, opcode, rt, rs, rd):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str(f"{opcode} {rt}, {rs}, {rd}, 0")
    runner.run()


@pytest.mark.sanity
@pytest.mark.assembler
@pytest.mark.parametrize("imm", [100, 0, -100, 0x100, -0x100,
                                 0xfffff, 524287, -524287])
def test_assembler_imm_value_range(tmp_path, imm):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str(f"add $zero, $zero, $imm, {imm}")
    runner.run()

@pytest.mark.sanity
@pytest.mark.assembler
@pytest.mark.parametrize("imm", [0, 0x1, -53, 0x1337])
def test_assembler_imm_in_all_regs(tmp_path, imm):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str(f"add $imm, $imm, $imm, {imm}")
    runner.run()

def generate_random_command(newline=True, add_random_chars=True):
    opcode = random.choice([op for op in OPCODE_TO_NUMBER.keys()])
    rt = random.choice([reg for reg in REGISTER_TO_NUMBER.keys()])
    rs = random.choice([reg for reg in REGISTER_TO_NUMBER.keys()])
    rd = random.choice([reg for reg in REGISTER_TO_NUMBER.keys()])
    if add_random_chars:
        break1 = random.choice(10*[" "] + ['\t', "\t\t", "  ", " \t ", "\t \t"])
        break2 = random.choice(10*[" "] + ['\t', "\t\t", "  ", " \t ", "\t \t"])
        break3 = random.choice(10*[" "] + ['\t', "\t\t", "  ", " \t ", "\t \t"])
        break4 = random.choice(10*[" "] + ['\t', "\t\t", "  ", " \t ", "\t \t"])
        command = f"{opcode}{break1}{rt},{break2}{rs},{break3}{rd},{break4}0"
    else:
        command = f"{opcode} {rt}, {rs}, {rd}, 0"
    if newline:
        command += os.linesep

    return command

def generate_random_command_with_label(label, newline=True):
    opcode = random.choice([op for op in OPCODE_TO_NUMBER.keys()])
    rt = random.choice([reg for reg in REGISTER_TO_NUMBER.keys() if reg != "$imm"])
    rs = random.choice([reg for reg in REGISTER_TO_NUMBER.keys() if reg != "$imm"])
    rd = random.choice([reg for reg in REGISTER_TO_NUMBER.keys() if reg != "$imm"])
    command = f"{opcode} {rt}, {rs}, {rd}, {label}"

    if newline:
        command += os.linesep

    return command

def generate_word_command(address, value, newline=True):
    command = f".word {address} {value}"

    if newline:
        command += os.linesep

    return command

@pytest.mark.sanity
@pytest.mark.assembler
def test_assembler_line_with_comments(tmp_path):
    command = ""
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    command += f"{generate_random_command(newline=False)}#Some comment\n"
    command += f"{generate_random_command(newline=False)}#######Some comment\n"
    command += f"{generate_random_command(newline=False)}\t\t\t #######\n"
    command += f"{generate_random_command(newline=False)}    #    \n"
    command += f"{generate_random_command(newline=False)}#  #  #  # AA\n"
    runner.set_input_data_from_str(command)
    runner.run()

@pytest.mark.sanity
@pytest.mark.assembler
def test_assembler_long_line(tmp_path):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    # Add comment followed by 'A' for entire command max length
    command = generate_random_command(newline=False)
    command += "#"
    # Max line length is 300, but we need extra space for the \0
    command += (299-len(command)) * 'A'
    runner.set_input_data_from_str(command)
    print(command)
    runner.run()


@pytest.mark.sanity
@pytest.mark.assembler
@pytest.mark.parametrize("max_label_length", [5, 10, 20])
@pytest.mark.parametrize("extra_label_calls", [0, 30, 50])
def test_assembler_many_labels(tmp_path, max_label_length, extra_label_calls):
    # TODO: Adding label at the first without any commands before it (address zero) cause seg fault
    command = ""
    command += generate_random_command()
    labels_names = [utils.get_random_string(x) for x in range(1, max_label_length)]
    random.shuffle(labels_names)
    for label in labels_names:
        command += f"{label}:\n"
        command += generate_random_command_with_label(label)

    # Add extra calls to labels
    for _ in range(extra_label_calls):
        command += generate_random_command_with_label(random.choice(labels_names))

    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str(command)
    print(command)
    runner.run()

@pytest.mark.sanity
@pytest.mark.assembler
def test_assembler_label_in_the_middle(tmp_path):
    label_name = "SomeLabel"
    command = ""
    for _ in range(5):
        command += generate_random_command_with_label(label_name)
        command += generate_random_command()
        command += generate_random_command_with_label(label_name)
        command += generate_random_command_with_label(label_name)
    command += f"{label_name}:\n"
    for _ in range(5):
        command += generate_random_command_with_label(label_name)
        command += generate_random_command()
        command += generate_random_command()
        command += generate_random_command_with_label(label_name)
        command += generate_random_command_with_label(label_name)

    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str(command)
    print(command)
    runner.run()

@pytest.mark.sanity
@pytest.mark.assembler
@pytest.mark.parametrize("address,value", [(10, 100),
                                           (256, 0x17),
                                           (0xaa, 11),
                                           (0xbb, 0xcc)])
def test_assembler_word_command(tmp_path, address, value):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    command = ""

    command += generate_random_command()
    command += generate_word_command(address, value)


    runner.set_input_data_from_str(command)
    print(command)
    runner.run()


@pytest.mark.sanity
@pytest.mark.assembler
@pytest.mark.parametrize("iter_number", range(10))
def test_assembler_multiple_word_commands(tmp_path, iter_number):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    command = ""

    command += generate_random_command()
    command += generate_random_command()
    command += generate_random_command()
    command += generate_word_command(0x30, 45)
    command += generate_random_command()
    command += generate_word_command(300, 100)
    command += generate_word_command(302, 102)
    command += generate_word_command(301, 101)
    command += generate_word_command(0x20, 35)
    for i in range(iter_number):
        command += generate_word_command(random.randint(0, 4095), random.randint(0, 127))

    runner.set_input_data_from_str(command)
    print(command)
    runner.run()


def random_command_generation(tmp_path, number_of_commands):
    commands = []

    # Taking only a single label in order to prvent 2 lables after each other
    labels_names = [utils.get_random_string(x) for x in range(1, 2)]
    for label_name in labels_names:
        commands.append(f"{label_name}:\n")
        number_of_commands -=1

    for _ in range(number_of_commands//3):
        commands.append(generate_random_command_with_label(random.choice(labels_names)))
        number_of_commands -= 1

    for _ in range(number_of_commands):
        commands.append(generate_random_command())
        number_of_commands -= 1

    # TODO: Add words as well after fixing bugs over there

    random.shuffle(commands)
    command = "".join(commands)
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str(command)
    print(command)
    runner.run()


@pytest.mark.sanity
@pytest.mark.assembler
@pytest.mark.parametrize("number_of_commands", [5, 100, 300])
def test_assembler_random_command_generation(tmp_path, number_of_commands):
    random_command_generation(tmp_path, number_of_commands)

@pytest.mark.stress
@pytest.mark.assembler
@pytest.mark.parametrize("number_of_commands", [x for x in range(5, 1000)])
@pytest.mark.parametrize("iter_number", [x for x in range(5)])
def test_assembler_random_command_generation_stress(tmp_path, number_of_commands, iter_number):
    random_command_generation(tmp_path, number_of_commands)
