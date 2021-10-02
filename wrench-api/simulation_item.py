class SimulationItem:
    """
    WRENCH Simulation Item class
    """

    def __init__(self, simulation, name):
        """
        Constructor

        :param simulation: simulation object
        :param name: simulation item name
        """
        self.simulation = simulation
        self.name = name

    def get_name(self):
        return self.name

    


