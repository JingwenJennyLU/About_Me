'''
Test code for Modeling Epidemics

Emma Nechamkin and Anne Rogers
July 2018

Borja Sotomayor
September 2018, 2020

Anne Rogers
July 2019, July 2021
'''

import json
import os
import sys
import random

import pytest

import sir

### TODO: question: can the call to sys.path go away?

# Handle the fact that the grading code may not
# be in the same directory as sir.py
sys.path.append(os.getcwd())

# Get the name of the directory that holds the grading code.
BASE_DIR = os.path.dirname(__file__)
TEST_DIR = os.path.join(BASE_DIR, "tests")


###### Test utility funtions ######
def gen_check_rand_calls(seed, max_num_calls):
    '''
    Generate a function that can be used to check whether the correct
    number of calls were made to the random number generator.

    Inputs:
      seed (int): the seed for the random number generator
      max_num_calls (int): the maximum number of calls to
         random.random() that will need to be verified.

    Returns: function of one variable
    '''

    random.seed(seed)
    rand_vals = [random.random() for i in range(max_num_calls+1)]

    def check(expected_num_calls):
        '''
        Check whether the expected number of calls to random.random()
        were made.

        Inputs:
          expected_num_calls: the number of calls that should have
          been made.

        Returns: boolean that will be True if the check succeeded and
          False otherwise and, if necessary, an error message as a
          string.
        '''
        assert expected_num_calls <= max_num_calls

        # Make a call to random.
        actual_r = random.random()
        expected_r = rand_vals[expected_num_calls]

        # Did the call to random yield the expected value?
        if actual_r == pytest.approx(expected_r):
            return True, None

        for i, rand_val in enumerate(rand_vals):
            if actual_r == pytest.approx(rand_val):
                if i < expected_num_calls:
                    return False, "Not enough calls to random.random()"
                return False, "Too many calls to random.random()"

        return False, "Incorrect number of calls to random.random()"

    return check


CHECK_RAND_20170217 = gen_check_rand_calls(20170217, 100)


def convert_city(params, city_key="city"):
    """
    Convert the representation of the individual people in the city
    from lists to tuples.

    Args:
        params (dictionary): the parameters for a given test
        city_key (str, optional): Defaults to "city".

    Returns:
        [list of tuples]: returns a list of person tuples
    """
    return [tuple(p) for p in params[city_key]]


def read_config_file(filename):
    '''
    Load the test cases from a JSON file.

    Inputs:
      filename (string): the name of the test configuration file.

    Returns: (list) test cases
    '''

    with open(os.path.join(TEST_DIR, filename)) as f:
        tests = json.load(f)

        for t in tests:
            if "city" not in t:
                break
            t["city"] = convert_city(t)

        # The test numbers start at 1
        return zip(range(len(tests)), tests)


def check_sequence(recreate_msg, actual, expected):
    """
    Do a few standard checks for sequences: (1) Does the actual value have the
    expected length, (2) do the individual elements of the actual value have the
    right types, and (3) do the actual and expected values match.

    Args:
        recreate_msg (string): explains how to rerun the test in ipython3
        actual (tuple or list): the actual value
        expected (typle or list): the expected value
    """

    expected_type_str = "tuple" if isinstance(expected, tuple) else "list"

    msg = "Result should be a {} of length {}\n"
    msg += recreate_msg
    msg = msg.format(expected_type_str, len(expected))

    # check length
    assert len(actual) == len(expected), msg

    # check element types
    type_msg = "Element {} in the {} should have type {}\n"
    type_msg += recreate_msg

    for i, (a, e) in enumerate(zip(actual, expected)):
        assert isinstance(a, type(e)), \
            type_msg.format(i, expected_type_str, type(e))

    # check whole value
    val_msg = "Actual ({}) and expected ({}) values do not match an index {}.\n"
    val_msg += "  Actual: {}\n"
    val_msg += "  Expected: {}\n"
    val_msg += recreate_msg
    assert actual == expected, val_msg


