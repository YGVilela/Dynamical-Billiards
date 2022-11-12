import PySimpleGUI as sg

from billiards.core.geometry import SimplePath
from billiards.data_manager import DataManager

dm = DataManager()


def parametrization_input_window(currentParametrization: SimplePath = None):
    defaultX = None
    defaultY = None
    defaultT0 = None
    defaultT1 = None

    newPath = None
    pathName = None

    if currentParametrization is not None:
        defaultX = str(currentParametrization.expressionX)
        defaultY = str(currentParametrization.expressionY)
        defaultT0 = str(currentParametrization.t0)
        defaultT1 = str(currentParametrization.t1)

    layout = [
        [
            sg.Text("X Parametrization"),
            sg.In(default_text=defaultX, size=(25, 1), key="paramX")
        ],
        [
            sg.Text("Y Parametrization"),
            sg.In(default_text=defaultY, size=(25, 1), key="paramY")
        ],
        [
            sg.Text("t0"),
            sg.In(default_text=defaultT0, size=(8, 1), key="t0"),
            sg.Text("t1"),
            sg.In(default_text=defaultT1, size=(8, 1), key="t1")
        ],
        [
            sg.Button("Cancel", key="cancel"),
            sg.Button("Ok", key="ok")
        ]
    ]

    window = sg.Window("Dynamical Billiards", layout, finalize=True)

    while True:
        event, values = window.read()

        if event == "ok":
            try:
                newPath = SimplePath(
                    values["t0"],
                    values["t1"],
                    values["paramX"],
                    values["paramY"]
                )
                pathName = str(newPath)
                break

            except BaseException as err:
                sg.popup(err.__str__())
                continue

        elif event in (sg.WIN_CLOSED, "cancel"):
            break

    window.close()
    return newPath, pathName
