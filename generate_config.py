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


def generate_configs(experiment_config):

    experiments=[]
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
                                
                                for stripes in data["stripes"]:
                                    striped_dir=(data_dir / f"stripes={stripes}")

                                    current_benchmark["paths"]=[str(striped_dir)]

                                    config_folder=Path(os.path.join(os.getcwd(),"experiments",folder_prefix))
                                    config={"benchmarks":[current_benchmark] }
                                    slurm_resources={"nodes": 1 }
                                    storage_resources={"stripes":1,"work_dir":config_folder}

                                    experiments.append({"config":config,"storage_resources":storage_resources,"slurm_resources":slurm_resources})
    return experiments


def setup_experiment( experiment: dict) -> None :

    config=experiment["config"]
    storage_resources=experiment["storage_resources"]
    work_dir=storage_resources["work_dir"]

    work_dir.mkdir(parents=True, exist_ok=True)
    with open( work_dir/ "config.yaml","w+") as f :
                                        dump( config , f, Dumper=Dumper)
    
    for benchmark in  config["benchmarks"]:
        for data_dir_name in benchmark["paths"]:
            Path(data_dir_name).mkdir(parents=True, exist_ok=True)

    return experiment    


with open("experiment.yaml") as f:
    data = load(f, Loader=Loader)

experiments=generate_configs(data)

for experiment in experiments:
    setup_experiment(experiment)
