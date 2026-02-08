'''
Polling places: test code for simulate_election_day
'''

import pytest
from util_tests import run_simulate_test

# DO NOT MODIFY THIS FILE
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

DATA_DIR = "./data/"

@pytest.mark.parametrize("config_file", precinct_files)
def test_voter_generation(config_file):
    # the number of booths and the impatience threshold do
    # not matter when we are just checking the voters.
    run_simulate_test(DATA_DIR + config_file, 1, 1, check_start = False)
