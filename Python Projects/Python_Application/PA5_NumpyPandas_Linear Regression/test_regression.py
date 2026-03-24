'''
Test code for linear regression
'''

import json
import pytest
import numpy as np

from regression import DataSet, Model, compute_single_var_models, \
  compute_all_vars_model, compute_best_pair, forward_selection, \
  validate_model

# DO NOT REMOVE THESE LINES OF CODE
# pylint: disable-msg= invalid-name, missing-docstring, too-many-arguments, line-too-long
# pylint: disable-msg= missing-docstring, too-many-locals, unused-argument, broad-except
# pylint: disable-msg= assignment-from-none

DATASETS = ["city", "houseprice"]
DATA_DIR = "./data/"

@pytest.fixture(scope="session")
def test_data():
    """
    Fixture for loading the test data and creating the Dataset objects
    """
    test_data_file = DATA_DIR + "test_data.json"
    try:
        with open(test_data_file) as f:
            data = json.load(f)
    except IOError as e:
        pytest.fail("Unable to load test data file in {}".format(test_data_file), e)
    except Exception as e:
        pytest.fail("Unexpected exception: {}".format(e), e)

    for ds in DATASETS:
        data_dir = DATA_DIR + ds
        try:
            ds_obj = DataSet(data_dir)
        except IOError as e:
            pytest.fail("Unable to load dataset in {}".format(data_dir), e)
        except Exception as e:
            pytest.fail("Unexpected exception: {}".format(e), e)

        data[ds]["dataset_object"] = ds_obj

        with open(data_dir + "/data.csv") as f:
            header = f.readline()
            labels = header.strip().split(",")
            data[ds]["labels"] = labels

    return data


def fcompare(prefix, model_str, attribute, got, expected):
    error_msg = "Incorrect {} (got {}, expected {})".format(attribute, got, expected)
    assert got == pytest.approx(expected), prefix + model_str + error_msg


def ds_labels(test_data, dataset, var_indexes):
    labels = test_data[dataset]["labels"]
    var_labels = [labels[x] for x in var_indexes]
    return var_labels


def model_labels(test_data, dataset, target_idx, feature_idx):
    tgt_idx_label = ds_labels(test_data, dataset, [target_idx])
    tgt_idx_label = tgt_idx_label[0]
    feat_idx_labels = ds_labels(test_data, dataset, feature_idx)
    return tgt_idx_label, feat_idx_labels


def check_models(test_data, dataset, func, models):
    """
    Given a list of models returned by one of the functions in Tasks 1-4,
    checks whether the correct models were returned

    Inputs:
        test_data: dictionary with keys "city" and "stock".
            The corresponding values are dictionaries with keys "expected",
            "dataset_object", and "labels"
        dataset: (string) name of dataset, either "city" or "stock"
        func: (string) name of function in Task 1-4 to be tested
        models: List of model objects, returned by a function in Task 1-4
    """
    expected_models = test_data[dataset]["expected"][func]

    prefix = "\nTesting {} on {} dataset\n".format(func, dataset)

    # Check that the function returned the correct number of models
    err_msg = prefix + "Expected {} models, but got {}"
    err_msg = err_msg.format(len(expected_models), len(models))
    assert len(models) == len(expected_models), err_msg

    if None in models:
        pytest.fail(prefix + "The function returned None instead of a Model object")

    # Check that the list of models contains every expected model
    model_pairs = []
    for exp_model in expected_models:

        model = None
        for m in models:
            if m.target_idx == exp_model["target_idx"] and set(m.feature_idx) == set(exp_model["feature_idx"]):
                model = m
                break

        if model is None:
            tgt_idx_label, feat_idx_labels = model_labels(test_data, dataset,
                                                           exp_model["target_idx"],
                                                           exp_model["feature_idx"])
            feat_idx_labels = ", ".join(feat_idx_labels)
            err_msg = "Expected to find a model with target variable {} and feature variables {}. No such model was returned."
            err_msg = err_msg.format(tgt_idx_label, feat_idx_labels)
            pytest.fail(prefix + err_msg)

        model_pairs.append((model, exp_model))

    # Check that each model has the correct values
    for model, exp_model in model_pairs:
        tgt_idx_label, feat_idx_labels = model_labels(test_data, dataset, exp_model["target_idx"], exp_model["feature_idx"])
        feat_idx_labels = ", ".join(feat_idx_labels)
        model_str = "<Model: target_idx={}, featuew_idx={}>\n".format(tgt_idx_label, feat_idx_labels)

        beta0 = model.beta[0]
        exp_beta0 = exp_model["beta"][0]

        fcompare(prefix, model_str, "beta0", beta0, exp_beta0)

        betas = sorted(zip(model.feature_idx, model.beta[1:]))
        exp_betas = sorted(zip(exp_model["feature_idx"], exp_model["beta"][1:]))

        for (feat_idx, beta), (exp_feat_idx, exp_beta) in zip(betas, exp_betas):
            assert feat_idx == exp_feat_idx, "Unexpected error in tests. Please notify instructors."

            var_label = ds_labels(test_data, dataset, [feat_idx])
            var_label = var_label[0]

            fcompare(prefix, model_str, "beta for " + var_label, beta, exp_beta)
        if 'R2' in exp_model:
            R2 = model.R2
            exp_R2 = exp_model["R2"]
            fcompare(prefix, model_str, "R2", R2, exp_R2)

        # if "adj_R2" in exp_model:
        #     adj_R2 = model.adj_R2
        #     exp_adj_R2 = exp_model["adj_R2"]
        #     fcompare(prefix, model_str, "Adjusted R2", adj_R2, exp_adj_R2)

