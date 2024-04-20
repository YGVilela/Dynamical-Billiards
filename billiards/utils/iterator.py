
from multiprocess import Manager, Process
from progress.bar import Bar
from PySimpleGUI import ProgressBar, Window, Text

from billiards.core.dynamics import Billiard


def iterate_serial(
    billiard: Billiard,
    iterations: int,
    GUI: bool = False,
    method: str = None
):
    totalIter = iterations * len(billiard.orbits)
    if GUI:
        window = Window(
            "Iterating...",
            layout=[[ProgressBar(totalIter, size=(50, 10), key="progress")]],
            finalize=True
        )
    else:
        bar = Bar(
            'Iterating', suffix='%(percent)d%% - %(eta)ds',
            max=totalIter
        )

    currentProgress = [0]

    def cb():
        if GUI:
            currentProgress[0] += 1
            window["progress"].update(currentProgress[0])
        else:
            bar.next()

    billiard.iterate(
        iterations=iterations,
        callback=cb,
        method=method
    )

    if GUI:
        window.close()
    else:
        bar.finish()


def iterate_parallel(
    billiard: Billiard,
    iterations: int,
    threads: int,
    GUI: bool = False,
    method: str = None
):
    manager = Manager()
    queue = manager.Queue()

    def cb():
        queue.put(1)

    # TODO: Fix parallel bar problem
    def tick(queue, totalIter):
        currentProgress = 0
        #     window = Window(
        #         "Iterating...",
        #         layout=[
        #             [ProgressBar(totalIter, size=(50, 10), key="progress")]
        #         ],
        #         finalize=True
        #     )

        bar = Bar(
            'Iterating', suffix='%(percent)d%% - %(eta)ds',
            max=totalIter
        )
        

        while True:
            queue.get()
            currentProgress += 1
            # if GUI:
            #     window["progress"].update(currentProgress)
            bar.next()

            if totalIter <= currentProgress:
                break

        bar.finish()

    totalIter = iterations * len(billiard.orbits)

    if GUI:
        window = Window(
            "Iterating...",
            layout=[
                [Text("Check terminal for progress."),]
            ],
            finalize=True
        )
        # window = Window(
        #     "Iterating...",
        #     layout=[
        #         [ProgressBar(totalIter, size=(50, 10), key="progress")]
        #     ],
        #     finalize=True
        # )

    consumer = Process(
        target=tick, args=[queue, totalIter]
    )
    consumer.start()

    billiard.iterate_parallel(
        iterations=iterations,
        callback=cb,
        poolSize=threads,
        method=method
    )

    # Bugs when there are no orbits!
    consumer.join()
    if GUI:
        window.close()
