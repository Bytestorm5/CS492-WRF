import numpy as np
import mock_controller as Controller
from skopt import gp_minimize
from skopt.utils import use_named_args
from skopt.space import Real, Integer, Categorical

# ACTUAL PARAMS TBD
dim_m = Real(low=-5.0, high=5.0, name='m')
dim_b = Real(low=-5, high=5, name='b')
dimensions = [dim_m, dim_b]

@use_named_args(dimensions=dimensions)
def evaluate(**params):       
    gt = Controller.get_true_data()
    pred = Controller.run_model(params)

    # MSE
    diff = gt - pred
    eval = (diff ** 2).sum() / len(pred)
    print(params, eval)
    return eval

def optimize(iterations=10, rng_seed=123) -> tuple[list, float]:
    result = gp_minimize(func=evaluate, dimensions=dimensions, n_calls=iterations, noise=0.1, random_state=rng_seed)
    return result['x'], result['fun']

if __name__ == "__main__":
    param_result, eval = optimize(iterations=25, rng_seed=635)
    print("BEST PARAMS:", param_result)
    print("EVAL:", eval)