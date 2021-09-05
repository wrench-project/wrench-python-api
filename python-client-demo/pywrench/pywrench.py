from pywrench.simulation import WRENCHSimulation
from pywrench.exception import WRENCHException


def start_simulation(platform_file_path, controller_hostname, daemon_host="localhost", daemon_port=8101):
    """
    Start a new simulation
    :param platform_file_path: path of a file that contains the simulated platform's description in XML
    :param controller_hostname: the name of the (simulated) host in the platform on which the simulation concroller will run
    :param daemon_host: the name of the host on which the WRENCH daemon is running
    :param daemon_port: port number on which the WRENCH daemon is listening
    :return:
    """
    try:
        return WRENCHSimulation(platform_file_path, controller_hostname, daemon_host, daemon_port)
    except WRENCHException:
        raise

