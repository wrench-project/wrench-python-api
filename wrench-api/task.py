import requests
import json
from pywrench.exception import WRENCHException
from pywrench.simulation_item import SimulationItem

class Task(SimulationItem):
    """
    WRENCH Task class
    """

    def get_flops(self):
        return self.simulation.task_get_flops(self.name)

    def get_min_num_cores(self):
        return self.simulation.task_get_min_num_cores(self.name)

    def get_max_num_cores(self):
        return self.simulation.task_get_max_num_cores(self.name)

    def get_memory(self):
        return self.simulation.task_get_memory(self.name)



