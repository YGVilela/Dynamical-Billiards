import os
from typing import Tuple
import PySimpleGUI as sg
from billiards.billiards import Billiard
from billiards.geometry import SimplePath, ComposedPath
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from progress.bar import Bar

from billiards.graphics import GraphicsMatPlotLib
from billiards.input import parse_conditions

# welcome screen

# Constants. Consider changing this...
CLOSE_WINDOW = 0
dataFolder = "data"

# Screens


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
            edit_parametrization()
            window.un_hide()
        elif event == "load":
            window.hide()
            load_simulation()
            window.un_hide()
        elif event == sg.WIN_CLOSED:
            break

    window.close()

# Todo: Edit to be able to rename


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

    windowResponse = None
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
                    nextResponse = edit_initial_conditions(billiard)
                    if nextResponse == CLOSE_WINDOW:
                        windowResponse = nextResponse
                        break
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
            windowResponse = CLOSE_WINDOW
            break

    window.close()
    return windowResponse


def edit_initial_conditions(billiard: Billiard):
    conditionDict = {
        get_initial_condition_string(orbit.initialCondition): index
        for index, orbit in enumerate(billiard.orbits)
    }

    inputLayout = [
        [
            sg.Text("T:"),
            sg.Checkbox(
                "Random", default=True, key="randomT",
                enable_events=True)
        ],
        [
            sg.Text("Range", key="textTRange"),
            sg.In(size=(5, 1), key="tMin", default_text="0"),
            sg.In(size=(5, 1), key="tMax",
                  default_text=str(billiard.boundary.t1))
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

    window = sg.Window("Dynamical Billiards: Initial Conditions", [
        [sg.Column(inputLayout)],
        [
            sg.Button("Back", key="back"),
            sg.Button("Next", key="next")
        ]
    ], finalize=True)

    windowResponse = None
    while True:
        event, values = window.read()
        if event == "back":
            break

        elif event == "next":
            window.hide()
            nextResponse = simulate(billiard)
            if nextResponse == CLOSE_WINDOW:
                windowResponse = nextResponse
                break
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

        elif event == sg.WIN_CLOSED:
            windowResponse = CLOSE_WINDOW
            break

    window.close()
    return windowResponse


def simulate(billiard: Billiard):

    window = sg.Window("Dynamical Billiards: Simulate", [
        [
            sg.Button("Iterate", key="iterate"),
            sg.Button("Save", key="save"),
            sg.Button("Open Image", key="open")
        ],
        [
            sg.Graph((640, 480), (0, 0), (640, 480), key='canvas')
        ],
        [
            sg.Button("Back", key="back"),
            sg.Button("Close", key="close")
        ]
    ], finalize=True)

    graph = GraphicsMatPlotLib(
        billiard.boundary, billiard.orbits
    )
    figure = graph.plot()
    canvas = FigureCanvasTkAgg(figure, window['canvas'].Widget)
    plot_widget = canvas.get_tk_widget()
    plot_widget.grid(row=0, column=0)

    windowResponse = None
    while True:
        event, values = window.read()
        if event == "back":
            break

        elif event == "iterate":
            answer = sg.popup_get_text("How many iterations:")
            if answer is not None:
                try:
                    answerAsInt = int(answer)
                except BaseException as err:
                    sg.popup(err.__str__())

                # Todo: How to report progress?
                bar = Bar(
                    'Iterating', suffix='%(percent)d%% - %(eta)ds',
                    max=answerAsInt * len(billiard.orbits)
                )
                billiard.iterate(iterations=answerAsInt, callback=bar.next)
                bar.finish()

                figure = graph.plot(fig=figure)
                figure.canvas.draw()

        elif event == "save":
            answer = sg.popup_get_text("Simulation name:")
            if answer is not None:
                folder = os.path.join(dataFolder, answer)
                billiard.save(folder)
                sg.popup("Saved successfully!")

        # Bug: After open, iterate doesn't work! Plot fails
        elif event == "open":
            GraphicsMatPlotLib.show(figure)

        elif event in (sg.WIN_CLOSED, "close"):
            windowResponse = CLOSE_WINDOW
            break

    window.close()
    return windowResponse


def load_simulation():
    existingSimulations = os.listdir(dataFolder)

    inputLayout = [
        [
            sg.Text("Select the simulation:"),
        ],
        [
            sg.Listbox(
                values=existingSimulations, size=(40, 20),
                key="simulations", select_mode=sg.LISTBOX_SELECT_MODE_SINGLE
            )
        ]

    ]

    window = sg.Window("Dynamical Billiards: Select the simulation", [
        [sg.Column(inputLayout)],
        [
            sg.Button("Back", key="back"),
            sg.Button("Next", key="next")
        ]
    ], finalize=True)

    windowResponse = None
    while True:
        event, values = window.read()
        if event == "back":
            break

        elif event == "next":
            selectedConditions = values["simulations"]
            path = os.path.join(dataFolder, selectedConditions[0])
            billiard = Billiard.load(path)

            window.hide()
            nextResponse = simulate(billiard)
            if nextResponse == CLOSE_WINDOW:
                windowResponse = nextResponse
                break
            window.un_hide()

        elif event == sg.WIN_CLOSED:
            windowResponse = CLOSE_WINDOW
            break

    window.close()
    return windowResponse


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
