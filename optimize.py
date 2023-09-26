import numpy as np
import wrf_controller as Controller
from skopt import gp_minimize
from skopt.utils import use_named_args
from skopt.space import Real, Integer, Categorical

# ACTUAL PARAMS TBD
dim_qh = Integer(low=450, high=700, name='qh')
dim_qhl = Integer(low=700, high=900, name='qhl')
dim_qs = Integer(low=50, high=200, name='qs')
dimensions = [dim_qh, dim_qhl, dim_qs]

@use_named_args(dimensions=dimensions)
def evaluate(**params):     
    print("\n--- EVALUATING CURRENT RESULTS ---")  
    gt = Controller.get_true_data()
    pred = Controller.run_model(params)

    # MSE
    SE = 0
    for pred_t, pred_val in pred.items():
        SE += (pred_val - gt[pred_t]) ** 2
    MSE = SE / len(pred.keys())
    print(f"--- MSE: {MSE} ---\n")
    return MSE

def optimize(iterations=10, rng_seed=123) -> tuple[list, float]:
    result = gp_minimize(func=evaluate, dimensions=dimensions, n_calls=np.int32(iterations), noise=0.1, random_state=np.int32(rng_seed))
    return result['x'], result['fun']

if __name__ == "__main__":
    param_result, eval = optimize(iterations=25, rng_seed=5)
    print("BEST PARAMS:", param_result)
    print("EVAL:", eval)