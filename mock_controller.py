import numpy as np

# Functions to mock an interface with the WRF-Solar Model
# Abstracting like this makes it easier to test

# get_true_data() and run_model() should output data in the same format/shape

# Gets the ground truth output data for the model as a numpy array

Xs = list(range(50))

def get_true_data() -> np.ndarray:
    return np.array([(x * 2) + 3 for x in Xs])

# Runs the model with given parameters and returns output as numpy arrays
def run_model(params) -> np.ndarray:
    return np.array([(x * params['m']) + params['b'] for x in Xs])