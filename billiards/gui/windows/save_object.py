
import PySimpleGUI as sg

from billiards.data_manager import DataManager
from billiards.exceptions import ObjectExistsException

dm = DataManager()


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
