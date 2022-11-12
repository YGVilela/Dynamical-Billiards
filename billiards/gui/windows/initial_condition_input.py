
import PySimpleGUI as sg

from billiards.data_manager import DataManager
from billiards.utils.misc import parse_conditions

dm = DataManager()


def initial_condition_input_window(maxT):
    layout = [
        [
            sg.Text("T:"),
            sg.Checkbox(
                "Random", default=True, key="randomT",
                enable_events=True)
        ],
        [
            sg.Text("Range", key="textTRange"),
            sg.In(size=(5, 1), key="tMin", default_text="0"),
            sg.In(size=(5, 1), key="tMax", default_text=str(maxT))
        ],
        [
            sg.Text("Value"),
            sg.In(size=(5, 1), key="tValue", visible=False),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Text("Theta"),
            sg.Checkbox("Random", default=True, key="randomTheta",
                        enable_events=True)
        ],
        [
            sg.Text("Range"),
            sg.In(size=(5, 1), key="thetaMin", default_text="0"),
            sg.In(size=(5, 1), key="thetaMax", default_text="pi")
        ],
        [
            sg.Text("Value"),
            sg.In(size=(5, 1), key="thetaValue", visible=False),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Text("Samples"),
            sg.In(size=(5, 1), key="instances", default_text="1")
        ],
        [
            sg.Button("Cancel", key="cancel"),
            sg.Button("Add Conditions", key="add")
        ]
    ]

    window = sg.Window("Dynamical Billiards", layout, finalize=True)

    newConditions = []
    while True:
        event, values = window.read()

        if event == "add":
            dictionaire = {}
            dictionaire["instances"] = int(values["instances"])
            if values["randomT"]:
                dictionaire["t"] = "Random"
                dictionaire["tRange"] = [values["tMin"], values["tMax"]]
            else:
                dictionaire["t"] = values["tValue"]

            if values["randomTheta"]:
                dictionaire["theta"] = "Random"
                dictionaire["thetaRange"] = [
                    values["thetaMin"], values["thetaMax"]
                ]
            else:
                dictionaire["theta"] = values["thetaValue"]

            newConditions = parse_conditions(dictionaire)

            break

        elif event == "randomT":
            window["tValue"].update(visible=not window["tValue"].visible)
            window["tMin"].update(visible=not window["tMin"].visible)
            window["tMax"].update(visible=not window["tMax"].visible)

        elif event == "randomTheta":
            window["thetaValue"].update(
                visible=not window["thetaValue"].visible
            )
            window["thetaMin"].update(visible=not window["thetaMin"].visible)
            window["thetaMax"].update(visible=not window["thetaMax"].visible)

        elif event in (sg.WIN_CLOSED, "cancel"):
            break

    window.close()
    return newConditions
