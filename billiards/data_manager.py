# Todo: Get this from a file
import json
import os
from PySimpleGUI import popup_yes_no
from pathlib import Path
from pandas import read_csv

from billiards.billiards import Billiard, Orbit
from billiards.geometry import ComposedPath


defaultValues = {
    "mainFolder": "data",
    "subfolders": {
        "simulations": "simulations",
        "boundaries": "boundaries",
        "orbits": "orbits"
    }
}


class DataManager:
    def __init__(self, envVariables=defaultValues):
        necessaryFolders = {
            subfolder: os.path.join(envVariables["mainFolder"], subfolder)
            for subfolder in envVariables["subfolders"]
        }

        missingFolders = [
            folderPath
            for _, folderPath in necessaryFolders.items()
            if not Path(folderPath).exists()
        ]

        if len(missingFolders) > 0:
            response = popup_yes_no(
                f"Missing the folders \n{str(missingFolders)}\
                \n Create and proceed?"
            )

            if response == "Yes":
                for folderPath in missingFolders:
                    Path(folderPath).mkdir(exist_ok=True)
            else:
                raise Exception(
                    "Can't init DataManager. " +
                    f"Missing the folders {str(missingFolders)}."
                )

        self.folders = necessaryFolders

    def list_boundaries(self):
        return os.listdir(self.folders["boundaries"])

    def load_boundary(self, boundaryName):
        filePath = os.path.join(self.folders["boundaries"], boundaryName)
        componentArray = json.load(open(filePath))

        boundary = ComposedPath.from_json(componentArray)

        return boundary

    def list_simulations(self):
        return os.listdir(self.folders["simulations"])

    def load_simulation(self, simulationName):
        filePath = os.path.join(self.folders["simulations"], simulationName)
        return json.load(open(filePath))

    def load_simulation_billiard(self, simulationName: str):
        simulationParams = self.load_simulation(simulationName)

        boundary = self.load_boundary(simulationParams["boundary"])
        orbits = self.load_simulation_orbits(simulationName, boundary)

        return Billiard(boundary, orbits=orbits)

    def load_simulation_boundary(self, simulationName):
        filePath = os.path.join(self.folders["simulations"], simulationName)
        simulationParams = json.load(open(filePath))

        boundary = self.load_boundary(simulationParams["boundary"])

        return boundary

    def load_simulation_orbits(
        self,
        simulationName,
        boundary: ComposedPath = None
    ):
        if boundary is None:
            boundary = self.load_simulation_boundary(simulationName)

        orbitsFolder = os.path.join(self.folders["orbits"], simulationName)

        fileList = []
        if os.path.exists(orbitsFolder):
            fileList = os.listdir(orbitsFolder)

        orbits = [
            Orbit(boundary, read_csv(os.path.join(orbitsFolder, fileName)))
            for fileName in fileList
            if fileName.endswith(".csv")
        ]

        return orbits

    def create_boundary(
        self,
        boundaryName,
        boundary: ComposedPath,
        overwrite=False
    ):
        print(f"Trying to create {boundaryName}")
        filePath = os.path.join(self.folders["boundaries"], boundaryName)
        if Path(filePath).exists() and not overwrite:
            print("Already exists!!")
            raise ObjectExistsException(
                "Another boundary with that name already exists."
            )

        boundaryJson = boundary.to_json()
        with open(filePath, 'w', encoding='utf-8') as f:
            json.dump(boundaryJson, f, ensure_ascii=False, indent=4)

    def create_simulation(
        self,
        simulationName,
        boundaryName,
        overwrite=False
    ):
        filePath = os.path.join(self.folders["simulations"], simulationName)
        if Path(filePath).exists() and not overwrite:
            raise ObjectExistsException(
                "Another simulation with that name already exists."
            )

        simulationJson = {
            "name": simulationName,
            "boundary": boundaryName
        }
        with open(filePath, 'w', encoding='utf-8') as f:
            json.dump(simulationJson, f, ensure_ascii=False, indent=4)

    # Todo: find out how to just update the csv
    def upsert_simulation_orbits(self, simulationName, orbits):
        orbitsFolder = os.path.join(self.folders["orbits"], simulationName)
        Path(orbitsFolder).mkdir(exist_ok=True)

        for orbit in orbits:
            t, theta = orbit.initialCondition
            orbitName = f"{t}_{theta}.csv"
            orbitPath = os.path.join(orbitsFolder, orbitName)

            orbit.points.to_csv(orbitPath, index=False)


class ObjectExistsException(BaseException):
    def __init__(self, message: str):
        super().__init__(message)
