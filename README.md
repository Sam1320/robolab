# robolab
game-like interface for visualizing basic robotic algorithms.

## Set-up
- Make sure your python version is >=3.10.
- clone repo locally
- inside the ``robolab/`` folder run ```$ python install_requirements.py``` and wait a few seconds for the required libraries to install.
- run ```$ python main.py```

## Histogram Filter
![alt text](https://github.com/Sam1320/robolab/blob/main/images/histogram_filter_thumbnail_resized.png)

The world is discretized in a 2D grid and each grid has a color. The robot can sense the color of the grid it is currently in and depending on the color sensed (which is prone to error depending on the noise of the sensor) 
the robot updates its belief of where it is located in the map. The belief of the robot is displayed on the righthand side going from blue to red (low vs high belief of being located at the given cell).

## Particle Filter
![alt text](https://github.com/Sam1320/robolab/blob/main/images/particle_filter_thumbnail_resized.png) 

The world is continuous. The robot represents its uncertainty with particles distributed in space with different x, y and heading values. When the robot moves each particle makes the same movement relative to its current state, 
then the robot and (each particle individually) sense its distance to each feature (in this case celestial bodies) and the particles are then resampled with repetition with a probability
proportional to the similarity of the measurements of the given particle and the measurements of the robot. Therefore, the closer the particles are to the robot the more likely they are to being sampled and the more similar 
the orientation of the particle is to the orientation of the robot the more likely the particle is to survive the next resampling round since it moved in roughly the same direction of the robot.

## Kalman Filter 1D
![alt text](https://github.com/Sam1320/robolab/blob/main/images/kalman_1d_thumbnail_resized.png) 

The world is 1 dimensional and continuous. The robot represents its location uncertainty with a normal distribution (i.e. with a mean and a variance values). Movement and Measurment updates are decoupled so the robot can move 
without sensing and viceversa. With every motion update the uncertainty increases due to the noise in the motion actuators and with every measurement the uncertainty decreases because the robot its getting more information 
about its environment.

## Kalman Filter 2D
![alt text](https://github.com/Sam1320/robolab/blob/main/images/kalman_2d_thumbnail_resized.png) 

Similar to the 1D case but with 2 dimensions.

## A*
![alt text](https://github.com/Sam1320/robolab/blob/main/images/a_star_thumbnail_resized.png) 

A* is an optimal algorithm used for finding a path from a start position to a goal. The start and goal position are set and the best path is displayed. The size of the map as well as the obstacle density and location can all be adjusted.
If no path can be found (e.g. the goal is surrounded by obstacles) then an exclamation mark will be shown in the last position visited that was closest to the goal.

## Dynammic Programming
![alt text](https://github.com/Sam1320/robolab/blob/main/images/dynamic_programming_thumbnail_resized.png) 

Grid world similar to the one used in the A* interface. Here only the goal needs to be set by the user and the optimal path from every cell to the goal is found using dynammic programming. The path is shown with arrows in the direction that needs to be taken in every cell. If there is no path to the goal from a cell then there is no arrow drawn on that specific cell.

## Optimum Policy
![alt text](https://github.com/Sam1320/robolab/blob/main/images/optimum_policy_thumbnail_resized.png) 

Similar to A* but in this case orientation (i.e. UP, RIGHT, DOWN, LEFT) matters and the user can assign different costs to each action (FORWARD, LEFT, RIGHT). The optimal path is then found considering the cost of the actions.

## Path Smoothing
![alt text](https://github.com/Sam1320/robolab/blob/main/images/path_smoothing_thumbnail_resized.png) 

Grid world where the user can set goal and starting position and the optimal path will be found. However, in this case two paths are shown, namely the original path found by A* and the _smoothed_ path. The smoothed path is found by adjusting each coordinate in the discrete path to be closer to its neighbors so that there are not sharp corners and the robot can navigate it more smoothly. The user can control the level of smoothness by using the mouse wheel. The least smooth path possible is equal to the original path found by A*. The smoothest path possible is just a straight line from start to goal.

## PID Control
![alt text](https://github.com/Sam1320/robolab/blob/main/images/pid_control_thumbnail_resized.png) 

The world is a highway and the robot is a car trying to drive stably across the center of the highway. The commands sent to the car are found using PID control. The user can manually set each of the PID parameters and also set the intial position and drift of the robot. At run time the user can increase or decrease the speed of the car using the RIGHT or LEFT arrow keys. The drift (i.e. The level of deviation from perfect alignment of the steering wheel) can also be controlled at run time using the UP and DOWN arrow keys. The optimal parameters can be found programatically by an algorihtm called Twiddle, the user need only press the "T" key and the system will try to find the optimal parameters for the given state of the environment.




