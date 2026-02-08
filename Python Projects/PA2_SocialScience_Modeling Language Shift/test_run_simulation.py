"""
MACS 30121: Language shifts

Test code for the run_simulation function.
"""

import os
import sys
import pytest

BASE_DIR = os.path.dirname(__file__)
TEST_DIR = os.path.join(BASE_DIR, "tests")

timeout = 60

# Handle the fact that the grading code may not
# be in the same directory as schelling.py
sys.path.insert(0, os.getcwd())

# Get the test files from the same directory as
# this file.
BASE_DIR = os.path.dirname(__file__)

# Keep pylint from complaining about generated code.
#pylint: disable-msg=wrong-import-position
#pylint: disable-msg=missing-docstring

from language import run_simulation
import test_helpers
import utility

def helper_test_run_simulation(params):
    """
    Do one simulation with the specified parameters and
      match the actual grid with the expected grid
    
    Inputs:
      params (dictionary): simulation parameters
    """

    input_filename = os.path.join(TEST_DIR, params["input_filename"])
    R = params["R"]
    thresholds = tuple(params["thresholds"])
    max_steps = params["max_steps"]

    actual_grid, centers = utility.read_grid(input_filename)
    actual_frequency = run_simulation(actual_grid, R, thresholds, centers, max_steps)
    
    expected_filename = params["expected_filename"]
    expected_grid, centers = utility.read_grid(expected_filename)

    recreate_msg = "To recreate this test in ipython3 run:\n"
    recreate_msg += "    region, centers = utility.read_grid('{}')\n"
    recreate_msg += "    language.run_simulation(region, {}, {}, centers, {})"
    recreate_msg = recreate_msg.format(input_filename, R, thresholds, max_steps)

    difference = utility.find_difference(actual_grid, expected_grid)
    if difference:
        (i, j) = difference
        msg = "Actual and expected grids don't match.\n"
        msg += "    At location: ({}, {})\n"
        msg += "      actual: {}\n"
        msg += "      expected: {}\n"
        msg = msg.format(i, j, actual_grid[i][j], expected_grid[i][j])
        msg = msg + "\n" + recreate_msg
        pytest.fail(msg)

@pytest.mark.parametrize(
    "params",
    test_helpers.read_config_file("test_run_simulation_small.json"))
def test_run_simulation_small(params):
    helper_test_run_simulation(params)

@pytest.mark.parametrize(
    "params",
    test_helpers.read_config_file("test_run_simulation_medium.json"))
def test_run_simulation_medium(params):
    helper_test_run_simulation(params)

@pytest.mark.parametrize(
    "params",
    test_helpers.read_config_file("test_run_simulation_large.json"))
def test_run_simulation_large(params):
    helper_test_run_simulation(params)
