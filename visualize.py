import matplotlib.pyplot as plt
from extract_GT import get_GT
import numpy as np

def show_run(run, name, GT = False, scatter = False):
    plt.clf()
    if GT:
        gt = get_GT()
        plt.plot(run[:,0], gt, label = "GT")
        plt.title("DOWN MSE: {:.2} TOT MSE: {:.2}".format(np.mean((gt - run[:,1])**2), np.mean((gt - run[:,4])**2)))
    if scatter:
        plt.scatter(run[:,0], run[:,1], label = "SWDOWN")
        plt.scatter(run[:,0], run[:,4], label = "DIR + DIF")
    else:
        plt.scatter(run[:,0], run[:,1], label = "SWDOWN")
        plt.scatter(run[:,0], run[:,4], label = "DIR + DIF")
    plt.legend()
    plt.savefig(name + '.jpg')