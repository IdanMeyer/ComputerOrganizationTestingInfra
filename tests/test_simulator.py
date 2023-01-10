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
SECTOR_SIZE = 128
NUMBER_OF_SECTORS = 128


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
        "add $s0, $imm, $zero, 0xffff",
        "add $s1, $zero, $imm, -0x100",
        "add $s2, $zero, $imm, 0x70",
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":10, "$t1":-1,  "$t2":-78, "$s0":0xffff, "$s1":-0x100,"$s2":0x70})


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
@pytest.mark.parametrize("value_1", [5,6])
@pytest.mark.parametrize("value_2", [5,6])
def test_simulator_blt_sanity(value_1, value_2, tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())

    is_less_then = int(value_1 < value_2)
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {value_1}",
        f"add $t1, $zero, $imm, {value_2}",
        f"add $t2, $zero, $imm, 1",
        f"blt $imm, $t0, $t1, Exit",
        f"add $t2, $zero, $imm, 0",
        f"Exit:",
        f"halt $zero, $zero, $zero, 0",
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":value_1, "$t1":value_2, "$t2":is_less_then})


@pytest.mark.simulator
@pytest.mark.sanity
@pytest.mark.parametrize("value_1", [5,6])
@pytest.mark.parametrize("value_2", [5,6])
def test_simulator_bgt_sanity(value_1, value_2, tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())

    is_greater_then = int(value_1 > value_2)
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {value_1}",
        f"add $t1, $zero, $imm, {value_2}",
        f"add $t2, $zero, $imm, 1",
        f"bgt $imm, $t0, $t1, Exit",
        f"add $t2, $zero, $imm, 0",
        f"Exit:",
        f"halt $zero, $zero, $zero, 0",
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":value_1, "$t1":value_2, "$t2":is_greater_then})

@pytest.mark.simulator
@pytest.mark.sanity
@pytest.mark.parametrize("value_1", [5,6])
@pytest.mark.parametrize("value_2", [5,6])
def test_simulator_ble_sanity(value_1, value_2, tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())

    is_less_then = int(value_1 <= value_2)
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {value_1}",
        f"add $t1, $zero, $imm, {value_2}",
        f"add $t2, $zero, $imm, 1",
        f"ble $imm, $t0, $t1, Exit",
        f"add $t2, $zero, $imm, 0",
        f"Exit:",
        f"halt $zero, $zero, $zero, 0",
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":value_1, "$t1":value_2, "$t2":is_less_then})


@pytest.mark.simulator
@pytest.mark.sanity
@pytest.mark.parametrize("value_1", [5,6])
@pytest.mark.parametrize("value_2", [5,6])
def test_simulator_bge_sanity(value_1, value_2, tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())

    is_greater_then = int(value_1 >= value_2)
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {value_1}",
        f"add $t1, $zero, $imm, {value_2}",
        f"add $t2, $zero, $imm, 1",
        f"bge $imm, $t0, $t1, Exit",
        f"add $t2, $zero, $imm, 0",
        f"Exit:",
        f"halt $zero, $zero, $zero, 0",
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":value_1, "$t1":value_2, "$t2":is_greater_then})


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

def add_overflow(a,b,num_bits):
    rangeMax = 2**(num_bits-1)
    result = a + b
    if result >= rangeMax:
        return int((result) % rangeMax)
    else:
        return result

@pytest.mark.stress
@pytest.mark.simulator
@pytest.mark.parametrize("iter_number", range(100))
def test_simulator_add_stress(tmp_path, iter_number):
    number_1 = random.randint(-2**17, +2**17)
    number_2 = random.randint(-2**17, +2**17)

    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {number_1}",
        f"add $t1, $zero, $imm, {number_2}",
        f"add $t2, $t0, $t1, 0",
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":number_1, "$t1":number_2,  "$t2":add_overflow(number_1, number_2, 20)})

