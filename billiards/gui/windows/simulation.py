from ast import literal_eval

import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

from billiards.data_manager import DataManager
from billiards.graphics.mpl import GraphicsMatPlotLib
from billiards.gui.windows.get_filter import get_filter_window
from billiards.gui.windows.initial_condition_input import \
    initial_condition_input_window
from billiards.gui.windows.update_config import update_config_window
from billiards.numeric_methods import DEFAULT_METHOD
from billiards.utils.iterator import iterate_parallel, iterate_serial
from billiards.utils.time import sharedTimer

dm = DataManager()


def simulation_window(simulationName: str):
    GraphicsMatPlotLib.clear()
    billiard = dm.load_simulation_billiard(simulationName)

    listValues = [
        str(orbit.initialCondition)
        for orbit in billiard.orbits
    ]

    # Todo: Load this from ?
    configurations = {
        "parallel": False,
        "threads": 2,
        "iterationMethod": DEFAULT_METHOD,
        "automarker": True,
        "markersize": 20
    }
    markerSize = None

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
    figure = graph.plot(orbitIndexes=[], markerSize=markerSize)
    draw_figure_w_toolbar(
        window['canvas'].TKCanvas, figure, window['controlCanvas'].TKCanvas
    )

    while True:
        event, values = window.read()

        if event == "iterate":

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

        elif event == "saveSimulation":
            dm.upsert_simulation_orbits(simulationName, billiard.orbits)
            window.TKroot.title("Dynamical Billiards")

        elif event == "plotTrajectory":
            orbitIndexes = window["conditions"].GetIndexes()

            plotFigure = graph.plot(
                orbitIndexes=orbitIndexes,
                plotBoundary=True, plotPhase=False,
                markerSize=markerSize
            )
            plotFigure.show()

        elif event == "plotOrbit":
            orbitIndexes = window["conditions"].GetIndexes()

            plotFigure = graph.plot(
                orbitIndexes=orbitIndexes,
                plotBoundary=False, plotPhase=True,
                markerSize=markerSize
            )
            plotFigure.show()

        elif event == "preview":
            orbitIndexes = window["conditions"].GetIndexes()

            figure = graph.plot(
                orbitIndexes=orbitIndexes, fig=figure,
                markerSize=markerSize
            )
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
            tFilter, thetaFilter = get_filter_window(billiard.boundary.length)
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
            if not configurations["automarker"]:
                markerSize = configurations["markersize"]

        elif event in (sg.WIN_CLOSED, "close"):
            break

    window.close()


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
