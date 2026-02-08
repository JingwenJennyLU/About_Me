'''
Polling places: test code for simulate_election_day
'''

import csv
import pytest
from util_tests import run_simulate_test

# DO NOT REMOVE THESE LINES OF CODE
# pylint: disable-msg= invalid-name, missing-docstring, too-many-arguments, line-too-long
# pylint: disable-msg= missing-docstring, too-many-locals, unused-argument


precinct_files = ["precinct-0.json",
                  "precinct-1.json",
                  "precinct-2.json",
                  "precinct-3.json",
                  "precinct-4.json",
                  "precinct-5.json",
                  "precinct-6.json",
                  "precinct-7.json"]

def make_test_parameters():
    # 1000 minutes is longer than any of the precincts are open
    # even the most impatient person will stay to vote.

    # A threshold of 0 means that an voter impatient voter will leave
    # unless a machine is open when they walk in the door

    impatience_thresholds = [1000, 20, 5, 1, 0]
    booth_counts = [1, 2, 5]

    test_parameters = []
    for p in precinct_files:
        for nb in booth_counts:
            for imp_thresh in impatience_thresholds:
                test_parameters.append((p, nb, imp_thresh))

    # add test cases for the largest precinct.
    large_precinct = "precinct-3.json"
    for nb in [50, 100, 500]:
        for imp_thresh in impatience_thresholds:
            test_parameters.append((p, nb, imp_thresh))

    return test_parameters

DATA_DIR = "./data/"

@pytest.mark.parametrize(("config_file", "num_booths", "impatience_threshold"), make_test_parameters())
def test_simulate(config_file, num_booths, impatience_threshold):
    run_simulate_test(DATA_DIR + config_file, num_booths, impatience_threshold, check_start = True)
    


