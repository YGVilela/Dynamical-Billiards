import json
import os
from typing import Tuple
import PySimpleGUI as sg
from billiards.billiards import Billiard, iterate_parallel, iterate_serial
from billiards.geometry import SimplePath, ComposedPath
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

from billiards.graphics import GraphicsMatPlotLib
from billiards.input import parse_conditions
from billiards.time import sharedTimer

# Constants. Consider changing this...
constants = {
    "CLOSE_WINDOW": 0,
    "DataFolder": "data"
}


def welcome_window(dataFolder: str):
    constants["DataFolder"] = dataFolder

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


def edit_parametrization(boundary=None):
    if boundary is None:
        boundary = ComposedPath()

    pathDict = {
        get_path_string(component["path"]): index
        for index, component in enumerate(boundary.paths)
    }

    inputLayout = [
        [
            sg.Button("Load Boundary", key="load")
        ],
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
                    if nextResponse == constants["CLOSE_WINDOW"]:
                        windowResponse = nextResponse
                        break
            except BaseException as err:
                sg.popup(err.__str__())

            window.un_hide()

        elif event == "load":
            jsonFile = sg.popup_get_file("Sellect the boundary json:")
            if jsonFile is not None:
                dictionary = json.load(open(jsonFile))
                boundary = ComposedPath.from_json(dictionary)

                pathDict = {
                    get_path_string(component["path"]): index
                    for index, component in enumerate(boundary.paths)
                }
                window["parts"].update(pathDict)
                figure = GraphicsMatPlotLib(boundary).plot(
                    plotPhase=False, fig=figure
                )
                figure.canvas.draw()

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
            windowResponse = constants["CLOSE_WINDOW"]
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
            if nextResponse == constants["CLOSE_WINDOW"]:
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
            windowResponse = constants["CLOSE_WINDOW"]
            break

    window.close()
    return windowResponse


def simulate(billiard: Billiard):
    conditionDict = {
        get_initial_condition_string(orbit.initialCondition): index
        for index, orbit in enumerate(billiard.orbits)
    }

    inputLayout = [
        [
            sg.Text("Iterations"),
            sg.In("1", size=(5, 1), key="iterations")
        ],
        [
            sg.Button("Iterate", key="iterate")
        ],
        [
            sg.Button("Save simulation", key="save")
        ],
        [
            sg.Checkbox("Parallelize", key="parallel", enable_events=True)
        ],
        [
            sg.Text("Threads"),
            sg.In("2", size=(5, 1), key="threads", visible=False)
        ],
        [
            sg.Button("Plot All Orbits", key="plotOrbit"),
            sg.Button("Plot All Trajectories", key="plotTrajectory")
        ],
        [
            sg.Button("Preview Selected Orbits & Trajectories", key="preview")
        ],
        [
            sg.Button("Select All", key="selectAll"),
            sg.Button("Clear Selection", key="clearSelection")
        ],
        [
            sg.Listbox(
                values=list(conditionDict.keys()), size=(40, 20),
                key="conditions", select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE
            )
        ]
    ]

    plotLayout = [
        [sg.Canvas(key="controlCanvas")],
        [
            # Todo: change dimensions according to inputs!
            sg.Graph((640, 480), (0, 0), (640, 480), key='canvas')
        ]
    ]

    window = sg.Window("Dynamical Billiards: Simulate", [
        [
            sg.Column(inputLayout),
            sg.VerticalSeparator(),
            sg.Column(plotLayout)
        ],
        [
            sg.Button("Back", key="back"),
            sg.Button("Close", key="close")
        ]
    ], finalize=True)

    graph = GraphicsMatPlotLib(
        billiard.boundary, billiard.orbits
    )
    figure = graph.plot(orbitIndexes=[])
    draw_figure_w_toolbar(
        window['canvas'].TKCanvas, figure, window['controlCanvas'].TKCanvas
    )

    windowResponse = None
    while True:
        event, values = window.read()
        if event == "back":
            break

        elif event == "iterate":
            # Todo: Figure out a way to disable without minimizing
            window.disable()

            iterations = int(values["iterations"])

            # Todo: Figure a common way of showing the bar
            if values["parallel"]:
                threads = int(values["threads"])

                idTimer = sharedTimer.start_operation("iterate_parallel")
                iterate_parallel(billiard, iterations, threads, GUI=True)
                sharedTimer.end_operation("iterate_parallel", idTimer)

            else:
                idTimer = sharedTimer.start_operation("iterate_serial")
                iterate_serial(billiard, iterations, GUI=True)
                sharedTimer.end_operation("iterate_serial", idTimer)

            window.enable()

        elif event == "save":
            sg.popup_get_folder
            answer = sg.popup_get_text("Simulation name:")
            if answer is not None:
                folder = os.path.join(constants["DataFolder"], answer)
                billiard.save(folder)
                sg.popup("Saved successfully!")

        elif event == "parallel":
            window["threads"].update(visible=not window["threads"].visible)

        elif event == "plotTrajectory":
            plotFigure = graph.plot(plotBoundary=True, plotPhase=False)
            plotFigure.show()

        elif event == "plotOrbit":
            plotFigure = graph.plot(plotBoundary=False, plotPhase=True)
            plotFigure.show()

        elif event == "preview":
            selectedConditions = values["conditions"]
            orbitIndexes = [
                conditionDict[conditionStr]
                for conditionStr in selectedConditions
            ]

            figure = graph.plot(orbitIndexes=orbitIndexes, fig=figure)
            draw_figure_w_toolbar(
                window['canvas'].TKCanvas,
                figure, window['controlCanvas'].TKCanvas
            )

        elif event == "selectAll":
            indexes = list(range(len(billiard.orbits)))
            window["conditions"].update(set_to_index=indexes)

        elif event == "clearSelection":
            window["conditions"].update(set_to_index=[])

        elif event in (sg.WIN_CLOSED, "close"):
            windowResponse = constants["CLOSE_WINDOW"]
            break

    window.close()
    return windowResponse


def load_simulation():
    existingSimulations = os.listdir(constants["DataFolder"])

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
            path = os.path.join(constants["DataFolder"], selectedConditions[0])
            billiard = Billiard.load(path)

            window.hide()
            nextResponse = simulate(billiard)
            if nextResponse == constants["CLOSE_WINDOW"]:
                windowResponse = nextResponse
                break
            window.un_hide()

        elif event == sg.WIN_CLOSED:
            windowResponse = constants["CLOSE_WINDOW"]
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


class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)


def draw_figure_w_toolbar(
    canvas: sg.Canvas,
    figure,
    canvas_toolbar: sg.Canvas
):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(figure, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)
