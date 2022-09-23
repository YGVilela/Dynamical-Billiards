import os
from typing import Tuple
import PySimpleGUI as sg
from billiards.billiards import Billiard
from billiards.geometry import SimplePath, ComposedPath
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from billiards.graphics import GraphicsMatPlotLib
from billiards.input import parse_conditions

# welcome screen


def welcome_window():
    layout = [
        [
            sg.Button("New Simulation", key="new"),
            sg.Button("Load Simulation", key="load")
        ]
    ]

    window = sg.Window("Dynamical Billiards", layout)

    while True:
        event, values = window.read()
        if event == "new":
            window.hide()
            name_simulation()
            window.un_hide()
        elif event == "load":
            window.hide()
            load_simulation()
            window.un_hide()
        elif event == sg.WIN_CLOSED:
            break

    window.close()

# Todo: Edit to be able to rename


def name_simulation(curName=None):
    layout = [
        [
            sg.Text("Name"),
            sg.In(size=(25, 1), key="name", default_text=curName)
        ],
        [
            sg.Button("Back", key="back"),
            sg.Button("Next", key="next")
        ]
    ]

    window = sg.Window("Dynamical Billiards: Simulation Name", layout)

    while True:
        event, values = window.read()
        if event == "back":
            break

        elif event == "next":
            window.hide()
            folderName = os.path.join("data", values["name"])
            if os.path.exists(folderName):
                sg.popup("Another simulation with that name already exists!")
            else:
                os.mkdir(folderName)
                edit_parametrization()
            window.un_hide()

        elif event == sg.WIN_CLOSED:
            break

    window.close()


def edit_parametrization(boundary=None):
    if boundary is None:
        boundary = ComposedPath()

    pathDict = {
        get_path_string(component["path"]): index
        for index, component in enumerate(boundary.paths)
    }

    inputLayout = [
        [
            sg.Text("X Parametrization"),
            sg.In(size=(25, 1), key="paramX")
        ],
        [
            sg.Text("Y Parametrization"),
            sg.In(size=(25, 1), key="paramY")
        ],
        [
            sg.Text("t0"),
            sg.In(size=(8, 1), key="t0"),
            sg.Text("t1"),
            sg.In(size=(8, 1), key="t1")
        ],
        [
            sg.Button("Add Parametrization", key="add"),
            sg.Button("Remove Parametrization", key="remove")
        ],
        [
            sg.Listbox(
                values=list(pathDict.keys()), size=(40, 20),
                key="parts", select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE
            )
        ]

    ]

    previewLayout = [
        [sg.Text("Preview:"), ],
        [sg.Graph((640, 480), (0, 0), (640, 480), key='canvas')]
    ]

    window = sg.Window("Dynamical Billiards: Boundary Parametrization", [
        [
            sg.Column(inputLayout),
            sg.VSeperator(),
            # Figure this out!
            sg.Column(previewLayout)
        ],
        [
            sg.Button("Back", key="back"),
            sg.Button("Next", key="next")
        ]
    ], finalize=True)
    figure = GraphicsMatPlotLib(
        boundary
    ).plot(plotPhase=False)
    canvas = FigureCanvasTkAgg(figure, window['canvas'].Widget)
    plot_widget = canvas.get_tk_widget()
    plot_widget.grid(row=0, column=0)

    while True:
        event, values = window.read()
        if event == "back":
            break

        elif event == "next":
            window.hide()
            try:
                if not boundary.is_closed():
                    sg.popup("The boundary must be closed!")
                else:
                    billiard = Billiard(boundary)
                    edit_initial_conditions(billiard)
            except BaseException as err:
                sg.popup(err.__str__())

            window.un_hide()

        elif event == "add":
            try:
                newPath = SimplePath(
                    values["t0"],
                    values["t1"],
                    values["paramX"],
                    values["paramY"]
                )
                pathName = get_path_string(newPath)

            except BaseException as err:
                sg.popup(err.__str__())

            # Todo: check properly!
            if pathName in pathDict:
                sg.popup("Path already in boundary!")
            else:
                boundary.add_path(newPath)
                curValues = list(pathDict.keys())
                pathDict[pathName] = len(curValues)
                curValues.append(pathName)
                window["parts"].update(curValues)

                figure = GraphicsMatPlotLib(boundary).plot(
                    plotPhase=False, fig=figure
                )
                figure.canvas.draw()

        elif event == "remove":
            selectedPaths = values["parts"]
            for pathString in selectedPaths:
                pathIndex = pathDict[pathString]
                del pathDict[pathString]
                boundary.remove_path(pathIndex)
                for key in pathDict:
                    if pathDict[key] > pathIndex:
                        pathDict[key] -= 1

            window["parts"].update(list(pathDict.keys()))
            figure = GraphicsMatPlotLib(boundary).plot(
                plotPhase=False, fig=figure
            )
            figure.canvas.draw()

        elif event == sg.WIN_CLOSED:
            break

    window.close()