def check_result(recreate_msg, actual, expected):
    """
    Verify that the actual value return from a function matches the
    expected value.

    Args:
        recreate_msg (string): describes how to recreate the test in ipython3
        actual (some type): actual value.
        expected (some type): expected value
    """
    msg = "The function returned None."
    msg += " Did you forget to include a return statement?\n"
    assert actual is not None, \
        msg + recreate_msg + "\n"

    msg = "The function returned a value of the wrong type.\n"
    msg += "  Expected return type: {}.\n"
    msg += "  Actual return type: {}.\n"
    msg += recreate_msg + "\n"
    assert isinstance(actual, type(expected)), \
        msg.format(type(expected), type(actual))

    if isinstance(expected, (tuple, list)):
        # do some quick length and element type checks on the sequence
        check_sequence(recreate_msg, actual, expected)
    else:
        # check the values.
        msg = "Actual ({}) and expected ({}) values do not match.\n"
        msg += recreate_msg + "\n"
        assert actual == expected, \
        msg.format(actual, expected)




###### Task: has_an_infected_neighbor ######
def __test_has_an_infected_neighbor(test_params, is_test6):
    '''
    Test harness for has_an_infected_neighbor

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        city, index of a location in the city,
        the expected result
    '''

    test_num, params = test_params

    city = params["city"]
    city_copy = city[:]
    actual = sir.has_an_infected_neighbor(city, params["location"])

    recreate_msg = ("See the information for Task {}1, Test {} to "
                    "see how to recreate this test.")
    recreate_msg = recreate_msg.format("6-" if is_test6 else "", test_num)

    expected = params["expected"]
    check_result(recreate_msg, actual, expected)

    # Extra check
    assert city_copy == city, \
        "\nDo not modify the input city!\n" + recreate_msg

@pytest.mark.parametrize(
    "test_params",
    read_config_file("has_infected_neighbor_tests.json"))
def test_has_an_infected_neighbor(test_params):
    """
    Test for has_an_infected_neighbor (no vaxxed)

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        city, index of a location in the city,
        the expected result
    """
    __test_has_an_infected_neighbor(test_params, False)


@pytest.mark.vax
@pytest.mark.parametrize(
    "test_params",
    read_config_file("vax_has_infected_neighbor_tests.json"))
def test_vax_has_an_infected_neighbor(test_params):
    """
    Test for has_an_infected_neighbor with vaxxed

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        city, index of a location in the city,
        the expected result
    """
    __test_has_an_infected_neighbor(test_params, True)



###### Task : Advance person at location ######
def __test_advance_person_at_location(test_params, is_test6):
    """
    Test harness for advance_person_at_location

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        seed, city, index of location in the city,
        infection rate, number of days contagious
        expected result
    """

    test_num, params = test_params

    city = params["city"]
    city_copy = city[:]

    actual = sir.advance_person_at_location(city,
                                            params["location"],
                                            params["days_contagious"])

    recreate_msg = ("See the information for Task 2, Test {} to "
                    "see how to recreate this test.")
    recreate_msg = recreate_msg.format("6-" if is_test6 else "", test_num)

    # convert expected to the correct type
    expected = tuple(params["expected"])
    check_result(recreate_msg, actual, expected)

    # Extra checks
    assert city_copy == city, \
        "\nDo not modify the city!\n" + recreate_msg


@pytest.mark.parametrize(
    "test_params",
    read_config_file("advance_person_tests.json"))
def test_advance_person_at_location(test_params):
    """
    Test for advance_person_at_location, no vaxxed people.

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        seed, city, index of location in the city,
        infection rate, number of days contagious
        expected result
    """
    __test_advance_person_at_location(test_params, False)


@pytest.mark.vax
@pytest.mark.parametrize(
    "test_params",
    read_config_file("vax_advance_person_tests.json"))
