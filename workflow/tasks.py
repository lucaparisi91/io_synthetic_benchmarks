
from pathlib import Path
import os
import subprocess
import time
import sys

class task:
    
    def __init__(self,name:str,script:str,resources=None):
        self.name=name
        self.script=script
        self.resources=resources
        
    def __repr__(self) -> str:
        return f"<name={repr(self.name)},script={ repr(self.script)},resources={repr(self.resources)}>"