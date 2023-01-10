# ComputerOrganizationTestingInfra

## Description
Tests for Computer organization course at TAU.

## Getting Started
* Clone the repository.
* Install `python3`, `pip`, and `pytest`.
* Edit ASSEMBLER_PATH  and SIMULATOR_PATH at tests/test_assembler.py and tests/test_simulator.py
* Executing tests via terminal (cmd or bash) from the root of this repo:
```
python3 -m pytest test_simulator <path_to_test_file>
```
* For example:
```
python3 -m pytest test_simulator.py
```


### Notes
**Usefull pytest flags:**
* `-s` - Show prints to stdout even if the tests pass.
* `-x` - Stop execution after the first failure (by default, all tests are executed).
* `-k` - Filter tests to execute by keyword.
* `-m` - Execute only a specific mark. For example sanity or stress.

**This is how I usally execute the tests: (from the main directory of this repo)**
```
python3 -m pytest tests/test_simulator.py -m sanity
```


### Dependencies
* python3 - Can be installed from: https://www.python.org/downloads/
* pip -Installation instructions: https://pip.pypa.io/en/stable/cli/pip_install/
* pytest - Can be installed from: https://docs.pytest.org/en/7.2.x/getting-started.html#get-started