def test_vax_advance_person_at_location(test_params):
    """
    Test for advance_person_at_location, some vaxxed people.

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        seed, city, index of location in the city,
        infection rate, number of days contagious
        expected result
    """
    __test_advance_person_at_location(test_params, True)


###### Task: Move simulation forward one day ######
@pytest.mark.parametrize(
    "test_params",
    read_config_file("simulate_one_day_tests.json"))
def __test_simulate_one_day(test_params, is_test6):
    """
    Test harness for simulate_one_day

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        seed, city, infection rate, number of days contagious,
        expected result
    """

    test_num, params = test_params

    city = params["city"]
    city_copy = city[:]

    actual = sir.simulate_one_day(city,
                                  params["days_contagious"])

    recreate_msg = ("See the information for Task 3, Test {} to "
                    "see how to recreate this test.")
    recreate_msg = recreate_msg.format("6-" if is_test6 else "", test_num)

    # Fix the type of the people in the city
    expected = convert_city(params, "expected")
    check_result(recreate_msg, actual, expected)

    # Extra check
    assert city_copy == city, \
        "\nDo not modify the input city!\n" + recreate_msg

@pytest.mark.parametrize(
    "test_params",
    read_config_file("simulate_one_day_tests.json"))
def test_simulate_one_day(test_params):
    """
    Test for simulate_one_day, no vaxxed people

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        seed, city, infection rate, number of days contagious,
        expected result
    """
    __test_simulate_one_day(test_params, False)


@pytest.mark.vax
@pytest.mark.parametrize(
    "test_params",
    read_config_file("vax_simulate_one_day_tests.json"))
def test_vax_simulate_one_day(test_params):
    """
    Test for simulate_one_day, some vaxxed people

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        seed, city, infection rate, number of days contagious,
        expected result
    """
    __test_simulate_one_day(test_params, True)



###### Task: check stopping condition ######
def __test_is_transmission_possible(test_params, is_test6):
    """
    Test harness for is_transmission_possible function

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        city and the expected result
    """

    test_num, params = test_params

    city = params["city"]
    city_copy = city[:]

    actual = sir.is_transmission_possible(city)

    recreate_msg = ("See the information for Task 4, Test {} to "
                    "see how to recreate this test.")
    recreate_msg = recreate_msg.format("6-" if is_test6 else "", test_num)

    expected = params["expected"]
    check_result(recreate_msg, actual, expected)

    # Extra check
    assert city_copy == city, \
        "\nDo not modify the input city!\n" + recreate_msg


@pytest.mark.parametrize(
    "test_params",
    read_config_file("is_transmission_possible.json"))
def test_is_transmission_possible(test_params):
    """
    Test harness for is_transmission_possible function no vaxxed people.

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
    """

    __test_is_transmission_possible(test_params, False)


@pytest.mark.vax
@pytest.mark.parametrize(
    "test_params",
    read_config_file("vax_is_transmission_possible.json"))
def test_vax_is_transmission_possible(test_params):
    """
    Test harness for is_transmission_possible function with some vaxxed
      folks added in.

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
    """

    __test_is_transmission_possible(test_params, True)


###### Task: run simulation over multiple days  ######
def __test_run_simulation(test_params, is_test6):
    """
    Test harness for run_simulation

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        city, the number of days contagious, and the
        expected result
    """

    test_num, params = test_params

    starting_city = params["city"]
    city_copy = starting_city[:]

    actual = sir.run_simulation(starting_city,
                                params["days_contagious"])

    recreate_msg = ("See the information for Task 5, Test {} to "
                    "see how to recreate this test.")
    recreate_msg = recreate_msg.format("6-" if is_test6 else "", test_num)

    # convert the type pf the people in the city
    expected = params["expected"]
    expected = ([tuple(p) for p in expected[0]], expected[1])
    check_result(recreate_msg, actual, expected)

    # Extra check
    assert city_copy == starting_city, \
        "\nDo not modify the input city!\n" + recreate_msg


