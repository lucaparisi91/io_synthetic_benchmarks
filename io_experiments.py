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


def generate_configs(experiment_config: dict):
    
    experiments=[]
    for layer in experiment_config["layers"]:
        for fied in experiment_config["fields"]:
            for mesh in experiment_config["mesh"]:
                for fields in experiment_config["fields"]:
                    for operation in experiment_config["operation"]:
                        for api in experiment_config["api"]:
                            folder_prefix=f"layer={layer}/fields={fields}/mesh={mesh}"

                            m=re.match(r"C([0-9]+)",mesh)
                            mesh_number=int(m[1])   
                            shape=[int(layer),mesh_number,mesh_number]
                            current_benchmark=copy.deepcopy(benchmark_template)
                            current_benchmark["shape"]=shape
                            current_benchmark["operation"]=str(operation)
                            current_benchmark["fields"]=int(fields)
                            current_benchmark["API"]=api

                            for directory in experiment_config["directories"]:
                                data_dir=Path(os.path.join(directory,folder_prefix))
                                data_dir.mkdir(parents=True, exist_ok=True)
                                
                                for stripes in experiment_config["stripes"]:
                                    for nodes in experiment_config["nodes"]:
                                        for ntasks_per_node in experiment_config["ntasks-per-node"]:
                                            slurm_resources={"nodes": nodes }
                                            slurm_resources["ntasks-per-node"]=ntasks_per_node
                                            config_folder=Path(os.path.join(os.getcwd(),"experiments",folder_prefix))
                                            config={"benchmarks":[current_benchmark] }
                                            storage_resources={"stripes":1,"work_dir":config_folder}
                                            striped_dir=(data_dir / f"stripes={stripes}" / f"nodes={nodes}")
                                            current_benchmark["paths"]=[str(striped_dir) ]

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