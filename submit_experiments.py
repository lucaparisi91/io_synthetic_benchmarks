
from pathlib import Path
import os
import subprocess
import time
import sys


# class JobException(Exception):

#     def __init__( self, task, command_exception):
#         self.task=task
#         self.command_exception=command_exception

#     def __str__( self ):
#         return f"""
#                 Error in running job {self.task.name}. 
#                 Command error: {str(command_exception)}
#                 """
    


class slurm_executor:

    def __init__(self,default_resources):
        
        self.states=[
                    "BOOT_FAIL",
                    "CANCELLED",
                    "COMPLETED",	
                    "DEADLINE",
                    "FAILED",
                    "NODE_FAIL",
                    "OUT_OF_MEMORY",
                    "PENDING",
                    "PREEMPTED",
                    "RUNNING",
                    "SUSPENDED",	
                    "TIMEOUT"
                    ]

        self.completed_states=[ "BOOT_FAIL",
                                "CANCELLED",
                                "COMPLETED",
                                "DEADLINE",
                                "FAILED",
                                "NODE_FAIL",
                                "OUT_OF_MEMORY",
                                "TIMEOUT" ]

        self.succeded_states=["COMPLETED"]
        self.default_resources=default_resources


    def submit(self, task,work_dir : Path = Path(".") ) -> int:
        

        slurm_options= dict ()
        slurm_options.update(self.default_resources)

        slurm_options.update(
            {
                "job-name" : task.name
            }

        )

        if (task.resources is not None):
            slurm_options.update(task.resources)
        
        # Generate a tempory batch script file
        batch_script=self._generate_batch_script(task.script,slurm_options,work_dir)
        script_file_name = os.path.join(work_dir, "submit.sh")
        with open( script_file_name,"w+") as f:
            f.write(batch_script)
        
        # Submit the script

        
        output=subprocess.check_output(["sbatch","--parsable" ,script_file_name],cwd=work_dir)
        

        job_id= int(output)
        return job_id
    

    def get_state(self, job_id : int ) -> str :
        """
        Return the state for a given job
        """    
        check_job_state=f"sacct --parsable -j {job_id} --format=State | cut -d '|' -f1 | sed -n 2p"
        state=subprocess.check_output(["sh","-c",check_job_state])
        return state.decode("utf-8").strip()

    def done( self, jobid: int) -> bool:

        return self.get_state(  job_id) in self.completed_states

    def wait(self, job_id : int):
        """
        Block until the job is completed
        """

        while (not self.done(job_id) ):
            time.sleep(10)



    def _generate_batch_script(self,script: str ,slurm_options: dict ,work_dir : Path =None ) -> str :    
        batch_script="#!/bin/bash\n"

        for option_name,option_value in slurm_options.items():
            batch_script+=f"#SBATCH --{option_name}={option_value}\n"
        
        if work_dir is not None:
            batch_script+=f"cd {work_dir}\n"
        batch_script+=script   
        
        return str(batch_script)
    
    
        

        
            
        


class task:

    def __init__(self,name,script,resources=None):
        self.name=name
        self.script=script
        self.resources=resources



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





executor= slurm_executor(
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



#config= "./experiments/layer=70/fields=1/mesh=C12/config.yaml"

configs= get_configs("./experiments")

print(configs)

for index,config in enumerate(configs):
    current_task=task(f"benchio_{index}", bash_script )
    work_dir=os.path.abspath(Path(config).parent)
    job_id = executor.submit(current_task,work_dir=work_dir)
    executor.wait(job_id)
    print(f"Task {current_task.name} completed with state " , executor.get_state(job_id) )