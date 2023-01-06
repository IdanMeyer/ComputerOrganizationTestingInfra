import os

from Infra.assembler_wrapper import REGISTER_TO_NUMBER, AssemblerTestRunner

class SimulatorException(Exception):
    pass

class SimulatorTestRunner(object):
    def __init__(self, assembler_path, simulator_path, test_folder, should_compile=False):
        self.assembler_runner = AssemblerTestRunner(assembler_path, test_folder, should_compile=should_compile)
        self.c_simulator_path = os.path.realpath(simulator_path)
        self.input_data = None
        self.expected_output = None
        self.test_folder = test_folder
        self.test_asm_path = os.path.join(self.test_folder, "test.asm")
        self.memin_txt_path = os.path.join(self.test_folder, "memin.txt")
        self.memout_txt_path = os.path.join(self.test_folder, "memout.txt")
        self.regout_txt_path = os.path.join(self.test_folder, "regout.txt")
        self.trace_txt_path = os.path.join(self.test_folder, "trace.txt")
        self.cycles_txt_path = os.path.join(self.test_folder, "cycles.txt")

    def set_input_data_from_str(self, input_data):
        self.assembler_runner.set_input_data_from_str(input_data)

    def set_input_data_from_file(self, file_path):
        self.assembler_runner.set_input_data_from_file(file_path)

    def run(self, regs_to_validate=None):
        c_assembler_output = self.assembler_runner.execute_c_assembler(
            self.test_asm_path,
            self.memin_txt_path)

        self.execute_c_simulator()
        self._validate_regs(regs_to_validate)

    def _validate_regs(self, regs_to_validate):
        if regs_to_validate is None:
            return

        with open(self.regout_txt_path, "rb") as f:
            register_values = f.read().splitlines()

        for reg, expected_value in regs_to_validate.items():
            reg_index = REGISTER_TO_NUMBER[reg]
            if reg_index == 0 or reg_index == 1:
                raise SimulatorException("Cannot validate registers $zero or $imm because they are not saved at reg.txt")
            actual_reg_value = register_values[reg_index-2]
            print(f"Validating register {reg}. expected: {expected_value}, actual: {actual_reg_value}")
            int_actual_reg_value = int(actual_reg_value, 16)
            if int_actual_reg_value >= 2**31:
                int_actual_reg_value -= 2**32
            assert int_actual_reg_value == expected_value

    def validate_all_regs_zero(self):
        self._validate_regs({key : 0 for key, value in REGISTER_TO_NUMBER.items() if value >=2})

    def execute_c_simulator(self):
        cmd_args = [self.memin_txt_path, self.memout_txt_path, self.regout_txt_path,
                    self.trace_txt_path, self.cycles_txt_path]
        command = ["cd", self.test_folder, "&&", self.c_simulator_path] + cmd_args
        # TODO: change this to use Popen instead of os.system
        result = os.system(" ".join(command))
        if result != 0:
            raise SimulatorException(f"C simulator failed")


        # Return output from memout
        with open(self.memout_txt_path, "r") as f:
            memout_data =  f.read()
        return memout_data
