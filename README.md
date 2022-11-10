# Dynamical-Billiards

Open source project to simulate [dynamical billiards](https://en.wikipedia.org/wiki/Dynamical_billiards), currently being developed by [Aniura Milanes Barrientos](http://lattes.cnpq.br/7202170379160546), [Sônia Pinto de Carvalho](http://lattes.cnpq.br/6695125616195750), [Cássio Morais](http://lattes.cnpq.br/2976593974420571) and [Yuri Garcia Vilela](http://lattes.cnpq.br/7173465337985484).

## Environment Preparation

- Clone the repository

- [Install python](https://www.python.org/downloads/) (tested on version 3.9.12)

- Install the necessary python libraries (listed on _requirements.txt_)

## Usage (Alpha version)

Execute the script _billiards.py_ or _billiards-gui.py_. For the former it's **necessary** to inform the [parameter file](#creating-the-parameters-file). On the first execution the folder structure to store the execution data will be created in the current directory.

      py billiards-gui.py

      py billiards.py MY_PARAMETERS.json

## Project description

The main goal of this project is to develop a software that's able to draw the trajectory of a particle on a billiard given its initial condition, as well as plot its orbit in the phase portrait.

The conditions on the billiard's surface are yet to be defined, but some interesting features would be:

- **Small deformations of classical boundaries:** Ad-hoc implementations of models to simulate the dynamics on billiards that are close to the circle, the ellipse, etc.

- **3-dimensional billiards:** Initially, the goal is to be able to simulate the dynamics on [ellipsoids](https://en.wikipedia.org/wiki/Ellipsoid), but this may evolve to the simulation of other surfaces (or even higher dimensions).

- **User defined boundaries [IMPLEMENTED (convex)]:** Ideally we would like to be able to simulate the dynamics regardless of the table's boundary, but we will probably start with convex billiards.

  - **To do:** Some classical curves are defined by parts, so we have to be careful about ill defined tangent vectors.

- **Stochastic ball-cushion interactions:** Besides the classical (simmetrical) reflection, we want to allow the ball-cushion interaction to be probabilistic. I still have to learn a lot about the subject, but I'll probably use the [Feres Random Map](https://arxiv.org/pdf/2005.01892.pdf).

### Possible features:

- **Irregular tables:** Should we consider tables that **exactly** flat? How can the user custom these irregularities? Should this be probabilistic? Maybe I can slightly disturb the metric. **Is this useful?**

- **Different geometries:** Should we consider tables in different geometries (hyperbolic, for instance)? How to implement that? Maybe just change how the velocity acts? **Is this useful?**

- **Animations:** Not a priority, but it wouldn't hurt to have animations of the particles reflecting over time.

## Creating the parameters file

In order to simulate the dynamics without the GUI, the user must inform the path to a '_json_' file containing the following fields:

- **name**: The name of the simulation. If a simulation with that name doesn't exist, it will be created with the given **boundary** and **initialConditions**.
- **boundary**: The boundary to be used in the simulation. Must be dictionary containing:
  - **name**: The boundary name. If a boundary with that name doesn't exist, it will be craeted according to **paths** attribute.
  - **paths**: An array with the [simple paths](#path-objects) that form the boundary of the billiard table.
- **initialConditions**: An array with the [initial conditions](#initial-conditions-objects) to be iterated.
- **iterations**: The number of iterations that must be performed.
- **show**: Whether or not the trajectories and the orbits must be exibited after the simulation is concluded.
- **saveImagesAt [OPTIONAL]**: The location where the images of the phase plane and the trajectories must be saved after the execution.
- **parallel**: Whether or not the simulation must be executed in parallel. Indicated when you have a large number of orbits to simulate.
- **threads**: How many threads must be created in the parallel simulation.
- **method**: The numeric method to be used to compute the billiard map. At the moment, the available methods are **Mewton**, **Regula Falsi** and **Bissection**.

### Path objects

Each element of the **path** array is the representation of a parametric curve in the 2D-space and contains the following attributes:

- **x**: The parametrization for the _x_ coordinate of the curve in the variable _t_.
- **y**: The parametrization for the _y_ coordinate of the curve in the variable _t_.
- **t0**: The initial value for _t_ in the parametrization.
- **t1**: The final value for _t_ in the parametrization.

The **x** and **y** attributes are expressions that will be interpreted using [SymPy](https://www.sympy.org/pt/index.html) and the **t0** and **t1** can be eiter numbers or numeric expressions to be interpreted by the same library.

It's important to note that we mantain the order of the paths that is given in the file, so in order identify that the curve is indeed closed the final point of each of these elements must be the initial point of the next one **AND** the final point of the last path must be the initial point of the first one.

### Initial Conditions objects

The elements of the **initialConditions** array can represent a single condition or a subset of conditions within a random set.

Each element is a dictionary with the attributes **t** and **theta**, the initial point in the boundary and the first reflection angle, that must be either numeric vaules, numeric expressions to be interpreted by [SymPy](https://www.sympy.org/pt/index.html) or the string "Random", if you want these values to be randomly generated.

If a value is to be taken at random, the dictonary must also include the attribute **tRange** and/or **thetaRange**, a tuple containing the start and the end of the sample interval. Again, these values must be numeric or [SymPy](https://www.sympy.org/pt/index.html) expressions.

Finally, the user may inform how many instances of each element they want to create (useful for random conditions). In that case, the attribute **instances** must be present in the dictionary.

### Sample file

A few sample files can be found in the [samples](samples) directory, as well as the resulting images.

For a quick reference, follows one configuration to execute dynamics on the Bunimovich stadium:

```json
{
  "name": "Stadium",
  "boundary": {
    "name": "Stadium",
    "paths": [
      { "x": "t", "y": "-1", "t0": -1, "t1": 1 },
      { "x": "cos(t)+1", "y": "sin(t)", "t0": "-pi/2", "t1": "pi/2" },
      { "x": "-t", "y": "1", "t0": "-1", "t1": "1" },
      { "x": "cos(t)-1", "y": "sin(t)", "t0": "pi/2", "t1": "3*pi/2" }
    ]
  },
  "initialConditions": [
    {
      "t": "0",
      "theta": "Random",
      "thetaRange": [0, "pi/2"],
      "instances": 1000
    }
  ],
  "iterations": 10,
  "method": "Newton",
  "show": true,
  "saveImagesAt": "samples/images/Stadium",
  "parallel": true,
  "threads": 10
}
```