# Todo: Above 10 initial conditions, hide preview
# and only display it when prompted


def edit_initial_conditions(billiard: Billiard):
    conditionDict = {
        get_initial_condition_string(orbit.initialCondition): index
        for index, orbit in enumerate(billiard.orbits)
    }

    inputLayout = [
        [
            sg.Text("T:"),
            sg.Checkbox("Random", default=True, key="randomT")
        ],
        [
            sg.Text("Value", visible=False),
            sg.In(size=(5, 1), key="tValue", visible=False),
        ],
        [
            sg.Text("Range"),
            sg.In(size=(5, 1), key="tMin", default_text="0"),
            sg.In(size=(5, 1), key="tMax",
                  default_text=str(billiard.boundary.t1))
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Text("Theta"),
            sg.Checkbox("Random", default=True, key="randomTheta")
        ],
        [
            sg.Text("Value", visible=False),
            sg.In(size=(5, 1), key="thetaValue", visible=False),
        ],
        [
            sg.Text("Range"),
            sg.In(size=(5, 1), key="thetaMin", default_text="0"),
            sg.In(size=(5, 1), key="thetaMax", default_text="pi")
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Text("Samples"),
            sg.In(size=(5, 1), key="instances", default_text="1")
        ],
        [
            sg.Button("Add IC", key="add"),
            sg.Button("Remove IC", key="remove")
        ],
        [
            sg.Listbox(
                values=list(conditionDict.keys()), size=(40, 20),
                key="conditions", select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE
            )
        ]

    ]

    previewLayout = [
        [sg.Text("Preview:"), ],
        [sg.Graph((640, 480), (0, 0), (640, 480), key='canvas')]
    ]

    window = sg.Window("Dynamical Billiards: Boundary Parametrization", [
        [
            sg.Column(inputLayout),
            sg.VSeperator(),
            # Figure this out!
            sg.Column(previewLayout)
        ],
        [
            sg.Button("Back", key="back"),
            sg.Button("Next", key="next")
        ]
    ], finalize=True)
    graphics = GraphicsMatPlotLib(
        billiard.boundary, orbits=billiard.orbits
    )
    figure = graphics.plot(plotPhase=False)
    canvas = FigureCanvasTkAgg(figure, window['canvas'].Widget)
    plot_widget = canvas.get_tk_widget()
    plot_widget.grid(row=0, column=0)

    while True:
        event, values = window.read()
        if event == "back":
            break

        elif event == "next":
            window.hide()
            sg.popup("Nothing for now!")
            window.un_hide()

        elif event == "add":
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

            conditions = parse_conditions(dictionaire)
            for condition in conditions:
                conditionName = get_initial_condition_string(condition)
                if conditionName in conditionDict:
                    sg.popup("Condition " + conditionName + " already added!")
                else:
                    billiard.add_orbit(condition)
                    curValues = list(conditionDict.keys())
                    conditionDict[conditionName] = len(curValues)
                    curValues.append(conditionName)
                    window["conditions"].update(curValues)

            figure = graphics.plot(
                plotPhase=False, fig=figure, plotNextDirection=True
            )
            figure.canvas.draw()

        elif event == "remove":
            selectedConditions = values["conditions"]
            for conditionString in selectedConditions:
                pathIndex = conditionDict[conditionString]
                del conditionDict[conditionString]
                billiard.remove_orbit(pathIndex)
                for key in conditionDict:
                    if conditionDict[key] > pathIndex:
                        conditionDict[key] -= 1

            window["conditions"].update(list(conditionDict.keys()))
            figure = graphics.plot(
                plotPhase=False, fig=figure, plotNextDirection=True
            )
            figure.canvas.draw()

        elif event == sg.WIN_CLOSED:
            break

    window.close()


def load_simulation():
    sg.popup("Not implemented yet!")

# Move this!


def get_path_string(path: SimplePath):
    return "t -> (" + str(path.expressionX) + "," + \
        str(path.expressionY) + "), with t in (" + \
        str(path.t0) + "," + str(path.t1) + ")"


def get_initial_condition_string(initialCondition: Tuple[float, float]):
    return str(initialCondition)


def render_matplotlib_figure(canvas: sg.Canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)

    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg
