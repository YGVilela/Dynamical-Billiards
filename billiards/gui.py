from ast import literal_eval
import json
import os
from typing import Tuple
import PySimpleGUI as sg
from billiards.billiards import Billiard, iterate_parallel, iterate_serial
from billiards.geometry import SimplePath, ComposedPath
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from sympy import parse_expr

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


def parametrization_input(currentParametrization: SimplePath = None):
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

    window = sg.Window("Dynamical Billiards: Boundary Parametrization",
                       layout, finalize=True
                       )

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
                pathName = get_path_string(newPath)
                break

            except BaseException as err:
                sg.popup(err.__str__())
                continue

        elif event in (sg.WIN_CLOSED, "cancel"):
            break

    window.close()
    return newPath, pathName


def edit_parametrization(boundary=None):
    if boundary is None:
        boundary = ComposedPath()

    valuesList = [
        get_path_string(component["path"])
        for component in boundary.paths
    ]
    pathSet = set(valuesList)

    inputLayout = [
        [
            sg.In(visible=False, key="saveBoundary", enable_events=True),
            sg.In(visible=False, key="loadBoundary", enable_events=True)
        ],
        [
            sg.FileSaveAs("Save Boundary", target="saveBoundary"),
            sg.FileBrowse("Load Boundary", target="loadBoundary",
                          enable_events=True)
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Button("Add", key="add"),
            sg.Button("Edit", key="edit"),
            sg.Button("Remove", key="remove")
        ],
        [
            sg.Listbox(
                values=valuesList, size=(40, 20),
                key="parts", select_mode=sg.LISTBOX_SELECT_MODE_SINGLE
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

        elif event == "saveBoundary":
            savePath = values["saveBoundary"]
            print("saving", savePath)
            boundaryJson = boundary.to_json()
            with open(savePath, 'w', encoding='utf-8') as f:
                json.dump(boundaryJson, f, ensure_ascii=False, indent=4)

        elif event == "loadBoundary":
            loadPath = values["loadBoundary"]
            print("loading", loadPath)
            dictionary = json.load(open(loadPath))
            boundary = ComposedPath.from_json(dictionary)

            valuesList = [
                get_path_string(component["path"])
                for component in boundary.paths
            ]
            pathSet = set(valuesList)

            window["parts"].update(valuesList)
            figure = GraphicsMatPlotLib(boundary).plot(
                plotPhase=False, fig=figure
            )
            figure.canvas.draw()

        elif event == "add":
            newPath, pathName = parametrization_input()
            if newPath is None:
                continue

            # Todo: check properly!
            if pathName in pathSet:
                sg.popup("Path already in boundary!")
            else:
                boundary.add_path(newPath)
                pathSet.add(pathName)
                valuesList.append(pathName)
                window["parts"].update(valuesList)

                figure = GraphicsMatPlotLib(boundary).plot(
                    plotPhase=False, fig=figure
                )
                figure.canvas.draw()

        elif event == "remove":
            indexes = window["parts"].GetIndexes()
            if len(indexes) == 0:
                continue

            pathIndex = indexes[0]
            boundary.remove_path(pathIndex)

            removedStr = valuesList.pop(pathIndex)
            pathSet.remove(removedStr)
            window["parts"].update(valuesList)
            figure = GraphicsMatPlotLib(boundary).plot(
                plotPhase=False, fig=figure
            )
            figure.canvas.draw()

        elif event == "edit":
            indexes = window["parts"].GetIndexes()
            if len(indexes) == 0:
                continue

            pathIndex = indexes[0]
            currentPath = boundary.paths[pathIndex]["path"]
            newPath, pathName = parametrization_input(currentPath)

            if newPath is None:
                continue

            if pathName in pathSet:
                sg.popup("Path already in boundary!")
            else:
                boundary.update_path(pathIndex, newPath)

                pathSet.remove(valuesList[pathIndex])
                pathSet.add(pathName)

                valuesList[pathIndex] = pathName
                window["parts"].update(valuesList)

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


def simulate(billiard: Billiard, name: str = "unnamed"):
    listValues = [
        get_initial_condition_string(orbit.initialCondition)
        for orbit in billiard.orbits
    ]

    inputLayout = [
        [
            sg.Button("Save simulation", key="saveSimulation")
        ],
        [
            sg.Text("Iterations"),
            sg.In("1", size=(5, 1), key="iterations"),
            sg.Button("Iterate", key="iterate")
        ],
        [
            sg.Checkbox("Parallelize", key="parallel", enable_events=True),
            sg.Text("Threads"),
            sg.In("2", size=(5, 1), key="threads", visible=False)
        ],
        [
            sg.Button("Plot Orbits", key="plotOrbit"),
            sg.Button("Plot Trajectories", key="plotTrajectory")
        ],
        [
            sg.Button("Preview Orbits & Trajectories", key="preview")
        ],
        [
            sg.Button("Select All", key="selectAll"),
            sg.Button("Select In Range", key="filterSelection"),
            sg.Button("Clear Selection", key="clearSelection")
        ],
        [
            sg.Listbox(
                listValues, size=(40, 20), key="conditions",
                select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE
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

    window = sg.Window(f"Dynamical Billiards: Simulate {name}", [
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

            window.TKroot.title(
                f"[Unsaved Changes] Dynamical Billiards: Simulate {name}"
            )
            window.enable()

        elif event == "saveSimulation":
            canceled = False
            if name == "unnamed":
                while True:
                    newName = sg.popup_get_text("Simulation name:")

                    if newName is None:
                        canceled = True
                        break

                    if newName in ("unnamed", ""):
                        sg.popup(f"Invalid simulation name {newName}")

                    folder = os.path.join(
                        constants["DataFolder"], f"{newName}"
                    )
                    if os.path.exists(folder):
                        overwrite = sg.popup_yes_no(
                            "A simulation with that name already exists.\
                            \n Do you want to overwrite it?"
                        )
                        if overwrite == "Yes":
                            name = newName
                            break
                    else:
                        name = newName
                        break

            if canceled:
                sg.popup("The simulation was NOT saved.")

            else:
                folder = os.path.join(
                    constants["DataFolder"], f"{name}"
                )
                billiard.save(folder)
                sg.popup("The simulation was saved successfully!")
                window.TKroot.title(
                    f"Dynamical Billiards: Simulate {name}"
                )

        elif event == "parallel":
            window["threads"].update(visible=not window["threads"].visible)

        elif event == "plotTrajectory":
            orbitIndexes = window["conditions"].GetIndexes()

            plotFigure = graph.plot(
                orbitIndexes=orbitIndexes,
                plotBoundary=True, plotPhase=False
            )
            plotFigure.show()

        elif event == "plotOrbit":
            orbitIndexes = window["conditions"].GetIndexes()

            plotFigure = graph.plot(
                orbitIndexes=orbitIndexes,
                plotBoundary=False, plotPhase=True
            )
            plotFigure.show()

        elif event == "preview":
            orbitIndexes = window["conditions"].GetIndexes()

            figure = graph.plot(orbitIndexes=orbitIndexes, fig=figure)
            draw_figure_w_toolbar(
                window['canvas'].TKCanvas,
                figure, window['controlCanvas'].TKCanvas
            )

        elif event == "selectAll":
            window["conditions"].update(
                set_to_index=list(range(len(listValues)))
            )

        elif event == "clearSelection":
            window["conditions"].update(set_to_index=[])

        elif event == "filterSelection":
            tFilter, thetaFilter = get_filter(billiard.boundary.length)
            if tFilter is None or thetaFilter is None:
                continue

            def filterFunc(initialConditionStr):
                t, theta = str_to_initial_condition(initialConditionStr)
                tInRange = tFilter[0] <= t <= tFilter[1]
                thetaInRange = thetaFilter[0] <= theta <= thetaFilter[1]

                return tInRange and thetaInRange

            selectedIndexes = [
                index
                for index in range(len(listValues))
                if filterFunc(listValues[index])
            ]

            window["conditions"].update(set_to_index=selectedIndexes)

        elif event in (sg.WIN_CLOSED, "close"):
            windowResponse = constants["CLOSE_WINDOW"]
            break

    window.close()
    return windowResponse


def get_filter(boundaryLength):
    window = sg.Window("Select the filter", [
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
    ])

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
            nextResponse = simulate(billiard, selectedConditions[0])
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


def str_to_initial_condition(initialConditionStr):
    return literal_eval(initialConditionStr)


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
