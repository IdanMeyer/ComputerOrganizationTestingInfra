import pytest
import pathlib
import random
import os

from Infra.assembler_wrapper import AssemblerTestRunner, AssemblyLine, PythonAssemblerTestRunner, OPCODE_TO_NUMBER, REGISTER_TO_NUMBER
from Infra import utils

# ASSEMBLER_PATH = "<assembler_path>"
ASSEMBLER_PATH = "../ComputerOrganizationProcessor/build/assembler"

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

def generate_random_command(newline=True):
    opcode = random.choice([op for op in OPCODE_TO_NUMBER.keys()])
    rt = random.choice([reg for reg in REGISTER_TO_NUMBER.keys()])
    rs = random.choice([reg for reg in REGISTER_TO_NUMBER.keys()])
    rd = random.choice([reg for reg in REGISTER_TO_NUMBER.keys()])
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

@pytest.mark.sanity
@pytest.mark.assembler
def test_assembler_line_with_comments(tmp_path):
    command = ""
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    command += f"{generate_random_command(newline=False)}#Some comment\n"
    command += f"{generate_random_command(newline=False)}#######Some comment\n"
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
def test_assembler_labels(tmp_path, max_label_length, extra_label_calls):
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
