from ast import literal_eval
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from sympy import parse_expr
from billiards.billiards import iterate_parallel, iterate_serial


from billiards.data_manager import DataManager, ObjectExistsException
from billiards.geometry import ComposedPath, SimplePath
from billiards.graphics import GraphicsMatPlotLib
from billiards.input import parse_conditions
from billiards.time import sharedTimer

# Todo: Allow user to update the variables on a configurations screen
dm = DataManager()


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
            new_simulation()
            window.un_hide()
        elif event == "load":
            window.hide()
            load_simulation()
            window.un_hide()
        elif event == sg.WIN_CLOSED:
            break

    window.close()


def new_simulation():
    # Choose boundary
    boundaryName = choose_boundary_window()
    if boundaryName is None:
        return

    # Create simulation
    simulationName = save_object("simulation", boundaryName)

    # Simulate
    simulation_window(simulationName)


def load_simulation():
    # Choose simulation
    simulationName = choose_simulation_window()

    # Simulate
    simulation_window(simulationName)


def choose_boundary_window():
    boundaryName = None
    currentBoundary = ComposedPath([])
    existingBoundaries = dm.list_boundaries()

    # Todo: Implement this component as an "Element" (class from PySimpleGUI)
    listComponent = [
        sg.Listbox(
            existingBoundaries, key="boundaryList", enable_events=True,
            size=(40, 20)
        ),
        sg.VerticalSeparator(),
        sg.Graph((640, 480), (0, 0), (640, 480), key='canvas')
    ]

    layout = [
        [
            sg.Button("Select boundary", key="select"),
            sg.Button("Create new boundary", key="new"),
            sg.Button("Create boundary from selection", key="fromSelection")
        ],
        listComponent,
        [sg.Button("Cancel", key="cancel")]
    ]

    window = sg.Window("Dynamical Billiards", layout, finalize=True)
    figure = GraphicsMatPlotLib(
        currentBoundary
    ).plot(plotPhase=False)
    canvas = FigureCanvasTkAgg(figure, window['canvas'].Widget)
    plot_widget = canvas.get_tk_widget()
    plot_widget.grid(row=0, column=0)

    while True:
        event, values = window.read()

        if event == "select":
            selected = values["boundaryList"][0]
            if selected is None:
                sg.popup("No boundary selected!")
                continue

            boundaryName = selected
            break

        elif event == "new":
            window.hide()
            boundaryName = create_boundary_window()
            if boundaryName is not None:
                break

            window.un_hide()

        elif event == "fromSelection":
            selected = values["boundaryList"][0]
            if selected is None:
                sg.popup("No boundary selected!")
                continue

            window.hide()

            boundaryName = create_boundary_window(selected)
            if boundaryName is not None:
                break

            window.un_hide()

        elif event == "boundaryList":
            selected = values["boundaryList"][0]
            print(f"Loading {selected}")
            currentBoundary = dm.load_boundary(selected)
            print(currentBoundary)
            figure = GraphicsMatPlotLib(currentBoundary).plot(
                plotPhase=False, fig=figure
            )
            figure.canvas.draw()

        elif event in (sg.WIN_CLOSED, "cancel"):
            break

    window.close()
    return boundaryName


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


