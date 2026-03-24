'''
Polling places: test code for avg_wait_time
'''

import csv
import pytest
import util
import sys
import os
import util_tests as ut

# Handle the fact that the grading code may not
# be in the same directory as implementation
sys.path.insert(0, os.getcwd())

# DO NOT MODIFY THIS FILE
# pylint: disable-msg= invalid-name, missing-docstring


DATA_DIR = "./data/"

with open(DATA_DIR + "impatience_threshold.csv") as f:
    reader = csv.DictReader(f)

    configs = []
    slow_configs = []
    for row in reader:
        config = (row["config_file"],
                  int(row["num_booths"]),
                  int(row["num_trials"]),
                  int(row["expected"]))
        if "precinct-3" in row["config_file"]:
            slow_configs.append(config)
        else:
            configs.append(config)


def run_test(precinct_file, num_booths, num_trials, expected):
    actual = ut.run_threshold_test(precinct_file, num_booths, num_trials)

    recreate_msg = "\nTo recreate this test run:\n"
    recreate_msg += "    util_tests.run_threshold_test({}, {}, {})"
    recreate_msg = recreate_msg.format(precinct_file, num_booths, num_trials)

    ut.check_none(actual, recreate_msg)
    ut.check_type(actual, expected, recreate_msg)
    ut.check_equals(actual, expected, recreate_msg)

@pytest.mark.parametrize("precinct_file, num_booths, num_trials, expected", configs)
def test_simulate(precinct_file, num_booths, num_trials, expected):
    run_test(DATA_DIR + precinct_file, num_booths, num_trials, expected)


@pytest.mark.slow
@pytest.mark.parametrize("precinct_file, num_booths, num_trials, expected", slow_configs)
def test_simulate_slow(precinct_file, num_booths, num_trials, expected):
    run_test(DATA_DIR + precinct_file, num_booths, num_trials, expected)
    