@pytest.mark.parametrize("dataset", DATASETS)
def test_task0(test_data, dataset):
    dataset_obj = test_data[dataset]["dataset_object"]

    model = Model(dataset_obj, dataset_obj.feature_idx)

    check_models(test_data, dataset, "create_model", [model])
            
@pytest.mark.parametrize("dataset", DATASETS)
def test_task1(test_data, dataset):
    dataset_obj = test_data[dataset]["dataset_object"]

    model = Model(dataset_obj, dataset_obj.feature_idx)

    check_models(test_data, dataset, "compute_R2", [model])

@pytest.mark.parametrize("dataset", DATASETS)
def test_task2a(test_data, dataset):
    dataset_obj = test_data[dataset]["dataset_object"]

    models = compute_single_var_models(dataset_obj)

    check_models(test_data, dataset, "compute_single_var_models", models)


@pytest.mark.parametrize("dataset", DATASETS)
def test_task2b(test_data, dataset):
    dataset_obj = test_data[dataset]["dataset_object"]

    model = compute_all_vars_model(dataset_obj)

    check_models(test_data, dataset, "compute_all_vars_model", [model])


@pytest.mark.parametrize("dataset", DATASETS)
def test_task3(test_data, dataset):
    dataset_obj = test_data[dataset]["dataset_object"]

    model = compute_best_pair(dataset_obj)

    check_models(test_data, dataset, "compute_best_pair", [model])



    
@pytest.mark.parametrize("dataset", DATASETS)
def test_task4(test_data, dataset):
    dataset_obj = test_data[dataset]["dataset_object"]

    models = forward_selection(dataset_obj)

    
    check_models(test_data, dataset, "forward_selection", models)

    ## We should move this into the larger check_models tests in the future
    model_orders = np.array([len(m.beta) for m in models])
    assert (model_orders == np.sort(model_orders)).all(),\
        "Returned models are not in increasing order."
        

@pytest.mark.parametrize("dataset", DATASETS)
def test_task5(test_data, dataset):
    dataset_obj = test_data[dataset]["dataset_object"]

    models = forward_selection(dataset_obj)

    if models is None:
        pytest.fail("When testing Task #5, forward_selection returned None instead of a list of Model objects")

    if models == []:
        pytest.fail("When testing Task #5, forward_selection returned an empty list instead of a list of Model objects")

    for model_i, model in enumerate(models):
        testing_R2 = validate_model(dataset_obj, model)

        exp_training_R2 = test_data[dataset]["expected"]["validate_model"][model_i]["training_R2"]
        exp_testing_R2 = test_data[dataset]["expected"]["validate_model"][model_i]["testing_R2"]

        print(testing_R2, exp_training_R2, exp_testing_R2)

        assert model.R2 == pytest.approx(exp_training_R2), \
            "Incorrect Training R2 for {} of dataset {}".format(model_i, dataset)
        assert testing_R2 == pytest.approx(exp_testing_R2), \
            "Incorrect Testing R2 for {} of dataset {}".format(model_i, dataset)