def simulation_window(simulationName: str):
    billiard = dm.load_simulation_billiard(simulationName)

    listValues = [
        str(orbit.initialCondition)
        for orbit in billiard.orbits
    ]

    # Todo: Load this from ?
    configurations = {
        "parallel": False,
        "threads": 2,
        "iterationMethod": "Newton"
    }

    inputLayout = [
        [
            sg.Button("Save simulation", key="saveSimulation"),
            sg.Button("Configure simulation", key="configureSimulation")
        ],
        [
            sg.Text("Iterations"),
            sg.In("1", size=(5, 1), key="iterations"),
            sg.Button("Iterate", key="iterate")
        ],
        [
            sg.Button("Add Initial Condition", key="addIC")
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

    layout = [
        [
            sg.Column(inputLayout),
            sg.VerticalSeparator(),
            sg.Column(plotLayout)
        ],
        [
            sg.Button("Close", key="close")
        ]
    ]

    window = sg.Window("Dynamical Billiards", layout, finalize=True)

    graph = GraphicsMatPlotLib(
        billiard.boundary, billiard.orbits
    )
    figure = graph.plot(orbitIndexes=[])
    draw_figure_w_toolbar(
        window['canvas'].TKCanvas, figure, window['controlCanvas'].TKCanvas
    )

    while True:
        event, values = window.read()

        if event == "iterate":
            # Todo: Figure out a way to disable without minimizing
            window.disable()

            iterations = int(values["iterations"])
            method = configurations["iterationMethod"]
            print(f"Iterating with config: {str(configurations)}")

            # Todo: Figure a common way of showing the bar
            if configurations["parallel"]:
                threads = configurations["threads"]

                idTimer = sharedTimer.start_operation("iterate_parallel")
                iterate_parallel(
                    billiard, iterations, threads, GUI=True, method=method
                )
                sharedTimer.end_operation("iterate_parallel", idTimer)

            else:
                idTimer = sharedTimer.start_operation("iterate_serial")
                iterate_serial(billiard, iterations, GUI=True, method=method)
                sharedTimer.end_operation("iterate_serial", idTimer)

            window.TKroot.title(
                "[Unsaved Iterations] Dynamical Billiards"
            )
            window.enable()

        elif event == "saveSimulation":
            dm.upsert_simulation_orbits(simulationName, billiard.orbits)
            window.TKroot.title("Dynamical Billiards")

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
                t, theta = literal_eval(initialConditionStr)
                tInRange = tFilter[0] <= t <= tFilter[1]
                thetaInRange = thetaFilter[0] <= theta <= thetaFilter[1]

                return tInRange and thetaInRange

            selectedIndexes = [
                index
                for index in range(len(listValues))
                if filterFunc(listValues[index])
            ]

            window["conditions"].update(set_to_index=selectedIndexes)

        elif event == "addIC":
            newConditions = initial_condition_input_window(
                billiard.boundary.t1)

            if len(newConditions) == 0:
                continue

            filteredConditions = list(
                filter(lambda c: str(c) not in listValues, newConditions)
            )

            if len(filteredConditions) == 0:
                sg.popup("The given conditions are already in the simulation.")
                continue

            conditionStrings = [
                str(condition) for condition in filteredConditions
            ]

            listValues += conditionStrings
            window["conditions"].update(listValues)
            billiard.add_orbits(filteredConditions)

        elif event == "configureSimulation":
            configurations = update_config_window(configurations)

        elif event in (sg.WIN_CLOSED, "close"):
            break

    window.close()


def update_config_window(currentConfig):
    # Todo: Load this from the numeric_methods lib
    methods = [
        "Bissection",
        "Newton",
        "Regula Falsi"
    ]

    input = [
        [
            sg.Checkbox(
                "Parallelize", key="parallel",
                default=currentConfig["parallel"]
            )
        ],
        [
            sg.Text("Threads:"),
            sg.Input(
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

    window = sg.Window("Dynamical Billiards", input, finalize=True)
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


def initial_condition_input_window(maxT):
    input = [
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

    window = sg.Window("Dynamical Billiards", input, finalize=True)

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


def create_boundary_window(baseBoundaryName: str = None):
    if baseBoundaryName is None:
        boundary = ComposedPath()
    else:
        boundary = dm.load_boundary(baseBoundaryName)

    valuesList = [
        str(component["path"])
        for component in boundary.paths
    ]

    inputLayout = [
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

    layout = [
        [
            sg.Column(inputLayout),
            sg.VSeperator(),
            sg.Column(previewLayout)
        ],
        [
            sg.Button("Cancel", key="cancel"),
            sg.Button("Create Boundary", key="create")
        ]
    ]

    window = sg.Window("Dynamical Billiards", layout, finalize=True)

    figure = GraphicsMatPlotLib(
        boundary
    ).plot(plotPhase=False)
    canvas = FigureCanvasTkAgg(figure, window['canvas'].Widget)
    plot_widget = canvas.get_tk_widget()
    plot_widget.grid(row=0, column=0)

    boundaryName = None
    while True:
        event, values = window.read()

        if event == "create":
            if not boundary.is_closed():
                sg.popup("The boundary must be closed!")
                continue

            # Save the boundary
            boundaryName = save_object("boundary", boundary)

            if boundaryName is not None:
                break

        elif event == "add":
            newPath, pathName = parametrization_input_window()
            if newPath is None:
                continue

            # Todo: check properly!
            if pathName in valuesList:
                sg.popup("Path already in boundary!")
            else:
                boundary.add_path(newPath)
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
            newPath, pathName = parametrization_input_window(currentPath)

            if newPath is None:
                continue

            if pathName in valuesList:
                sg.popup("Path already in boundary!")
            else:
                boundary.update_path(pathIndex, newPath)

                valuesList[pathIndex] = pathName
                window["parts"].update(valuesList)

                figure = GraphicsMatPlotLib(boundary).plot(
                    plotPhase=False, fig=figure
                )
                figure.canvas.draw()

        elif event in (sg.WIN_CLOSED, "cancel"):
            break

    window.close()
    return boundaryName


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
                pathName = str(newPath)
                break

            except BaseException as err:
                sg.popup(err.__str__())
                continue

        elif event in (sg.WIN_CLOSED, "cancel"):
            break

    window.close()
    return newPath, pathName


def save_object(objType: str, *args, overwriteByDefault=False):
    if objType == "boundary":
        func = dm.create_boundary
    elif objType == "simulation":
        func = dm.create_simulation
    else:
        raise Exception(f"Save for {objType} not implemented.")

    objName = None
    while True:
        objName = sg.popup_get_text(f"Name your {objType}:")
        if objName is None:
            break

        try:
            func(objName, *args, overwrite=overwriteByDefault)

            break
        except ObjectExistsException:
            res = sg.popup_yes_no(
                f"A(n) {objType} named {objName} already exists.\n\
                Do you want to overwrite it?")

            if res == "Yes":
                func(objName, *args, overwrite=True)
                break

    return objName


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
