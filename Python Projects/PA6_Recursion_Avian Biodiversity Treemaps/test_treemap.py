'''
Tests for treemaps
'''

import json
import operator
import pytest
import treemap
import tree

# DO NOT REMOVE THESE LINES OF CODE
# pylint: disable-msg= missing-docstring, redefined-outer-name
# pylint: disable-msg= invalid-name, too-many-locals
# pylint: disable-msg= assignment-from-none, assignment-from-no-return, bad-continuation

TEST_KEYS = ['s1', 's2', 's3', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr',
             'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Year']


@pytest.fixture(scope="session")
def data_internal_values():
    """
    Fixture for loading the data for compute_internal_values
    """
    return get_data_values_paths()


@pytest.fixture(scope="session")
def data_paths():
    """
    Fixture for loading the data for compute_paths
    """
    return get_data_values_paths()


def get_data_values_paths():
    d = {}

    d["birds"] = load_trees("data/birds.json")
    d["expected_birds_values_paths"] = load_trees(
        "test_data/expected_birds_values_paths.json")

    return d


@pytest.fixture(scope="session")
def data_rectangles():
    """
    Fixture for loading the data for compute_rectangles
    """

    d = {}

    for filename_base in ['sparrows', 'birds']:
        d[filename_base] = load_trees("data/" + filename_base + ".json")
        filename = "test_data/expected_" + filename_base + \
                   "_rectangles.json"
        try:
            with open(filename) as f:
                d["expected_" + filename_base + "_rectangles"] = json.load(f)
        except FileNotFoundError:
            msg = ("Cannot open file: {}.\n"
                   "Did you remember to run the script to get"
                   " the data and the test files?".format(filename))
            pytest.fail(msg.format(filename))

    return d


def compare_trees(t, expected_t, error_prefix, recreate_msg, attributes):
    node_error_prefix = error_prefix + "Checking a node with " + ", ".join(
        ["{}={}".format(attr, repr(getattr(t, attr, "[not assigned]")))
        for attr in attributes]) + "\n"

    for attr in attributes:
        assert hasattr(t, attr), \
            node_error_prefix + \
            "Node is missing attribute {}.\n".format(attr) + \
            recreate_msg

        assert getattr(t, attr) == getattr(expected_t, attr), \
        node_error_prefix + ("Node has incorrect {}. "
            "Got {}, expected {}.\n").format(attr,
            repr(getattr(t, attr)), repr(getattr(expected_t, attr))) + \
            recreate_msg


    children = list(t.children)
    expected_children = list(expected_t.children)

    if expected_children == []:
        assert children == [], node_error_prefix + \
            "Expected node to have no children, but it has children.\n" + \
            recreate_msg
    else:
        for c in children:
            assert isinstance(c, tree.Tree), node_error_prefix + \
                "Node has a child that is not a Tree: {}\n".format(c) + \
                recreate_msg

        sorted_children = sorted(children, key=operator.attrgetter("key"))
        sorted_expected_children = sorted(
            expected_children, key=operator.attrgetter("key"))
        keys = [c.key for c in sorted_children]
        expected_keys = [c.key for c in sorted_expected_children]


        assert keys == expected_keys, node_error_prefix + \
            "Expected node to have children with keys {} " \
            "but the children's keys are {}.\n".format(expected_keys, keys) + \
            recreate_msg

        for child, expected_child in zip(sorted_children,
                                         sorted_expected_children):
            compare_trees(child, expected_child, error_prefix,
                recreate_msg, attributes)


def fcompare(prefix, recreate_msg, rec, expected_rec, attr):
    got = getattr(rec, attr)
    expected = fancy_get(expected_rec, attr)
    if not isinstance(expected, tuple):
        expected = pytest.approx(expected)
    assert got == expected, \
        prefix +  "Rectangle '{}' has incorrect {} " \
        "(got {}, expected {}).\n".format(rec.label, attr, got, expected) + \
        recreate_msg


def compare_rectangles(recs, expected_recs, error_prefix, recreate_msg):
    assert isinstance(recs, list), \
        "Expected compare_rectangles to return a list of " \
        "Rectangle objects.\n" + recreate_msg

    assert len(recs) == len(expected_recs), \
        "Expected {} rectangles, but got {} instead.\n".format(
            len(expected_recs), len(recs)) + recreate_msg

    sorted_recs = sorted(recs, key=lambda rec: (rec.label,
        rec.x, rec.y, rec.width, rec.height, rec.color_code))
    sorted_expected_recs = sorted(expected_recs, key=lambda r: (r['label'],
        r['x'], r['y'], r['width'], r['height'], r['color_code']))

    labels = [rec.label for rec in sorted_recs]
    expected_labels = [r["label"] for r in sorted_expected_recs]

    assert labels == expected_labels, \
        error_prefix + ("Expected rectangles with labels {} "
        "but the labels are {}.\n").format(expected_labels, labels) + \
        recreate_msg

    for rec, expected_rec in zip(sorted_recs, sorted_expected_recs):
        for attr in ("x", "y", "width", "height", "color_code"):
            fcompare(error_prefix, recreate_msg, rec, expected_rec, attr)


@pytest.mark.parametrize("key", TEST_KEYS)
def test_compute_internal_values(data_internal_values, key):
    error_prefix, recreate_msg = gen_recreate_msg('data/birds.json', 'data',
        'compute_internal_values', key)

    expected_t = data_internal_values['expected_birds_values_paths'][key]
    t = data_internal_values['birds'][key]

    total_count = treemap.compute_internal_values(t)

    assert total_count == expected_t.value, \
        error_prefix + ("Incorrect compute_internal_values return value. "
            "Got {}, expected {}.\n").format(total_count, expected_t.value) + \
            recreate_msg

    compare_trees(t, expected_t, error_prefix,
        recreate_msg, ["key", "value"])


@pytest.mark.parametrize("key", TEST_KEYS)
def test_compute_paths(data_paths, key):
    error_prefix, recreate_msg = gen_recreate_msg('data/birds.json', 'data',
        'compute_paths', key)

    expected_t = data_paths['expected_birds_values_paths'][key]
    t = data_paths['birds'][key]

    actual_return = treemap.compute_paths(t)

    assert actual_return is None, \
        error_prefix + ("compute_paths is supposed to return None. "
            "Got {}, expected {}.\n").format(actual_return, "None") + \
            recreate_msg

    compare_trees(t, expected_t, error_prefix,
        recreate_msg, ["key", "path"])


@pytest.mark.parametrize("key", TEST_KEYS)
def test_compute_rectangles_flat(data_rectangles, key):
    do_test_compute_rectangles(data_rectangles, 'sparrows', 'data_flat', key)


@pytest.mark.parametrize("key", TEST_KEYS)
def test_compute_rectangles_full(data_rectangles, key):
    do_test_compute_rectangles(data_rectangles, 'birds', 'data', key)


def do_test_compute_rectangles(data_rectangles, filename_base, dict_name, key):
    error_prefix, recreate_msg = gen_recreate_msg(
        'data/' + filename_base + '.json', dict_name,
        'compute_rectangles', key, 'recs')

    expected_recs = \
        data_rectangles['expected_' + filename_base + '_rectangles'][key]
    t = data_rectangles[filename_base][key]

    recs = treemap.compute_rectangles(t)

    compare_rectangles(recs, expected_recs, error_prefix, recreate_msg)


### Helper functions

def load_trees(filename):
    '''
    Loads trees from a json file. The json file
    should consist of a dictionary mapping tree
    names to trees represented as lists.

    Input:
        filename: (string) name of the json file.

    Returns: dictionary mapping tree names (strings)
        to Tree instances.
    '''

    try:
        with open(filename) as f:
            trees_json = json.load(f)

        return {name: list_to_tree(lst) for name, lst in trees_json.items()}
    except FileNotFoundError:
        msg = ("Cannot open file: {}.\n"
               "Did you remember to run the script to get"
               " the data and the test files?".format(filename))
        pytest.fail(msg.format(filename))


def list_to_tree(lst): ### MODIFIED FROM treemap.py VERSION
    '''
    Converts a list to a tree. The first element
    of the list should be a dictionary mapping
    attributes to values. The remaining elements
    of the list are the child subtrees, in the
    same format.

    Input:
        lst: list representing a tree.

    Returns: a Tree instance.
    '''

    root = lst[0]
    children = lst[1:]
    t = tree.Tree(fancy_get(root, 'key'), fancy_get(root, 'value'))
    for attrname in root:
        attrvalue = fancy_get(root, attrname)
        if attrname not in ['key', 'value']:
            setattr(t, attrname, attrvalue)
    for child_list in children:
        t.add_child(list_to_tree(child_list))
    return t

def fancy_get(d, key, default=None):
    val = d.get(key, default)
    if isinstance(val, list):
        return tuple(val)

    return val


def gen_recreate_msg(filename, dict_name, function, key, save_variable=None):
    error_prefix = ("Error when testing {} "
        "on {} with key {}\n").format(function, filename, key)

    recreate_msg = "To recreate this test in ipython3 run:\n"
    recreate_msg += "  {} = treemap.load_trees('{}')\n".format(
        dict_name, filename)
    recreate_msg += "  {}treemap.{}({}['{}'])".format(
        ("" if save_variable is None else save_variable + " = "),
        function, dict_name, key)

    return error_prefix, recreate_msg
