
import PySimpleGUI as sg

from sympy import parse_expr

from billiards.data_manager import DataManager

dm = DataManager()


def get_filter_window(boundaryLength):
    layout = [
        [
            sg.Text("t between"),
            sg.In("0", key="tMin", size=(7, 1)),
            sg.Text("and"),
            sg.In(str(boundaryLength), key="tMax", size=(7, 1))
        ],
        [
            sg.Text("theta between"),
            sg.In("0", key="thetaMin", size=(7, 1)),
            sg.Text("and"),
            sg.In("pi", key="thetaMax", size=(7, 1))
        ],
        [
            sg.Button("Filter", key="filter"),
            sg.Button("Cancel", key="cancel")
        ]
    ]

    window = sg.Window("Dynamical Billiards", layout, finalize=True)

    tRange = None
    thetaRange = None
    while True:
        event, values = window.read()

        if event == "filter":
            tMinExpr = values["tMin"]
            tMaxExpr = values["tMax"]
            thetaMinExpr = values["thetaMin"]
            thetaMaxExpr = values["thetaMax"]

            try:
                tMin = float(parse_expr(tMinExpr).evalf())
                tMax = float(parse_expr(tMaxExpr).evalf())
                thetaMin = float(parse_expr(thetaMinExpr).evalf())
                thetaMax = float(parse_expr(thetaMaxExpr).evalf())

                tRange = (tMin, tMax)
                thetaRange = (thetaMin, thetaMax)
                break
            except BaseException as err:
                sg.popup(err.__str__())

        elif event in (sg.WIN_CLOSED, "cancel"):
            break

    window.close()

    return tRange, thetaRange
