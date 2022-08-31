# Dynamical-Billiards

Open source project to simulate [dynamical billiards](https://en.wikipedia.org/wiki/Dynamical_billiards), currently being developed by [Aniura Milanes Barrientos](http://lattes.cnpq.br/7202170379160546), [Sônia Pinto de Carvalho](http://lattes.cnpq.br/6695125616195750) and [Yuri Garcia Vilela](http://lattes.cnpq.br/7173465337985484).

The main goal of this project is to develop a software that's able to draw the trajectory of a particle on a billiard given its initial condition, as well as plot its orbit in the phase portrait.

The conditions on the billiard's surface are yet to be defined, but some interesting features would be:

- **Small deformations of classical boundaries:** Ad-hoc implementations of models to simulate the dynamics on billiards that are close to the circle, the ellipse, etc.

- **3-dimensional billiards:** Initially, the goal is to be able to simulate the dynamics on [ellipsoids](https://en.wikipedia.org/wiki/Ellipsoid), but this may evolve to the simulation of other surfaces (or even higher dimensions).

- **User defined boundaries:** Ideally we would like to be able to simulate the dynamics regardless of the table's boundary, but we will probably start with convex billiards.

  - As pointed by my collegue [Cássio Morais](http://lattes.cnpq.br/2976593974420571), some classical curves are defined by parts, so we have to be careful about ill defined tangent vectors.

- **Stochastic ball-cushion interactions:** Besides the classical (simmetrical) reflection, we want to allow the ball-cushion interaction to be probabilistic. I still have to learn a lot about the subject, but I'll probably use the [Feres Random Map](https://arxiv.org/pdf/2005.01892.pdf).

To consider:

- **Irregular tables:** Should we consider tables that **exactly** flat? How can the user custom these irregularities? Should this be probabilistic? Maybe I can slightly disturb the metric. **Is this useful?**

- **Different geometries:** Should we consider tables in different geometries (hyperbolic, for instance)? How to implement that? Maybe just change how the velocity acts? **Is this useful?**

- **GUI and animations:** Not a priority, as the script can be executed from the terminal, but it wouldn't hurt to have user friendly interfaces and animations of the particle reflecting over time.
