import PySimpleGUI as sg

from billiards.gui.flows import load_simulation_flow, new_simulation_flow


def main_window():
    layout = [
        [
            sg.Button("New Simulation", key="new")
        ],
        [
            sg.Button("Load Simulation", key="load")
        ]
    ]

    window = sg.Window("Dynamical Billiards", layout, finalize=True)

    while True:
        event, values = window.read()
        if event == "new":
            window.hide()
            new_simulation_flow()
            window.un_hide()
        elif event == "load":
            window.hide()
            load_simulation_flow()
            window.un_hide()
        elif event == sg.WIN_CLOSED:
            break

    window.close()