@pytest.mark.stress
@pytest.mark.simulator
@pytest.mark.parametrize("iter_number", range(100))
def test_simulator_sub_stress(tmp_path, iter_number):
    number_1 = random.randint(-2**17, +2**17)
    number_2 = random.randint(-2**17, +2**17)

    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = os.linesep.join([
        f"add $t0, $zero, $imm, {number_1}",
        f"add $t1, $zero, $imm, {number_2}",
        f"sub $t2, $t0, $t1, 0",
        "halt $zero, $zero, $zero, 0"
                                 ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$t0":number_1, "$t1":number_2,  "$t2":add_overflow(number_1, -number_2, 20)})


def disk_read(tmp_path, ram_buffer_address, sector):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    diskin_data = runner.generate_random_diskin_data()
    asm_input = f"""add $s0, $zero, $zero, 0 # Initialize s0 to zero
    add $t0, $zero, $imm, 6
    out $imm, $zero, $t0, IRQ_HANDLER # enable irq handler
    add $t0, $zero, $imm, 1
    out $imm, $zero, $t0, 1 # enable irq1
    add $t0, $zero, $imm, 15
    out $imm, $zero, $t0, {sector} # enable disk sector {sector}
    add $t0, $zero, $imm, 16
    out $imm, $zero, $t0, {ram_buffer_address} # enable disk buffer 0
    add $t0, $zero, $imm, 14
    out $imm, $zero, $t0, 1 # enable disk cmd for read
L1:
	beq $imm, $s0,$zero,L1 # stay here till last write
	halt $zero, $zero, $zero, 0 # will reach here when done
IRQ_HANDLER:
    add $s0, $zero, $imm, 1
    reti $zero, $zero, $zero, 0 #return from irq call"""
    runner.set_input_data_from_str(asm_input)
    runner.run()
    memout = runner.read_memout()
    for i in range(SECTOR_SIZE):
        assert diskin_data[SECTOR_SIZE*sector+i].upper() == memout[ram_buffer_address+i]


@pytest.mark.sanity
@pytest.mark.simulator
@pytest.mark.parametrize("base_address", [0x100])
@pytest.mark.parametrize("sector", [0,2])
def test_simulator_disk_read_sanity(tmp_path, base_address, sector):
    disk_read(tmp_path, base_address, sector)


@pytest.mark.stress
@pytest.mark.simulator
@pytest.mark.parametrize("base_address", [0x100, 0x273])
@pytest.mark.parametrize("sector", range(0, NUMBER_OF_SECTORS))
def test_simulator_disk_read_stress(tmp_path, base_address, sector):
    disk_read(tmp_path, base_address, sector)


def disk_write(tmp_path, ram_buffer_address, sector):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    asm_input = f"""add $s0, $zero, $zero, 0 # Initialize s0 to zero
    add $t0, $zero, $imm, 6
    out $imm, $zero, $t0, IRQ_HANDLER # enable irq handler
    add $t0, $zero, $imm, 1
    out $imm, $zero, $t0, 1 # enable irq1
    add $t0, $zero, $imm, 15
    out $imm, $zero, $t0, {sector} # enable disk sector 0
    add $t0, $zero, $imm, 16
    out $imm, $zero, $t0, {ram_buffer_address} # enable disk buffer 0
    add $t0, $zero, $imm, 14
    out $imm, $zero, $t0, 2 # enable disk cmd for write
L1:
	beq $imm, $s0,$zero,L1 # stay here till last write
	halt $zero, $zero, $zero, 0 # will reach here when done
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
    add $t0, $zero, $imm, 6 ## Adding command just for more data
IRQ_HANDLER:
    add $s0, $zero, $imm, 1
    reti $zero, $zero, $zero, 0 #return from irq call"""
    runner.set_input_data_from_str(asm_input)
    runner.run()
    diskout = runner.read_diskout()
    memin = runner.read_memin()

    for i in range(SECTOR_SIZE):
        if ram_buffer_address + i < len(memin):
            assert diskout[SECTOR_SIZE*sector+i] == memin[ram_buffer_address+i].upper()
        else:
            assert diskout[SECTOR_SIZE*sector+i] == b'00000'

@pytest.mark.sanity
@pytest.mark.simulator
@pytest.mark.parametrize("base_address", [0])
@pytest.mark.parametrize("sector", [0,2])
def test_simulator_disk_write_sanity(tmp_path, base_address, sector):
    disk_write(tmp_path, base_address, sector)


@pytest.mark.stress
@pytest.mark.simulator
@pytest.mark.parametrize("base_address", [0, 0x30])
@pytest.mark.parametrize("sector", range(SECTOR_SIZE))
def test_simulator_disk_write_stress(tmp_path, base_address, sector):
    disk_write(tmp_path, base_address, sector)


# TODO: When writing 0x000ffff it is auto-completed to ffffffff (because of 1s complement). Is it OK?
@pytest.mark.sanity
@pytest.mark.simulator
@pytest.mark.parametrize("value", [0x00005678, 0x0000aaaa, 1, 2, 3, 4])
def test_simulator_leds_sanity(tmp_path, value):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    led_states = [0x0000bbcc, value, value<<1, value<<2, value<<3, value<<4]
    asm_input = os.linesep.join([
        f"in $t1, $zero, $imm, 9",
        f"add $t1, $zero, $imm, {led_states[0]}",
        f"out $t1, $zero, $imm, 9",
        f"add $t1, $zero, $imm, {led_states[1]}",
        f"out $t1, $zero, $imm, 9",
        f"sll $t1, $t1, $imm, 1",
        f"out $t1, $zero, $imm, 9",
        f"sll $t1, $t1, $imm, 1",
        f"out $t1, $zero, $imm, 9",
        f"sll $t1, $t1, $imm, 1",
        f"out $t1, $zero, $imm, 9",
        f"sll $t1, $t1, $imm, 1",
        f"out $t1, $zero, $imm, 9",
        f"sll $t1, $t1, $imm, 1",
        f"out $t1, $zero, $imm, 9",
        "halt $zero, $zero, $zero, 0"])

    runner.set_input_data_from_str(asm_input)
    runner.run()
    leds = runner.read_leds()
    for i, _ in enumerate(led_states):
        assert int(leds[i], 16) == led_states[i]


@pytest.mark.sanity
@pytest.mark.simulator
@pytest.mark.parametrize("value", [0x00005678, 0x0000aaaa, 1, 2, 3, 4])
def test_simulator_display_7_seg_sanity(tmp_path, value):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    display7seg_states = [0x0000bbcc, value, value<<1, value<<2, value<<3, value<<4]
    asm_input = os.linesep.join([
        f"in $t1, $zero, $imm, 10",
        f"add $t1, $zero, $imm, {display7seg_states[0]}",
        f"out $t1, $zero, $imm, 10",
        f"add $t1, $zero, $imm, {display7seg_states[1]}",
        f"out $t1, $zero, $imm, 10",
        f"sll $t1, $t1, $imm, 1",
        f"out $t1, $zero, $imm, 10",
        f"sll $t1, $t1, $imm, 1",
        f"out $t1, $zero, $imm, 10",
        f"sll $t1, $t1, $imm, 1",
        f"out $t1, $zero, $imm, 10",
        f"sll $t1, $t1, $imm, 1",
        f"out $t1, $zero, $imm, 10",
        f"sll $t1, $t1, $imm, 1",
        f"out $t1, $zero, $imm, 10",
        "halt $zero, $zero, $zero, 10"])

    runner.set_input_data_from_str(asm_input)
    runner.run()
    display7seg = runner.read_display7seg()
    for i, _ in enumerate(display7seg_states):
        assert int(display7seg[i], 16) == display7seg_states[i]


@pytest.mark.sanity
@pytest.mark.simulator
@pytest.mark.parametrize("timer_time", [50, 70, 5000])
@pytest.mark.parametrize("sleep_iter", [200, 800])
def test_simulator_timer_sanity(tmp_path, sleep_iter, timer_time):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    # Very "far" numbers were chosen as we did no calulate exactly how many cycles pass
    # between the start of the timer and the sleep.
    expected_a2 =  int(timer_time < sleep_iter/2)
    asm_input = os.linesep.join([
        f"add $t2, $zero, $imm,  {timer_time} # set timer",
        "out $t2, $zero, $imm, 13 # write to timermax",
        "add $t2, $zero, $imm, L4 # $t1 = address of L4",
        "out $t2, $zero, $imm, 6 # set irqhandler as L4",
        "out $imm, $zero, $zero, 1	     	# enable irq0",
        "add $t2, $zero, $imm, 1",
        "out $t2, $zero, $imm, 11 # enable tiemrenable",

        "add $t0, $zero, $zero, 0",
        f"add $t1, $zero, $imm, {sleep_iter}",
        "L1: # Loop for long exeuction time",
        "add $t0, $t0, $imm, 1",
        "blt $imm, $t0,$t1,L1",
        "halt $zero, $zero, $zero, 0",
        "L4:",
        "out $zero, $zero, $imm, 3			# clear irq0 status",
        "add $t2, $zero, $imm, 0",
        "out $t2, $zero, $imm, 11 # disable tiemrenable",
        "add $a2, $a2, $imm, 1				# save argument",
        "reti $zero, $zero, $zero, 0			# return from interrupt",
    ])
    runner.set_input_data_from_str(asm_input)
    runner.run({"$a2":expected_a2})


@pytest.mark.sanity
@pytest.mark.simulator
def test_simulator_compare_example_fib(tmp_path):
    runner = SimulatorTestRunner(ASSEMBLER_PATH, SIMULATOR_PATH, tmp_path.as_posix())
    example_fib_dir = os.path.join(TESTS_BASE_FOLDER, "..", "files", "fibexample_300422_win")
    example_fib_asm = os.path.join(example_fib_dir, "fib.asm")
    runner.set_input_data_from_file(example_fib_asm)
    runner.copy_irq2_to_test_folder(os.path.join(example_fib_dir, "irq2in.txt"))
    runner.copy_diskin_to_test_folder(os.path.join(example_fib_dir, "diskin.txt"))
    runner.run()
    runner.compare_directories(example_fib_dir)