@pytest.mark.parametrize(
    "test_params",
    read_config_file("run_simulation_tests.json"))
def test_run_simulation(test_params):
    """
    Test run_simulation, no vaxxed people

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        city, the number of days contagious, and the
        expected result
    """
    __test_run_simulation(test_params, False)

@pytest.mark.vax
@pytest.mark.parametrize(
    "test_params",
    read_config_file("vax_run_simulation_tests.json"))
def test_vax_run_simulation(test_params):
    """
    Test run_simulation, some vaxxed people

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        city, the number of days contagious, and the
        expected result
    """
    __test_run_simulation(test_params, True)


###### Task: vaccinate a person ######
@pytest.mark.parametrize(
    "test_params",
    read_config_file("vaccinate_person.json"))
def test_vaccinate_person(test_params):
    """
    Test vaccinate_person

    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        the seed, an augmented person, the expected result, and the expected
        number of calls to random.
    """
    test_num, params = test_params

    # set the seed
    random.seed(params["seed"])

    # use the same seed for all the tests
    if params["seed"] == sir.TEST_SEED:
        # Use pre-generated random checking function
        check_rand = CHECK_RAND_20170217
    else:
        check_rand = gen_check_rand_calls(params["seed"], 100)

    aug_person = tuple(params["aug_person"])

    recreate_msg = ("See the information for Task 7, Test {} to "
                    "see how to recreate this test.")
    recreate_msg = recreate_msg.format(test_num)

    actual = sir.vaccinate_person(aug_person)

    expected = tuple(params["expected"])
    check_result(recreate_msg, actual, expected)

    # Extra checks
    (check, msg) = check_rand(params["num_rand_calls"])
    assert check, msg + "\n" + recreate_msg

###### Task: vaccinate a city ######
@pytest.mark.parametrize(
    "test_params",
    read_config_file("vaccinate_city.json"))
def test_vaccinate_city(test_params):
    """
    Test vaccinate_city
    Inputs:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        a seed, a list of augmented persons, and the expected result city.
    """

    test_num, params = test_params

    city = params["city"]
    city_copy = city[:]
    expected_num_rand_calls = len([p[0] for p in city if p[0] == "S"])

    # use the same seed for all the tests
    if params["seed"] == sir.TEST_SEED and expected_num_rand_calls < 100:
        # Use pre-generated random checking function
        check_rand = CHECK_RAND_20170217
    else:
        check_rand = gen_check_rand_calls(params["seed"],
                                          expected_num_rand_calls)

    actual = sir.vaccinate_city(city, params["seed"])

    recreate_msg = ("See the information for Task 8, Test {} to "
                    "see how to recreate this test.")
    recreate_msg = recreate_msg.format(test_num)

    expected = convert_city(params, "expected")
    check_result(recreate_msg, actual, expected)

    # Extra checks
    assert city == city_copy, \
        "\nDo not modify the input city!\n" + recreate_msg

    # one call to random expected for each susceptible person.
    (check, msg) = check_rand(expected_num_rand_calls)
    assert check, msg + "\n" + recreate_msg


###### Task: Combine vaccination and simulation ######
@pytest.mark.parametrize(
    "test_params",
    read_config_file("vaccinate_and_simulate.json"))
def test_vaccinate_and_simulate(test_params):
    """
    Test vax_and_simulate

    Args:
      test_params (int, dictionary): the test number and the test
      parameters dictionary:
        augmented persons, and the expected result.
    """

    test_num, params = test_params
    city = params["city"]
    days_contagious = params["days_contagious"]
    seed = params["seed"]

    actual = sir.vaccinate_and_simulate(city, days_contagious, seed)

    recreate_msg = ("See the information for Task 9, Test {} to "
                    "see how to recreate this test.")
    recreate_msg = recreate_msg.format(test_num)

    # convert the expected city to have the right type
    expected = params["expected"]
    expected = ([tuple(p) for p in expected[0]], expected[1])
    check_result(recreate_msg, actual, expected)
