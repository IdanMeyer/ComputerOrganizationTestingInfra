import pytest
import pathlib
import random
import os

from Infra.assembler_wrapper import AssemblerTestRunner, AssemblyLine, PythonAssemblerTestRunner, OPCODE_TO_NUMBER, REGISTER_TO_NUMBER
from Infra import utils
from Infra.simulator_wrapper import SimulatorTestRunner


ASSEMBLER_PATH = "../ComputerOrganizationProcessor/build/assembler"
SIMULATOR_PATH = "../ComputerOrganizationProcessor/build/simulator"
# ASSEMBLER_PATH = r"..\ComputerOrganizationProcessor\VisualStudio\Assembler\x64\Debug\Assembler.exe"
# SIMULATOR_PATH = r"..\ComputerOrganizationProcessor\VisualStudio\Simulator\x64\Debug\Simulator.exe"

TESTS_BASE_FOLDER = pathlib.Path(__file__).parent.resolve()
NUMBER_OF_BITS_IN_REGISTER = 32


@pytest.mark.sanity
@pytest.mark.simulator
def test_simulator_halt(tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str("halt $zero, $zero, $zero, 0")
    runner.run({"$v0":0})
    runner.validate_all_regs_zero()

@pytest.mark.sanity
@pytest.mark.simulator
def test_simulator_add_sanity(tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = os.linesep.join([
        "add $t0, $zero, $imm, 10",
        "add $t1, $zero, $imm, -1",
        "add $t2, $zero, $imm, -78",
        "add $s0, $imm, $zero, 0xfff",
        "add $s1, $zero, $imm, -0x100",
        "add $s2, $zero, $imm, 0x70",
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":10, "$t1":-1,  "$t2":-78, "$s0":0xfff, "$s1":-0x100,"$s2":0x70})


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


@pytest.mark.simulator
@pytest.mark.sanity
@pytest.mark.parametrize("address", range(10, 14))
def test_simulator_word_command_and_lw_hex(address, tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    data = "0xaa"
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {address}",
        f"lw $t2, $t0, $zero, 0",
        "halt $zero, $zero, $zero, 0",
        f".word {address} {data}"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":address, "$t2":int(data, 16)})


@pytest.mark.simulator
@pytest.mark.sanity
@pytest.mark.parametrize("address", range(10, 14))
def test_simulator_word_command_and_lw_int(address, tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    data = "55"
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {address}",
        f"lw $t2, $t0, $zero, 0",
        "halt $zero, $zero, $zero, 0",
        f".word {address} {data}"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":address, "$t2":int(data, 10)})


@pytest.mark.simulator
@pytest.mark.stress
@pytest.mark.parametrize("address", range(6, 2048))
def test_simulator_word_command_and_lw_hex_stress(address, tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    data = "0xaa"
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {address}",
        f"lw $t2, $t0, $zero, 0",
        "halt $zero, $zero, $zero, 0",
        f".word {address} {data}"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":address, "$t2":int(data, 16)})

@pytest.mark.simulator
@pytest.mark.stress
@pytest.mark.parametrize("address", range(6, 2048))
def test_simulator_word_command_and_lw_int_stress(address, tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    data = address%3+35
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {address}",
        f"lw $t2, $t0, $zero, 0",
        "halt $zero, $zero, $zero, 0",
        f".word {address} {data}"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":address, "$t2":data})


@pytest.mark.simulator
@pytest.mark.sanity
@pytest.mark.parametrize("value_1", [5,6])
@pytest.mark.parametrize("value_2", [5,6])
def test_simulator_beq_sanity(value_1, value_2, tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())

    is_equal = int(value_1 == value_2)
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {value_1}",
        f"add $t1, $zero, $imm, {value_2}",
        f"add $t2, $zero, $imm, 1",
        f"beq $imm, $t0, $t1, Exit",
        f"add $t2, $zero, $imm, 0",
        f"Exit:",
        f"halt $zero, $zero, $zero, 0",
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":value_1, "$t1":value_2, "$t2":is_equal})

@pytest.mark.simulator
@pytest.mark.sanity
@pytest.mark.parametrize("value_1", [5,6])
@pytest.mark.parametrize("value_2", [5,6])
def test_simulator_bne_sanity(value_1, value_2, tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())

    is_equal = int(value_1 == value_2)
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {value_1}",
        f"add $t1, $zero, $imm, {value_2}",
        f"add $t2, $zero, $imm, 1",
        f"bne $imm, $t0, $t1, Exit",
        f"add $t2, $zero, $imm, 0",
        f"Exit:",
        f"halt $zero, $zero, $zero, 0",
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":value_1, "$t1":value_2, "$t2":not is_equal})


@pytest.mark.simulator
@pytest.mark.sanity
@pytest.mark.parametrize("value_1", [5])
@pytest.mark.parametrize("value_2", [5])
def test_simulator_jal_sanity(value_1, value_2, tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())

    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {value_1}",
        f"add $t1, $zero, $imm, {value_2}",
        f"add $t2, $zero, $imm, 1",
        f"jal $ra, $imm, $zero, Exit",
        f"add $t2, $zero, $imm, 0",
        f"Exit:",
        f"halt $zero, $zero, $zero, 0",
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":value_1, "$t1":value_2, "$t2":1, "$ra":8})
