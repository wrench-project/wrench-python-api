import json
from pywrench.exception import WRENCHException
from pywrench.simulation_item import SimulationItem


class ComputeService(SimulationItem):
    """
    WRENCH Compute Service class
    """

    def submit_standard_job(self, standard_job):
        return self.simulation.submit_standard_job(standard_job.get_name(), self.name)




