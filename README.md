# Dynamical-Billiards

Open source project to simulate [dynamical billiards](https://en.wikipedia.org/wiki/Dynamical_billiards), currently being developed by [Aniura Milanes Barrientos](http://lattes.cnpq.br/7202170379160546), [Sônia Pinto de Carvalho](http://lattes.cnpq.br/6695125616195750), [Cássio Morais](http://lattes.cnpq.br/2976593974420571) and [Yuri Garcia Vilela](http://lattes.cnpq.br/7173465337985484).

## Environment Preparation

- Clone the repository

- [Install python](https://www.python.org/downloads/) (tested on version 3.9.12)

- Install the necessary python libraries (listed on _requirements.txt_)

## Usage (Alpha version)

Execute the script _billiards.py_ or _billiards-gui.py_. For the former it's **necessary** to inform the [parameter file](#creating-the-parameters-file) and for the latter it's **possible** to inform the folder where the billiards data will be saved/loaded from (defaults to "data").

      py billiards.py MY_PARAMETERS.json

      py billiards-gui.py MY_DATA_FOLDER

### Creating the parameters file

In order to simulate the dynamics without the GUI, the user must inform the path to a '_json_' file containing the following fields:

- **paths**: An array of dictionaries representing the curves that form the boundary of the billiard table. Each dictionary must contain:
  - **x**: A parametrization for the _x_ coordinate of the curve in the variable _t_. This expression will be interpreted using the [SymPy](https://www.sympy.org/pt/index.html) library.
  - **y**: A parametrization for the _y_ coordinate of the curve in the variable _t_. This expression will be interpreted using the [SymPy](https://www.sympy.org/pt/index.html) library.
  - **t0**: The initial value for _t_ in the parametrization. Either a number or an numeric expression to be interpreted by [SymPy](https://www.sympy.org/pt/index.html).
  - **t1**: The final value for _t_ in the parametrization. Either a number or an numeric expression to be interpreted by [SymPy](https://www.sympy.org/pt/index.html).

**IMPORTANT:** The final point of each path must be the initial point of the next one AND the final point of the last path must be the initial point of the first one.

- **initialConditions**: An array of dictionaries representing the initial conditions to be iterated. Each dictionary must contain:

  - **t**: The initial point in the boundary. Either a number, an numeric expression to be interpreted by [SymPy](https://www.sympy.org/pt/index.html) or the string "Random", get a random point.
    - In order to get a random point, the sample interval must be given in the attribute **tRange**; an array containing the first and the last point of such interval.
  - **theta**: The first reflection angle. Either a number, an numeric expression to be interpreted by [SymPy](https://www.sympy.org/pt/index.html) or the string "Random", get a random angle.
    - In order to get a random angle, the sample interval must be given in the attribute **thetaRange**; an array containing the first and the last angle of such interval.

Additionally, the user may inform how many instances of that condition they wish to create (useful for random conditions). In that case, the attribute **instances** must be present in the dictionary.

- **iterations**: The number of iterations that must be performed.

- **show**: Whether or not the trajectories and the orbits must be exibited after the simulation is concluded.

- **saveImage**: Whether or not the trajectories and the orbits must be saved to an '_png_' file after the simulation is concluded. This image will be saved as '_MY_PARAMETERS/plot.png_', where "MY_PARAMETERS.json" is the file containing the parameters used on the simulation.

- **saveBilliard**: Whether or not the simulation data (orbits and boundary) must be saved after the simulation is concluded. The boundary will be saved as '_MY_PARAMETERS/boundary.json_' and each orbit as '_MY_PARAMETERS/orbits/INITIAL_CONDITIONS.csv_' where "INITIAL_CONDITIONS" is the concatenation of initial conditions for that orbit and "MY_PARAMETERS.json" is the file containing the parameters used on the simulation.

- **orbitsFolder [OPTIONAL]**: Path to a folder containing the starting orbits information.

- **parallelize**: Whether or not the simulation must be executed in parallel. Indicated when you have a large number of orbits to simulate.

- **threads**: How many threads must be created in the parallel simulation.

- **method**: The numeric method to be used to compute the billiard map. At the moment, the available methods are **newton**, **regula falsi** and **bissec**.

#### Sample file

The configuration to execute dynamics on the Bunimovich stadium:

```json
{
  "paths": [
    { "x": "t", "y": "-1", "t0": -1, "t1": 1 },
    { "x": "cos(t)+1", "y": "sin(t)", "t0": "-pi/2", "t1": "pi/2" },
    { "x": "-t", "y": "1", "t0": "-1", "t1": "1" },
    { "x": "cos(t)-1", "y": "sin(t)", "t0": "pi/2", "t1": "3*pi/2" }
  ],
  "initialConditions": [
    {
      "t": "Random",
      "theta": "Random",
      "tRange": [0, "2*pi + 4"],
      "thetaRange": [0, "pi"],
      "instances": 10
    },
    {
      "t": 1,
      "theta": "Random",
      "thetaRange": [0, "pi"]
    },
    {
      "t": "Random",
      "theta": "3*pi",
      "tRange": [0, "pi"],
      "instances": 3
    }
  ],
  "iterations": 10,
  "method": "newton",
  "show": true,
  "saveImage": false,
  "saveBilliard": true,
  "parallelize": true,
  "threads": 5
}
```

## Project description

The main goal of this project is to develop a software that's able to draw the trajectory of a particle on a billiard given its initial condition, as well as plot its orbit in the phase portrait.

The conditions on the billiard's surface are yet to be defined, but some interesting features would be:

- **Small deformations of classical boundaries:** Ad-hoc implementations of models to simulate the dynamics on billiards that are close to the circle, the ellipse, etc.

- **3-dimensional billiards:** Initially, the goal is to be able to simulate the dynamics on [ellipsoids](https://en.wikipedia.org/wiki/Ellipsoid), but this may evolve to the simulation of other surfaces (or even higher dimensions).

- **User defined boundaries [IMPLEMENTED (convex)]:** Ideally we would like to be able to simulate the dynamics regardless of the table's boundary, but we will probably start with convex billiards.

  - **To do:** Some classical curves are defined by parts, so we have to be careful about ill defined tangent vectors.

- **Stochastic ball-cushion interactions:** Besides the classical (simmetrical) reflection, we want to allow the ball-cushion interaction to be probabilistic. I still have to learn a lot about the subject, but I'll probably use the [Feres Random Map](https://arxiv.org/pdf/2005.01892.pdf).

### To be considered:

- **Irregular tables:** Should we consider tables that **exactly** flat? How can the user custom these irregularities? Should this be probabilistic? Maybe I can slightly disturb the metric. **Is this useful?**

- **Different geometries:** Should we consider tables in different geometries (hyperbolic, for instance)? How to implement that? Maybe just change how the velocity acts? **Is this useful?**

- **GUI and animations:** Not a priority, as the script can be executed from the terminal, but it wouldn't hurt to have user friendly interfaces and animations of the particle reflecting over time.

- **Parallelism:** The iteration of different orbits is a highly parallelizable problem, as they are completelly independent (pairwise). Therefore, implementing parallelism would be a great way of improving performance.
