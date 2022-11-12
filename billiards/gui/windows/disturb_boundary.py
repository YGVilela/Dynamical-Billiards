
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sympy import limit, parse_expr

from billiards.core.geometry import ComposedPath
from billiards.graphics.mpl import GraphicsMatPlotLib


def disturb_boundary_window(boundary: ComposedPath):
    # Todo: Create disturb function database
    # Challenge: Create a dynamical interface according to parameters

    layout = [
        [
            sg.Text("Function:"), sg.In("0", key="function"),
        ],
        [
            sg.Text("t0:"), sg.In(str(boundary.t0), key="t0", size=(15, 1)),
            sg.Text("t1:"), sg.In(str(boundary.t1), key="t1", size=(15, 1)),
        ],
        [
            sg.Button("Preview:", key="preview")
        ],
        [
            sg.Graph((640, 480), (0, 0), (640, 480), key='canvas')
        ],
        [
            sg.Button("Cancel", key="cancel"),
            sg.Button("Ok", key="ok")
        ]
    ]

    window = sg.Window("Dynamical Billiards", layout, finalize=True)

    figure = GraphicsMatPlotLib(
        boundary
    ).plot(plotPhase=False)
    canvas = FigureCanvasTkAgg(figure, window['canvas'].Widget)
    plot_widget = canvas.get_tk_widget()
    plot_widget.grid(row=0, column=0)

    newBoundary = None
    while True:
        event, values = window.read()

        if event == "ok":
            limitT0 = limit(
                parse_expr(values["function"]),
                "t", parse_expr(values["t0"]),
                "+"
            )
            limitT1 = limit(
                parse_expr(values["function"]),
                "t", parse_expr(values["t1"]),
                "-"
            )
            if limitT0 != 0 or limitT1 != 0:
                proceed = sg.popup_yes_no(
                    "Function limits are not 0, this may cause a\
                    \ndiscontinuity in the boundary.\
                    \nProceed anyway?"
                )

                if proceed != "Yes":
                    continue

            try:
                newBoundary = boundary.normal_disturb(
                    values["function"],
                    [values["t0"], values["t1"]]
                )

            except BaseException as error:
                sg.popup(str(error))

            break

        elif event == "preview":
            try:
                disturbedBoundary = boundary.normal_disturb(
                    values["function"],
                    [values["t0"], values["t1"]]
                )
                figure = GraphicsMatPlotLib(disturbedBoundary).plot(
                    plotPhase=False, fig=figure
                )
                figure.canvas.draw()
            except BaseException as error:
                sg.popup(str(error))

        elif event in (sg.WIN_CLOSED, "cancel"):
            break

    window.close()
    return newBoundary
