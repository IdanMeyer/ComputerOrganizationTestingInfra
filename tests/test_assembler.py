import pytest
from Infra.assembler_wrapper import AssemblerTestRunner, AssemblyLine

ASSEMBLER_PATH = "<assembler_path>"
def test_assembler_sanity():
    runner = AssemblerTestRunner(ASSEMBLER_PATH)
