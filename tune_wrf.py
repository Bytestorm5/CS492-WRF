# a simple tuning script
from process_output import process
from wrf_controller import run_WRF
from visualize import show_run

PATH = "/home/capstoneii/Build_WRF/WRF/run"
params = {'swint': 0}
with open('log', 'a') as log:
    for i in range(2):
        params['swint'] += 1

        with open('tuner.input', 'r') as reader:
            with open(f'{PATH}/namelist.input', 'w') as writer:
                writer.write(reader.read().format(**params))  

        if run_WRF(PATH, 20):
            show_run(process(PATH, "tuner"), f"swint_check_{i}", True, True)
        else:
            log.write(f"failed at {params['swint']}\n")