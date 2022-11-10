
import PySimpleGUI as sg

from billiards.data_manager import DataManager

dm = DataManager()


def choose_simulation_window():
    existingSimulations = dm.list_simulations()

    # Todo: Preview the simulation
    listComponent = [
        sg.Listbox(
            existingSimulations, key="simulationList", enable_events=True,
            size=(40, 20)
        )
    ]

    layout = [
        listComponent,
        [
            sg.Button("Cancel", key="cancel"),
            sg.Button("Select simulation", key="select"),
        ]
    ]

    window = sg.Window("Dynamical Billiards", layout, finalize=True)

    simulationName = None
    while True:
        event, values = window.read()

        if event == "select":
            selected = values["simulationList"][0]
            if selected is None:
                sg.popup("No simulation selected!")
                continue

            simulationName = selected
            break

        elif event in (sg.WIN_CLOSED, "cancel"):
            break

    window.close()
    return simulationName
