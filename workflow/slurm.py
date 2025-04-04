
from pathlib import Path
import os
import subprocess
import time
import sys

class slurm_executor:

    def __init__(self,default_resources,poll_intervall=10):
        
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
        self.poll_interval=poll_intervall # Time between different poll requests to the servers in seconds 

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

    def done( self, job_id: int) -> bool:

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


        
            
        





