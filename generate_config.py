from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import re
import copy

benchmark_template = {
    "filePerProcess": False,
    "processorGrid": [0,0,0],
    "paths": ["data"],
    "sync": True,
    "operation": "write"
}

benchmarks=[]

with open("experiment.yaml") as f:
    data = load(f, Loader=Loader)
    
for layer in data["layers"]:
    for filed in data["fields"]:
        for mesh in data["mesh"]:
            for fields in data["fields"]:
                for operation in data["operation"]:
                    for api in data["api"]:
                        m=re.match(r"C([0-9]+)",mesh)
                        mesh_number=int(m[1])   
                        shape=[int(layer),mesh_number,mesh_number]
                        current_benchmark=copy.deepcopy(benchmark_template)
                        current_benchmark["shape"]=shape
                        current_benchmark["operation"]=str(operation)
                        current_benchmark["fields"]=int(fields)
                        current_benchmark["API"]=api
                        benchmarks.append(current_benchmark)


with open("config.yaml","w") as f:
    dump({"benchmarks":benchmarks},f)