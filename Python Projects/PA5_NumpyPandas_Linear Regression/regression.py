'''
Linear regression

Main file for linear regression and model selection.
'''

import numpy as np
from sklearn.model_selection import train_test_split
import util


class DataSet(object):
    '''
    Class for representing a data set.
    '''

    def __init__(self, dir_path):
        '''
        Class for representing a dataset, performs train/test
        splitting.

        Inputs:
            dir_path: (string) path to the directory that contains the
              file
        '''

        parameters_dict = util.load_json_file(dir_path, "parameters.json")
        self.feature_idx = parameters_dict["feature_idx"]
        self.name = parameters_dict["name"]
        self.target_idx = parameters_dict["target_idx"]
        self.training_fraction = parameters_dict["training_fraction"]
        self.seed = parameters_dict["seed"]
        self.labels, data = util.load_numpy_array(dir_path, "data.csv")

        # do standardization before train_test_split
        if(parameters_dict["standardization"] == "yes"):
            data = self.standardize_features(data)

        self.training_data, self.testing_data = train_test_split(data,
            train_size=self.training_fraction, test_size=None,
            random_state=self.seed)

    # data standardization
    def standardize_features(self, data): 
        '''
        Standardize features to have mean 0.0 and standard deviation 1.0.
        Inputs:
          data (2D NumPy array of float/int): data to be standardized
        Returns (2D NumPy array of float/int): standardized data
        '''
        mu = data.mean(axis=0) 
        sigma = data.std(axis=0) 
        return (data - mu) / sigma

class Model(object):
    '''
    Class for representing a model.
    '''

    def __init__(self, dataset, feature_idx):
        '''
        Construct a data structure to hold the model.
        Inputs:
            dataset: an dataset instance
            feature_idx: a list of the feature indices for the columns (of the
              original data array) used in the model.
        '''

        self.dataset = dataset
        self.feature_idx = list(feature_idx)
        self.target_idx = dataset.target_idx

        x_training_features = dataset.training_data[:, self.feature_idx]
        self.y_train = dataset.training_data[:, self.target_idx]

        self.x_train = util.prepend_ones_column(x_training_features)
        self.beta = util.linear_regression(self.x_train, self.y_train)
        self.R2 = self.compute_r2(self.x_train, self.y_train)


    def __repr__(self):
        '''
        Format model as a string.
        '''

        target_name = self.dataset.labels[self.target_idx]
        result = f"{target_name} : {self.beta[0]:.6f}"
        for i, feat_idx in enumerate(self.feature_idx):
            feat_name = self.dataset.labels[feat_idx]
            coef = self.beta[i + 1]
            result += f" + {coef:.6f} * {feat_name}"
        return result

    def compute_r2(self, x, y):
        '''
        compute coefficient of r2
        
        inputs:
            x: 2d array, feature matrix with prepend ones
            y: 1d numpy array, target value

        return: float, r2
        '''

        y_pred = util.apply_beta(self.beta, x)
        residuals = y - y_pred
        y_mean = np.mean(y)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - y_mean) ** 2)
        r2 = 1 - (ss_res / ss_tot)

        return r2


def compute_single_var_models(dataset):
    '''
    Computes all the single-variable models for a dataset

    Inputs:
        dataset: (DataSet object) a dataset

    Returns:
        List of Model objects, each representing a single-variable model
    '''

    lst_models = [Model(dataset, [idx]) for idx in dataset.feature_idx]

    return lst_models


def compute_all_vars_model(dataset):
    '''
    Computes a model that uses all the feature variables in the dataset

    Inputs:
        dataset: (DataSet object) a dataset

    Returns:
        A Model object that uses all the feature variables
    '''

    return Model(dataset, dataset.feature_idx)


def compute_best_pair(dataset):
    '''
    Find the bivariate model with the best R2 value

    Inputs:
        dataset: (DataSet object) a dataset

    Returns:
        A Model object for the best bivariate model
    '''

    best_model = None
    best_r2 = -1

    num_features = len(dataset.feature_idx)
    for i in range(num_features):
        for j in range(i + 1, num_features):
            feature_pair = [dataset.feature_idx[i], dataset.feature_idx[j]]
            model = Model(dataset, feature_pair)

            if model.R2 > best_r2:
                best_r2 = model.R2
                best_model = model
    
    return best_model


def forward_selection(dataset):
    '''
    Given a dataset with P feature variables, uses forward selection to
    select models for every value of K between 1 and P.

    Inputs:
        dataset: (DataSet object) a dataset

    Returns:
        A list (of length P) of Model objects. The first element is the
        model where K=1, the second element is the model where K=2, and so on.
    '''
    
    models = []
    selected_features = []
    available_features = list(dataset.feature_idx)

    num_features = len(dataset.feature_idx)

    for k in range(num_features):
        best_model = None
        best_r2 = -1
        best_feature = None

        for feature in available_features:
            trial_features = selected_features + [feature]
            model = Model(dataset, trial_features)

            if model.R2 > best_r2:
                best_r2 = model.R2
                best_model = model
                best_feature = feature
        
        selected_features.append(best_feature)
        available_features.remove(best_feature)
        models.append(best_model)
    
    return models


def validate_model(dataset, model):
    '''
    Given a dataset and a model trained on the training data,
    compute the R2 of applying that model to the testing data.

    Inputs:
        dataset: (DataSet object) a dataset
        model: (Model object) A model that must have been trained
           on the dataset's training data.

    Returns:
        (float) An R2 value
    '''

    x_test_features = dataset.testing_data[:, model.feature_idx]
    y_test = dataset.testing_data[:, model.target_idx]

    x_test = util.prepend_ones_column(x_test_features)

    return model.compute_r2(x_test, y_test)
