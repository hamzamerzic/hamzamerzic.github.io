To convert a DAE file to URDF:

```
docker run --rm -it -v "$(pwd)":/data ros:noetic-robot bash
```

Then, inside the terminal:

```
apt-get update
apt-get install -y ros-noetic-collada-urdf
source /opt/ros/noetic/setup.bash
cd data
# -V and -C replace the 3D model with bounding boxes for visual collisions, respectively
rosrun collada_urdf collada_to_urdf /data/abb_irb52_7_120.dae /data/abb_irb52_7_120.urdf -V -C
# Now get a simple version of the .dae file for visualization and testing.
rosrun collada_urdf urdf_to_collada /data/abb_irb52_7_120.urdf /data/abb_irb52_7_120_simple.dae
```
