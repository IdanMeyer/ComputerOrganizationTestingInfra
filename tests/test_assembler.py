import pytest
import pathlib
from Infra.assembler_wrapper import AssemblerTestRunner, AssemblyLine, PythonAssemblerTestRunner

# ASSEMBLER_PATH = "<assembler_path>"
ASSEMBLER_PATH = "~/tmp/exec3"

TESTS_BASE_FOLDER = pathlib.Path(__file__).parent.resolve()

def test_python_assembler():
    runner = PythonAssemblerTestRunner(ASSEMBLER_PATH)
    runner.set_input_data_from_file(f"{TESTS_BASE_FOLDER}/resources/fib.asm")
    runner.set_expected_output_from_file(f"{TESTS_BASE_FOLDER}/resources/memin.txt")
    runner.run()

def test_assembler_sanity_compare_from_python(tmp_path):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str("halt $zero, $zero, $zero, 0")
    runner.run()

def test_assembler_sanity_custom_expected_output(tmp_path):
    runner = AssemblerTestRunner(ASSEMBLER_PATH, tmp_path.as_posix())
    runner.set_input_data_from_str("halt $zero, $zero, $zero, 0")
    runner.set_expected_output("15000\n")
    runner.run()
