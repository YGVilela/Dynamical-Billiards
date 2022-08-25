# Dynamical-Billiards

My experiments on _dynamical_ billiards. Unlike my [billiards](https://github.com/YGVilela/Billiards) project, this one is not meant to be a game, but a library where we can experiment with [dynamical billiards](https://en.wikipedia.org/wiki/Dynamical_billiards). Therefore, we still want it to be highly customizable, but we'll focus on developing:

- **User defined boundaries:** As pointed by my collegue [Cássio Morais](http://lattes.cnpq.br/2976593974420571), this can be done by defining curves by parts. If the tangent vector is not well defined (ambiguous) on some point, we'll assume theres a pocket there.

- **Stochastic ball-cushion interactions:** Besides the classical (simmetrical) reflection, I want to allow the ball-cushion interaction to be probabilistic. I still have to learn a lot about the subject, but I'll probably use the [Feres Random Map](https://arxiv.org/pdf/2005.01892.pdf) to do that.

- **Trajectory drawing and orbit plotting:** As we want to understand the dynamical properties of a billiard, it's mandatory to draws the trajectories and orbits for a point. It would be useful to be able to:

  - Draw the trajectories and plot the orbits of several initial conditions at once.
  - Animate the ball moving and plot more orbit point as it hits the boundaries.

To consider:

- **Irregular tables:** Should I consider tables that **exactly** flat? How should can the user custom these irregularities? Should this be probabilistic? Maybe I can slightly disturb the metric.

- **Different geometries:** Should I consider tables in different geometries (hyperbolic, for instance)? How to implement that? Maybe just change how the velocity acts?
