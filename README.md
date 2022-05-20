# robolab
game-like interface for visualizing basic robotic algorithms.

## Set-up
- Make sure your python version is >=3.10.
- clone repo locally
- inside the ``robolab/`` folder run ```$ python install_requirements.py``` and wait a few seconds for the required libraries to install.
- run ```$ python main.py```

## Histogram Filter
The world is discretized in a 2D grid and each grid has a color. The robot can sense the color of the grid it is currently in and depending on the color sensed (which is prone to error depending on the noise of the sensor) 
the robot updates its belief of where it is located in the map. The belief of the robot is displayed on the righthand side going from blue to red (low vs high belief of being located at the given cell).

## Particle Filter
The world is continuous. The robot represents its uncertainty with particles distributed in space with different x, y and heading values. When the robot moves each particle makes the same movement relative to its current state, 
then the robot and (each particle individually) sense its distance to each feature (in this case celestial bodies) and the particles are then resampled with repetition with a probability
proportional to the similarity of the measurements of the given particle and the measurements of the robot. Therefore, the closer the particles are to the robot the more likely they are to being sampled and the more similar 
the orientation of the particle is to the orientation of the robot the more likely the particle is to survive the next resampling round since it moved in roughly the same direction of the robot.

## Kalman Filter 1D
The world is 1 dimensional and continuous. The robot represents its location uncertainty with a normal distribution (i.e. with a mean and a variance values). Movement and Measurment updates are decoupled so the robot can move 
without sensing and viceversa. With every motion update the uncertainty increases due to the noise in the motion actuators and with every measurement the uncertainty decreases because the robot its getting more information 
about its environment.

## Kalman Filter 2D
Similar to the 1D case but with 2 dimensions.

## A*
A* is an optimal algorithm used for finding a path from a start position to a goal. The start and goal position are set and the best path is displayed. The size of the map as well as the obstacle density and location can all be adjusted.
If no path can be found (e.g. the goal is surrounded by obstacles) then an exclamation mark will be shown in the last position visited that was closest to the goal.




