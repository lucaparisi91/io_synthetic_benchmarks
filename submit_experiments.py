
from pathlib import Path
import os
import subprocess
import time
import sys
from workflow.slurm import slurm_executor
from workflow.tasks import task
from io_experiments import generate_configs, setup_experiment 
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from yaml import load, dump
from termcolor import colored

bash_script="""

export OMP_NUM_THREADS=1

BENCHIO_ROOT=/work/n02/n02/lparisin02/wp2/synthetic_io_benchmarks/cbenchio/scripts/build/src

srun --distribution=block:block --hint=nomultithread $BENCHIO_ROOT/benchio

"""



def get_configs(main_folder):
    
    configs=[]

    for dirpath, dnames, fnames in os.walk(main_folder):
        for f in fnames:
            if f == "config.yaml":
                configs.append(os.path.join(dirpath, f))
    
    return configs

if __name__ == "__main__":

    with open("experiment.yaml") as f:
        data = load(f, Loader=Loader)

    experiments=generate_configs(data)

    for experiment in experiments:
        setup_experiment(experiment)
    

    executor = slurm_executor(
        default_resources=
        {
            "nodes" : 1,
            "cpus-per-task": 1,
            "qos" : "short",
            "partition" : "standard",
            "time" : "00:02:00",
            "account": "n02-NGARCH"
        }
    )


    for index,experiment in enumerate(experiments):

        work_dir=os.path.abspath(experiment["storage_resources"]["work_dir"] )
        slurm_resources=experiment["slurm_resources"]
        
        current_task=task(f"benchio_{index}", bash_script,resources=slurm_resources )
        print(repr(current_task) )
        
        job_id = executor.submit(current_task,work_dir=work_dir)
        try:
             executor.wait(job_id)
        except Exception as e:
            print( colored( f"Error in submitting jobs: {str(e)} ","red") )
        else:
            print(f"Task {current_task.name} completed with state " , colored( executor.get_state(job_id) , "yellow" ) )
