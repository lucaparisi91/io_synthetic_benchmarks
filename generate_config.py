from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import re
import copy
import os
from pathlib import Path


benchmark_template = {
    "filePerProcess": False,
    "processorGrid": [0,0,0],
    "paths": ["data"],
    "sync": True,
    "operation": "write"
}

def create_data_directory(data,stripes):
    """
    Create the data inside a directory
    """

def experiment_dirname(config):
    """
    Get an unique directory name for the experiment
    """


def generate_slurm_script(config,nodes=1,tasks_per_node=1):
    """

    """

def run_slurm_script( script_name ):
    """
    """


def generate_configs(experiment_config):
    benchmarks=[]
    for layer in data["layers"]:
        for fied in data["fields"]:
            for mesh in data["mesh"]:
                for fields in data["fields"]:
                    for operation in data["operation"]:
                        for api in data["api"]:
                            folder_prefix=f"layer={layer}/fields={fields}/mesh={mesh}"

                            m=re.match(r"C([0-9]+)",mesh)
                            mesh_number=int(m[1])   
                            shape=[int(layer),mesh_number,mesh_number]
                            current_benchmark=copy.deepcopy(benchmark_template)
                            current_benchmark["shape"]=shape
                            current_benchmark["operation"]=str(operation)
                            current_benchmark["fields"]=int(fields)
                            current_benchmark["API"]=api
                            for directory in data["directories"]:
                                data_dir=Path(os.path.join(directory,folder_prefix))
                                data_dir.mkdir(parents=True, exist_ok=True)
                                print(data_dir)

                                for stripes in data["stripes"]:
                                    striped_dir=(data_dir / f"stripes={stripes}")
                                    striped_dir.mkdir(parents=True, exist_ok=True)
                                    current_benchmark["paths"]=[str(striped_dir)]

                                    benchmarks.append(current_benchmark)
                                    config_folder=Path(os.path.join(os.getcwd(),"experiments",folder_prefix))
                                    config_folder.mkdir(parents=True, exist_ok=True)
                                    with open(config_folder/ "config.yaml","w+") as f :
                                        dump( {"benchmarks":[current_benchmark]}, f, Dumper=Dumper)
                                        

with open("experiment.yaml") as f:
    data = load(f, Loader=Loader)

generate_configs(data)