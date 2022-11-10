from billiards.gui.windows.choose_boundary import choose_boundary_window
from billiards.gui.windows.choose_simulation import choose_simulation_window
from billiards.gui.windows.save_object import save_object
from billiards.gui.windows.simulation import simulation_window


def new_simulation_flow():
    # Choose boundary
    boundaryName = choose_boundary_window()
    if boundaryName is None:
        return

    # Create simulation
    simulationName = save_object("simulation", boundaryName)

    # Simulate
    simulation_window(simulationName)


def load_simulation_flow():
    # Choose simulation
    simulationName = choose_simulation_window()

    # Simulate
    simulation_window(simulationName)
