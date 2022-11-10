
import PySimpleGUI as sg

from billiards.data_manager import DataManager
from billiards.numeric_methods import METHODS

dm = DataManager()


def update_config_window(currentConfig):
    methods = list(METHODS.keys())

    layout = [
        [
            sg.Checkbox(
                "Parallelize", key="parallel",
                default=currentConfig["parallel"]
            )
        ],
        [
            sg.Text("Threads:"),
            sg.In(
                key="threads", default_text=str(currentConfig["threads"]),
                size=(5, 1)
            )
        ],
        [
            sg.Text("Iteration Method:"),
            sg.Combo(
                methods, key="iterationMethod",
                default_value=currentConfig["iterationMethod"]
            )
        ],
        [
            sg.Button("Save", key="save"),
            sg.Button("Cancel", key="cancel")
        ]
    ]

    window = sg.Window("Dynamical Billiards", layout, finalize=True)
    while True:
        event, values = window.read()

        if event == "save":
            currentConfig["parallel"] = values["parallel"]
            currentConfig["threads"] = int(values["threads"])
            currentConfig["iterationMethod"] = values["iterationMethod"]
            break

        if event in (sg.WIN_CLOSED, "cancel"):
            break

    window.close()
    return currentConfig
