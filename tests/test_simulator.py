import pytest
import pathlib
import random
import os

from Infra.assembler_wrapper import AssemblerTestRunner, AssemblyLine, PythonAssemblerTestRunner, OPCODE_TO_NUMBER, REGISTER_TO_NUMBER
from Infra import utils
from Infra.simulator_wrapper import SimulatorTestRunner

ASSEMBLER_PATH = "../ComputerOrganizationProcessor/build/assembler"
SIMULATOR_PATH = "../ComputerOrganizationProcessor/build/simulator"

TESTS_BASE_FOLDER = pathlib.Path(__file__).parent.resolve()
NUMBER_OF_BITS_IN_REGISTER = 32


@pytest.mark.sanity
@pytest.mark.simulator
def test_simulator_halt(tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str("halt $zero, $zero, $zero, 0")
    runner.run({"$v0":0})
    runner.validate_all_regs_zero()

# TODO: Fails on large number, for example: 0xfffff
@pytest.mark.sanity
@pytest.mark.simulator
def test_simulator_add_sanity(tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = os.linesep.join([
        "add $t0, $zero, $imm, 10",
        "add $t1, $zero, $imm, -1",
        "add $t2, $zero, $imm, -78",
        "add $s0, $imm, $zero, 10485",
        "add $s1, $zero, $imm, -0x100",
        "add $s2, $zero, $imm, 0x70",
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":10, "$t1":-1,  "$t2":-78, "$s0":10485, "$s1":-0x100,"$s2":0x70})


@pytest.mark.sanity
@pytest.mark.simulator
def test_simulator_sub_sanity(tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = os.linesep.join([
        "add $t0, $zero, $imm, 10",
        "add $t1, $zero, $imm, -1",
        "sub $t2, $t1, $t0, 0", # t2 should be -11
        "sub $t2, $t2, $imm, 5", # t2 should be -16
        "sub $s0, $imm, $t2, 70", # s0 should be 86
        "sub $s1, $s0, $s0, 0", # s1 should be 0
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":10, "$t1":-1,  "$t2":-16, "$s0":86, "$s1":0})


@pytest.mark.sanity
@pytest.mark.simulator
def test_simulator_mul_sanity(tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = os.linesep.join([
        "add $t0, $zero, $imm, 10",
        "add $t1, $zero, $imm, -1",
        "mul $t2, $t0, $t1, 0", # t2 should be -10
        "mul $t2, $t2, $t2, 0", # t2 should be +100
        "mul $t2, $t2, $imm, 2", # t2 should be +200
        "mul $s0, $t2, $imm, -2", # t2 should be -400
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":10, "$t1":-1,  "$t2":200, "$s0":-400})


@pytest.mark.sanity
@pytest.mark.simulator
@pytest.mark.parametrize("item_1", [12, 14, 182, -56])
@pytest.mark.parametrize("item_2", [13, 17, 0, 1])
def test_simulator_and_sanity(tmp_path, item_1, item_2):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {item_1}",
        f"add $t1, $zero, $imm, {item_2}",
        f"and $t2, $t0, $t1, 0",
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":item_1, "$t1":item_2,  "$t2":item_1&item_2})

@pytest.mark.sanity
@pytest.mark.simulator
@pytest.mark.parametrize("item_1", [12, 14, 182, -56])
@pytest.mark.parametrize("item_2", [13, 17, 0, 1])
def test_simulator_or_sanity(tmp_path, item_1, item_2):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {item_1}",
        f"add $t1, $zero, $imm, {item_2}",
        f"or $t2, $t0, $t1, 0",
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":item_1, "$t1":item_2,  "$t2":item_1|item_2})

@pytest.mark.sanity
@pytest.mark.simulator
@pytest.mark.parametrize("item_1", [12, 14, 182, -56])
@pytest.mark.parametrize("item_2", [13, 17, 0, 1])
def test_simulator_xor_sanity(tmp_path, item_1, item_2):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {item_1}",
        f"add $t1, $zero, $imm, {item_2}",
        f"xor $t2, $t0, $t1, 0",
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":item_1, "$t1":item_2,  "$t2":item_1^item_2})

@pytest.mark.sanity
@pytest.mark.simulator
@pytest.mark.parametrize("number", [12, 14, 182, -56, 0, 0xf])
@pytest.mark.parametrize("bits_to_shift", [13, 17, 0, 1, 2])
def test_simulator_sll_sanity(tmp_path, number, bits_to_shift):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {number}",
        f"add $t1, $zero, $imm, {bits_to_shift}",
        f"sll $t2, $t0, $t1, 0",
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    expected_t2 = number << bits_to_shift
    runner.run({"$t0":number, "$t1":bits_to_shift,  "$t2":expected_t2})


@pytest.mark.sanity
@pytest.mark.simulator
@pytest.mark.parametrize("number", [12, 14, 182, -56, 0, 0xf])
@pytest.mark.parametrize("bits_to_shift", [13, 17, 0, 1, 2])
def test_simulator_sra_sanity(tmp_path, number, bits_to_shift):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {number}",
        f"add $t1, $zero, $imm, {bits_to_shift}",
        f"sra $t2, $t0, $t1, 0",
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    expected_t2 = number >> bits_to_shift
    runner.run({"$t0":number, "$t1":bits_to_shift,  "$t2":expected_t2})


def right_logical_shift(val, n):
    return (val % 0x100000000) >> n

# TODO: Fails on large number, for example: 0xfffff
@pytest.mark.sanity
@pytest.mark.simulator
@pytest.mark.parametrize("number", [12, 14, 182, 0xfff, 0, 0xf])
@pytest.mark.parametrize("bits_to_shift", [3, 5, 0, 1, 2])
def test_simulator_srl_sanity(tmp_path, number, bits_to_shift):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {number}",
        f"add $t1, $zero, $imm, {bits_to_shift}",
        f"srl $t2, $t0, $t1, 0",
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    expected_t2 = right_logical_shift(number, bits_to_shift)
    runner.run({"$t0":number, "$t1":bits_to_shift,  "$t2":expected_t2})


@pytest.mark.sanity
@pytest.mark.simulator
def test_simulator_lw_sw_sanity(tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    addresses = [12, 14, 182, 13, 0, 82]
    # TODO: Validate negative values???
    values = [3, 0xff, 0, 0x1234, 2]
    regs_to_save_at = ["$s0", "$s1", "$s2", "$a0", "$a1"]
    asm_input = []
    for address, value in zip(addresses, values):
        asm_input.append(f"add $t0, $zero, $imm, {address}")
        asm_input.append(f"add $t1, $zero, $imm, {value}")
        asm_input.append(f"sw $t1, $t0, $zero, 0")


    for address, reg in zip(addresses, regs_to_save_at):
        asm_input.append(f"add $t0, $zero, $imm, {address}")
        asm_input.append(f"lw {reg}, $t0, $zero, 0")

    asm_input.append(f"halt $zero, $zero, $zero, 0")

    asm_input = os.linesep.join(asm_input)
    runner.set_input_data_from_str(asm_input)
    runner.run({key : value for key, value in zip(regs_to_save_at, values)})





# @pytest.mark.sanity
# @pytest.mark.assembler
# def test_assembler_sanity_custom_expected_output(tmp_path):
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     runner.set_input_data_from_str("halt $zero, $zero, $zero, 0")
#     runner.set_expected_output("15000\n")
#     runner.run()

# @pytest.mark.sanity
# @pytest.mark.assembler
# def test_assembler_sanity_compare_from_python(tmp_path):
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     runner.set_input_data_from_str("add $zero, $zero, $zero, 0")
#     runner.run()

# @pytest.mark.sanity
# @pytest.mark.assembler
# @pytest.mark.parametrize("opcode", [op for op in OPCODE_TO_NUMBER.keys()])
# def test_assembler_all_opcodes(tmp_path, opcode):
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     runner.set_input_data_from_str(f"{opcode} $zero, $zero, $zero, 0")
#     runner.run()

# @pytest.mark.sanity
# @pytest.mark.assembler
# @pytest.mark.parametrize("rt", [rt for rt in REGISTER_TO_NUMBER.keys()])
# def test_assembler_all_registers_rt(tmp_path, rt):
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     runner.set_input_data_from_str(f"add {rt}, $zero, $zero, 0")
#     runner.run()

# @pytest.mark.sanity
# @pytest.mark.assembler
# @pytest.mark.parametrize("rs", [rs for rs in REGISTER_TO_NUMBER.keys()])
# def test_assembler_all_registers_rs(tmp_path, rs):
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     runner.set_input_data_from_str(f"add $zero, {rs}, $zero, 0")
#     runner.run()

# @pytest.mark.sanity
# @pytest.mark.assembler
# @pytest.mark.parametrize("rd", [rd for rd in REGISTER_TO_NUMBER.keys()])
# def test_assembler_all_registers_rd(tmp_path, rd):
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     runner.set_input_data_from_str(f"add $zero, $zero, {rd}, 0")
#     runner.run()

# @pytest.mark.stress
# @pytest.mark.assembler
# @pytest.mark.parametrize("opcode", [op for op in OPCODE_TO_NUMBER.keys()])
# @pytest.mark.parametrize("rt", [rt for rt in REGISTER_TO_NUMBER.keys()])
# @pytest.mark.parametrize("rs", [rs for rs in REGISTER_TO_NUMBER.keys()])
# @pytest.mark.parametrize("rd", [rd for rd in REGISTER_TO_NUMBER.keys()])
# def test_assembler_all_ops_and_regs(tmp_path, opcode, rt, rs, rd):
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     runner.set_input_data_from_str(f"{opcode} {rt}, {rs}, {rd}, 0")
#     runner.run()


# @pytest.mark.sanity
# @pytest.mark.assembler
# @pytest.mark.parametrize("imm", [100, 0, -100, 0x100, -0x100,
#                                  0xfffff, 524287, -524287])
# def test_assembler_imm_value_range(tmp_path, imm):
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     runner.set_input_data_from_str(f"add $zero, $zero, $imm, {imm}")
#     runner.run()

# @pytest.mark.sanity
# @pytest.mark.assembler
# @pytest.mark.parametrize("imm", [0, 0x1, -53, 0x1337])
# def test_assembler_imm_in_all_regs(tmp_path, imm):
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     runner.set_input_data_from_str(f"add $imm, $imm, $imm, {imm}")
#     runner.run()

# def generate_random_command(newline=True, add_random_chars=True):
#     opcode = random.choice([op for op in OPCODE_TO_NUMBER.keys()])
#     rt = random.choice([reg for reg in REGISTER_TO_NUMBER.keys()])
#     rs = random.choice([reg for reg in REGISTER_TO_NUMBER.keys()])
#     rd = random.choice([reg for reg in REGISTER_TO_NUMBER.keys()])
#     if add_random_chars:
#         break1 = random.choice(10*[" "] + ['\t', "\t\t", "  ", " \t ", "\t \t"])
#         break2 = random.choice(10*[" "] + ['\t', "\t\t", "  ", " \t ", "\t \t"])
#         break3 = random.choice(10*[" "] + ['\t', "\t\t", "  ", " \t ", "\t \t"])
#         break4 = random.choice(10*[" "] + ['\t', "\t\t", "  ", " \t ", "\t \t"])
#         command = f"{opcode}{break1}{rt},{break2}{rs},{break3}{rd},{break4}0"
#     else:
#         command = f"{opcode} {rt}, {rs}, {rd}, 0"
#     if newline:
#         command += os.linesep

#     return command

# def generate_random_command_with_label(label, newline=True):
#     opcode = random.choice([op for op in OPCODE_TO_NUMBER.keys()])
#     rt = random.choice([reg for reg in REGISTER_TO_NUMBER.keys() if reg != "$imm"])
#     rs = random.choice([reg for reg in REGISTER_TO_NUMBER.keys() if reg != "$imm"])
#     rd = random.choice([reg for reg in REGISTER_TO_NUMBER.keys() if reg != "$imm"])
#     command = f"{opcode} {rt}, {rs}, {rd}, {label}"

#     if newline:
#         command += os.linesep

#     return command

# def generate_word_command(address, value, newline=True):
#     command = f".word {address} {value}"

#     if newline:
#         command += os.linesep

#     return command

# @pytest.mark.sanity
# @pytest.mark.assembler
# def test_assembler_line_with_comments(tmp_path):
#     command = ""
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     command += f"{generate_random_command(newline=False)}#Some comment\n"
#     command += f"{generate_random_command(newline=False)}#######Some comment\n"
#     command += f"{generate_random_command(newline=False)}\t\t\t #######\n"
#     command += f"{generate_random_command(newline=False)}    #    \n"
#     command += f"{generate_random_command(newline=False)}#  #  #  # AA\n"
#     runner.set_input_data_from_str(command)
#     runner.run()

# @pytest.mark.sanity
# @pytest.mark.assembler
# def test_assembler_long_line(tmp_path):
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     # Add comment followed by 'A' for entire command max length
#     command = generate_random_command(newline=False)
#     command += "#"
#     # Max line length is 300, but we need extra space for the \0
#     command += (299-len(command)) * 'A'
#     runner.set_input_data_from_str(command)
#     print(command)
#     runner.run()


# @pytest.mark.sanity
# @pytest.mark.assembler
# @pytest.mark.parametrize("max_label_length", [5, 10, 20])
# @pytest.mark.parametrize("extra_label_calls", [0, 30, 50])
# def test_assembler_many_labels(tmp_path, max_label_length, extra_label_calls):
#     # TODO: Adding label at the first without any commands before it (address zero) cause seg fault
#     command = ""
#     command += generate_random_command()
#     labels_names = [utils.get_random_string(x) for x in range(1, max_label_length)]
#     random.shuffle(labels_names)
#     for label in labels_names:
#         command += f"{label}:\n"
#         command += generate_random_command_with_label(label)

#     # Add extra calls to labels
#     for _ in range(extra_label_calls):
#         command += generate_random_command_with_label(random.choice(labels_names))

#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     runner.set_input_data_from_str(command)
#     print(command)
#     runner.run()

# @pytest.mark.sanity
# @pytest.mark.assembler
# def test_assembler_label_in_the_middle(tmp_path):
#     label_name = "SomeLabel"
#     command = ""
#     for _ in range(5):
#         command += generate_random_command_with_label(label_name)
#         command += generate_random_command()
#         command += generate_random_command_with_label(label_name)
#         command += generate_random_command_with_label(label_name)
#     command += f"{label_name}:\n"
#     for _ in range(5):
#         command += generate_random_command_with_label(label_name)
#         command += generate_random_command()
#         command += generate_random_command()
#         command += generate_random_command_with_label(label_name)
#         command += generate_random_command_with_label(label_name)

#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     runner.set_input_data_from_str(command)
#     print(command)
#     runner.run()

# @pytest.mark.sanity
# @pytest.mark.assembler
# @pytest.mark.parametrize("address,value", [(10, 100),
#                                            (256, 0x17),
#                                            (0xaa, 11),
#                                            (0xbb, 0xcc)])
# def test_assembler_word_command(tmp_path, address, value):
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     command = ""

#     command += generate_random_command()
#     command += generate_word_command(address, value)


#     runner.set_input_data_from_str(command)
#     print(command)
#     runner.run()


# @pytest.mark.sanity
# @pytest.mark.assembler
# def test_assembler_multiple_word_commands(tmp_path):
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     command = ""

#     command += generate_random_command()
#     command += generate_random_command()
#     command += generate_random_command()
#     command += generate_word_command(0x30, 45)
#     command += generate_random_command()
#     # TODO: Does not work when changing 300 and 301
#     command += generate_word_command(300, 100)
#     command += generate_word_command(301, 101)
#     command += generate_word_command(302, 102)
#     command += generate_word_command(303, 103)
#     command += generate_word_command(304, 104)


#     runner.set_input_data_from_str(command)
#     print(command)
#     runner.run()


# def random_command_generation(tmp_path, number_of_commands):
#     commands = []

#     # Taking only a single label in order to prvent 2 lables after each other
#     labels_names = [utils.get_random_string(x) for x in range(1, 2)]
#     for label_name in labels_names:
#         commands.append(f"{label_name}:\n")
#         number_of_commands -=1

#     for _ in range(number_of_commands//3):
#         commands.append(generate_random_command_with_label(random.choice(labels_names)))
#         number_of_commands -= 1

#     for _ in range(number_of_commands):
#         commands.append(generate_random_command())
#         number_of_commands -= 1

#     # TODO: Add words as well after fixing bugs over there

#     random.shuffle(commands)
#     command = "".join(commands)
#     runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
#     runner.set_input_data_from_str(command)
#     print(command)
#     runner.run()


# @pytest.mark.sanity
# @pytest.mark.assembler
# @pytest.mark.parametrize("number_of_commands", [5, 100, 300])
# def test_assembler_random_command_generation(tmp_path, number_of_commands):
#     random_command_generation(tmp_path, number_of_commands)

# @pytest.mark.stress
# @pytest.mark.assembler
# @pytest.mark.parametrize("number_of_commands", [x for x in range(5, 1000)])
# @pytest.mark.parametrize("iter_number", [x for x in range(5)])
# def test_assembler_random_command_generation_stress(tmp_path, number_of_commands, iter_number):
#     random_command_generation(tmp_path, number_of_commands)
