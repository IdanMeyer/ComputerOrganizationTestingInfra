import pytest
from Infra.assembler_wrapper import AssemblerTestRunner, AssemblyLine

ASSEMBLER_PATH = "<assembler_path>"
def test_assembler_sanity():
    runner = AssemblerTestRunner(ASSEMBLER_PATH)
    # a = AssemblyLine("L1: sub $t0, $t2, $t1, 0")
    # a = AssemblyLine("L2: mul $t0, $t2, $t1, 0")
    # print(a)
