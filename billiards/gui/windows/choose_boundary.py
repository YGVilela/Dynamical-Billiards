
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from billiards.core.geometry import ComposedPath
from billiards.data_manager import DataManager
from billiards.graphics.mpl import GraphicsMatPlotLib
from billiards.gui.windows.create_boundary import create_boundary_window

dm = DataManager()


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
