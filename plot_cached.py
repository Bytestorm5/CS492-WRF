import numpy as np
import matplotlib.pyplot as plt
import os
index = 4
for run in os.listdir('cached_runs'):
    data = np.load(os.path.join('cached_runs',run))
    #print(np.mean(data[:,index]))
    plt.plot(data[:,index])
plt.title("SWDOWN over many epochs")
plt.savefig('cached_runs.png')