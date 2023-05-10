
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from billiards.core.geometry import ComposedPath
from billiards.data_manager import DataManager
from billiards.graphics.mpl import GraphicsMatPlotLib
from billiards.gui.windows.parametrization_input import \
    parametrization_input_window
from billiards.gui.windows.save_object import save_object

dm = DataManager()


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
            valuesList.pop(pathIndex)
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
