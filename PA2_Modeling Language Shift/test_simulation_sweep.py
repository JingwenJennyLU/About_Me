"""
MACS 30121: Language shifts

Test code for the simulation_sweep function.
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

from language import simulation_sweep
import test_helpers
import utility

def helper_test_simulation_sweep(input_filename, R, A, Bs, C, max_steps, expected_frequencies):
    """
    Do one simulation with the specified parameters and
      match the actual frequencies with expected frequencies
    
    Inputs:
      input_filename (string): the grid file
      R (int): neighborhood radius
      A (float): the language state transition threshold A
      Bs (list of floats): a list of the transition thresholds B to
        use in the simulation
      C (float): the language state transition threshold C
      centers (list of tuples): a list of community centers in the
        region
      max_steps (int): maximum number of steps
      expected_frequencies (list of tuples): the expected frequencies
    """

    input_filename = os.path.join(TEST_DIR, input_filename)
    actual_grid, centers = utility.read_grid(input_filename)
    actual_frequencies = simulation_sweep(actual_grid, R, A, Bs, C, centers, max_steps)
    
    recreate_msg = "To recreate this test in ipython3 run:\n"
    recreate_msg += "    region, centers = utility.read_grid('{}')\n"
    recreate_msg += "    Bs = {}\n"
    recreate_msg += "    language.simulation_sweep(region, {}, {}, Bs, {}, centers, {})"
    recreate_msg = recreate_msg.format(input_filename, Bs, R, A, C, max_steps)

    if len(actual_frequencies) != len(expected_frequencies):
        msg = "Actual and expected number of frequencies don't match.\n"
        msg += "    actual: {}\n"
        msg += "    expected: {}\n"
        msg = msg.format(len(actual_frequencies), len(expected_frequencies))
        msg = msg + "\n" + recreate_msg
        pytest.fail(msg)

    for i, freq in enumerate(actual_frequencies):
        if freq != expected_frequencies[i]:
            msg = "Actual and expected frequencies don't match for B = {}.\n"
            msg += "    actual: {}\n"
            msg += "    expected: {}\n"
            msg = msg.format(Bs[i], freq, expected_frequencies[i])
            msg = msg + "\n" + recreate_msg
            pytest.fail(msg)

def test_simulation_sweep_1():
    input_filename = 'writeup-grid.txt'
    R = 1
    A = 0.6
    Bs = [0.6, 0.8, 1.0, 1.2, 1.4]
    C = 1.6
    max_steps = 1
    expected_frequencies =  [(5, 14, 6), (11, 9, 5), (15, 6, 4), (19, 6, 0), (19, 6, 0)]
    helper_test_simulation_sweep(input_filename, R, A, Bs, C, max_steps, expected_frequencies)

def test_simulation_sweep_2():
    input_filename = 'writeup-grid.txt'
    R = 1
    A = 0.6
    Bs = [0.6, 0.8, 1.0, 1.2, 1.4]
    C = 1.6
    max_steps = 5
    expected_frequencies =  [(3, 16, 6), (12, 8, 5), (25, 0, 0), (25, 0, 0), (25, 0, 0)]
    helper_test_simulation_sweep(input_filename, R, A, Bs, C, max_steps, expected_frequencies)

def test_simulation_sweep_3():
    input_filename = 'writeup-grid.txt'
    R = 2
    A = 0.6
    Bs = [0.6, 0.8, 1.0, 1.2, 1.4]
    C = 1.6
    max_steps = 1
    expected_frequencies =  [(1, 18, 6), (1, 18, 6), (21, 4, 0), (21, 4, 0), (21, 4, 0)]
    helper_test_simulation_sweep(input_filename, R, A, Bs, C, max_steps, expected_frequencies)

def test_simulation_sweep_4():
    input_filename = 'writeup-grid-with-cc.txt'
    R = 1
    A = 0.6
    Bs = [0.6, 0.8, 1.0, 1.2, 1.4]
    C = 1.6
    max_steps = 1
    expected_frequencies =  [(3, 16, 6), (5, 14, 6), (12, 8, 5), (13, 7, 5), (15, 7, 3)]
    helper_test_simulation_sweep(input_filename, R, A, Bs, C, max_steps, expected_frequencies)

def test_simulation_sweep_5():
    input_filename = 'writeup-grid-with-cc.txt'
    R = 1
    A = 0.6
    Bs = [0.6, 0.8, 1.0, 1.2, 1.4]
    C = 1.6
    max_steps = 5
    expected_frequencies =  [(3, 16, 6), (3, 16, 6), (14, 6, 5), (18, 4, 3), (18, 4, 3)]
    helper_test_simulation_sweep(input_filename, R, A, Bs, C, max_steps, expected_frequencies)

def test_simulation_sweep_6():
    input_filename = 'writeup-grid-with-cc.txt'
    R = 2
    A = 0.6
    Bs = [0.6, 0.8, 1.0, 1.2, 1.4]
    C = 1.6
    max_steps = 1
    expected_frequencies =  [(1, 18, 6), (1, 18, 6), (11, 9, 5), (15, 7, 3), (15, 7, 3)]
    helper_test_simulation_sweep(input_filename, R, A, Bs, C, max_steps, expected_frequencies)

def test_simulation_sweep_7():
    input_filename = 'medium-grid.txt'
    R = 1
    A = 0.6
    Bs = [0.6, 0.8, 1.0, 1.2, 1.4]
    C = 1.6
    max_steps = 5
    expected_frequencies =  [(6, 54, 40), (20, 42, 38), (68, 12, 20), (86, 3, 11), (87, 2, 11)]
    helper_test_simulation_sweep(input_filename, R, A, Bs, C, max_steps, expected_frequencies)

def test_simulation_sweep_8():
    input_filename = 'medium-grid.txt'
    R = 2
    A = 0.6
    Bs = [0.6, 0.8, 1.0, 1.2, 1.4]
    C = 1.6
    max_steps = 5
    expected_frequencies =  [(0, 67, 33), (12, 56, 32), (83, 6, 11), (87, 2, 11), (87, 2, 11)]
    helper_test_simulation_sweep(input_filename, R, A, Bs, C, max_steps, expected_frequencies)

def test_simulation_sweep_9():
    input_filename = 'large-grid.txt'
    R = 3
    A = 0.6
    Bs = [0.6, 0.8, 1.0, 1.2, 1.4]
    C = 1.6
    max_steps = 5
    expected_frequencies =  [(0, 1024, 576), (0, 1025, 575), (739, 537, 324), (1496, 55, 49), (1497, 54, 49)]
    helper_test_simulation_sweep(input_filename, R, A, Bs, C, max_steps, expected_frequencies)

def test_simulation_sweep_10():
    input_filename = 'large-grid.txt'
    R = 4
    A = 0.6
    Bs = [0.6, 0.8, 1.0, 1.2, 1.4]
    C = 1.6
    max_steps = 5
    expected_frequencies =  [(0, 1025, 575), (0, 1026, 574), (477, 714, 409), (1496, 55, 49), (1497, 54, 49)]
    helper_test_simulation_sweep(input_filename, R, A, Bs, C, max_steps, expected_frequencies)
