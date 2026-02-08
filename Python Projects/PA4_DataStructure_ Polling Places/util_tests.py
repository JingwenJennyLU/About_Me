'''
Polling places

Utilities
'''

import csv
import sys
import os
import pytest

from util import load_precinct

# Handle the fact that the grading code may not
# be in the same directory as implementation
sys.path.insert(0, os.getcwd())

from simulate import Precinct, VotingBooths, find_voting_booths_needed, find_impatience_threshold

# DO NOT MODIFY THIS FILE
# pylint: disable-msg= invalid-name, too-many-arguments, line-too-long
# pylint: disable-msg= too-many-branches

# # #
#
# HELPER FUNCTIONS
#
# # #

def check_none(actual, recreate_msg=None):
    msg = "The function returned None."
    msg += " Did you forget a return statement?"
    if recreate_msg is not None:
        msg += "\n" + recreate_msg

    assert actual is not None, msg

def check_type(actual, expected, recreate_msg=None):
    actual_type = type(actual)
    expected_type = type(expected)

    msg = "The function returned a value of the wrong type.\n"
    msg += "  Expected return type: {}.\n".format(expected_type.__name__)
    msg += "  Actual return type: {}.".format(actual_type.__name__)
    if recreate_msg is not None:
        msg += "\n" + recreate_msg

    assert isinstance(actual, expected_type), msg

def check_equals(actual, expected, recreate_msg=None):
    msg = "Actual ({}) and expected ({}) values do not match.".format(actual, expected)
    if recreate_msg is not None:
        msg += "\n" + recreate_msg

    assert actual == expected, msg


def bool_compare(nvoter, field, actual, expected, recreate_msg):
    """
    Compare an actual and expected boolean value for a voter.  

    nvoter: (int) the index of the voter in the voter list
    field: (str) the name of the field being compared
    actual: (bool) the expected value
    expected: (str) a bool represented as a string
    recreate_msg: (str) a message that explains how to rerun the test.
    """

    msg = "\nVoter #{} has incorrect {} value (actual {}, expected {})\n".format(nvoter, field, actual, expected)
    msg += recreate_msg

    print(nvoter, field)

    expected = (expected == "True")
    print("actual", actual, type(actual))
    print("expected", expected, type(expected))
    assert actual == expected, msg


def time_compare(nvoter, field, actual, expected, recreate_msg):
    """
    Compare an actual and expected time for a voter.  A time will be
    None when it is never set (e.g., when a voter leaves without voting
    their start time will be None.).

    nvoter: (int) the index of the voter in the voter list
    field: (str) the name of the field being compared
    actual: (float) the expected value
    expected: (str) a float represented as a string or the string "None"
    recreate_msg: (str) a message that explains how to rerun the test.
    """

    msg = "\nVoter #{} has incorrect {} value (actual {}, expected {})\n".format(nvoter, field, actual, expected)
    msg += recreate_msg

    if expected == "None":
        assert actual is None, msg
        return

    expected = float(expected)
    assert actual == pytest.approx(expected), msg

# # #
#
# RUN TESTS
#
# # #

def run_simulation(precinct_file, num_booths=1, impatience_threshold=1000):
    p, seed = load_precinct(precinct_file)
    precinct = Precinct(p["name"], p["hours_open"], p["num_voters"],
                        p["arrival_rate"], p["voting_duration_rate"],
                        p["impatience_prob"])
    # creat the booths if needed.
    vb = VotingBooths(num_booths)
    return precinct.simulate(seed, vb, impatience_threshold)


def run_simulate_test(precinct_file, num_booths, impatience_threshold, check_start):
    pvoters = run_simulation(precinct_file, num_booths, impatience_threshold)

    results_file = precinct_file.replace(".json", "_{}_{}.csv".format(num_booths,
                                                                      impatience_threshold))

    recreate_msg = "To recreate this test run:\n"
    recreate_msg += "    voters = util_tests.run_simulation('{}', {}, {})".format(precinct_file,
                                                                                  num_booths,
                                                                                  impatience_threshold)
    with open(results_file) as f:
        reader = csv.DictReader(f)

        rvoters = [row for row in reader]
        actual = len(pvoters)
        expected = len(rvoters)

        msg = "Incorrect number of voters (actual {}, expected {})\n".format(actual, expected)
        msg += recreate_msg

        assert actual == expected, msg

        for i, (returned_voter, expected_voter) in enumerate(zip(pvoters, rvoters)):
            time_compare(i, "arrival time", returned_voter.arrival_time, float(expected_voter["arrival_time"]), recreate_msg)
            time_compare(i, "voting duration", returned_voter.voting_duration, float(expected_voter["voting_duration"]), recreate_msg)
            if check_start:
                bool_compare(i, "has voted", returned_voter.has_voted, expected_voter["has_voted"], recreate_msg)
                time_compare(i, "start time", returned_voter.start_time, expected_voter["start_time"], recreate_msg)
                time_compare(i, "departure time", returned_voter.departure_time, expected_voter["departure_time"], recreate_msg)


def run_find_vb_test(precinct_file, impatience_threshold, num_trials):
    p, seed = load_precinct(precinct_file)
    precinct = Precinct(p["name"], p["hours_open"], p["num_voters"],
                        p["arrival_rate"], p["voting_duration_rate"],
                        p["impatience_prob"])
    return find_voting_booths_needed(seed, precinct, impatience_threshold, num_trials)


def run_threshold_test(precinct_file, num_booths, num_trials):
    p, seed = load_precinct(precinct_file)
    precinct = Precinct(p["name"], p["hours_open"], p["num_voters"],
                        p["arrival_rate"], p["voting_duration_rate"],
                        p["impatience_prob"])
    return find_impatience_threshold(seed, precinct, num_booths, num_trials)

