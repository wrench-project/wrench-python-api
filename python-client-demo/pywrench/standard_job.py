import requests
import json
from pywrench.exception import WRENCHException
from pywrench.simulation_item import SimulationItem


class StandardJob(SimulationItem):
    """
    WRENCH Standard Job class
    """
    def get_tasks(self):
        return self.simulation.standard_job_get_tasks(self.name)




