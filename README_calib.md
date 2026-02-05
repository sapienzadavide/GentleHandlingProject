# PickDNN Calibration Docker

A containerized environment for robotic hand-eye calibration with support for both eye-in-hand (camera on robot) and eye-to-hand (fixed camera) configurations for UR5e and Intel RealSense.

## Overview

This repository provides a complete calibration setup for robotic picking systems using:
- **easy_handeye2** - Hand-eye calibration for both mounting configurations
- **ros2_aruco** - ArUco marker detection for calibration targets
- RealSense camera integration
- Universal Robots (UR) driver support
- MoveIt2 for guided robot movement (optional)
- **aruco_tf_publisher** - Custom script to bridge ArUco topics to TF frames (crucial for eye-to-hand)

## Prerequisites

### Hardware
- Universal Robots UR5e (or compatible UR robot)
- RealSense camera (D435, D455, or compatible)
- Printed ArUco marker (instructions below)

### Software
- Docker with BuildX v0.19.3+
- Visual Studio Code with Dev Containers extension
- ROS2 Humble (included in container)

## Setup

1. **Clone this repository:**
```bash
   git clone <your-repo-url>
   cd gentle_handling
```

2. **Open in Visual Studio Code:**
```bash
   code .
```
   Use "Dev Containers: Reopen in Container" command to start the development container.

3. **Import calibration repositories:**
```bash
   cd ws
   vcs import src < ../calib.repos
```

4. **Install dependencies:**
```bash
   sudo rosdep init
   rosdep update
   rosdep install --from-paths src --ignore-src -r -y
```

5. **Build the workspace:**
```bash
   colcon build --symlink-install
   source install/setup.bash
```

## Generating Calibration Marker

Before calibration, you need to print an ArUco marker:
```bash
python3 << EOF
import cv2
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
marker = cv2.aruco.drawMarker(aruco_dict, 26, 400)
cv2.imwrite('aruco_marker_26.png', marker)
print('Marker saved as aruco_marker_26.png')
EOF
```

**Important steps:**
1. Print the `aruco_marker_26.png` on A4 paper
2. Mount it on a rigid surface (cardboard, wood, etc.)
3. **Measure the actual marker size** (e.g., 15cm) - this is critical for accuracy
4. Use this measurement in the calibration launch commands below

## Configuring ArUco Detection

Create a configuration file for ArUco detection with your measured marker size:
```bash
cat > /cfg/aruco_params.yaml << 'EOF'
aruco_node:
  ros__parameters:
    marker_size: 0.15  # Adjust to your measured marker size in meters
    aruco_dictionary_id: "DICT_6X6_250"
    image_topic: "/camera/camera/color/image_raw"
    camera_info_topic: "/camera/camera/color/camera_info"
    camera_frame: "camera_color_optical_frame"
EOF
```

**Note:** Update `marker_size` to match your actual measured marker dimension.

## Calibration Workflow

### Prerequisites for Calibration

Before starting calibration, ensure these nodes are running:

**Terminal 1 - Start UR Robot Driver:**
```bash
ros2 launch ur_robot_driver ur_control.launch.py \
    ur_type:=ur5e \
    robot_ip:=<ROBOT_IP> \
    launch_rviz:=false
```

**Terminal 2 - Start RealSense Camera:**
```bash
ros2 launch realsense2_camera rs_launch.py
## cast resolution 640x480x30:
ros2 launch realsense2_camera rs_launch.py \
    depth_module.depth_profile:='640x480x30' \
    rgb_camera.color_profile:='640x480x30'
```
**Note:** 
- Ensure the RealSense camera is connected via USB
- If running in Docker, the container must have USB device access (configured in `.devcontainer.json` with `--privileged`)
- Verify camera is detected: `rs-enumerate-devices` (from `librealsense2-utils`)

**Verify camera:**
```bash
# Check camera is detected
rs-enumerate-devices

# Verify image stream
ros2 topic hz /camera/camera/color/image_raw
```

**Terminal 3 - Start ArUco Detector:**
```bash
ros2 run ros2_aruco aruco_node --ros-args --params-file /cfg/aruco_params.yaml
```
**Verify marker detection:**
```bash
# In another terminal, check if marker is detected:
ros2 topic echo /aruco_markers

# You should see: marker_ids: [26]
# If not, ensure marker is visible to camera and correctly sized
```

**Terminal 4 - Start ArUco TF Publisher (Crucial for Eye-to-Hand):**
This script publishes the marker_26 frame based on detected poses.
```bash
python3 aruco_tf_publisher.py
```

### Eye-in-Hand Calibration (Camera on UR5e wrist)

**Setup:**
- Camera mounted on robot gripper/wrist
- ArUco marker fixed on table/base

**Terminal 5 - Launch Calibration:**
```bash
ros2 launch easy_handeye2 calibrate.launch.py \
    name:=eye_in_hand_calib \
    calibration_type:=eye_in_hand \
    robot_base_frame:=base_link \
    robot_effector_frame:=tool0 \
    tracking_base_frame:=camera_color_optical_frame \
    tracking_marker_frame:=camera_color_optical_frame \
    freehand_robot_movement:=true
```

**Result: Calculates transformation tool0 → camera_color_optical_frame**

### Eye-to-Hand Calibration (Fixed camera, , marker on robot)

**Setup:**
- Camera fixed observing workspace
- ArUco marker attached to robot gripper/tool0

**Terminal 5 - Launch Calibration:**
```bash
ros2 launch easy_handeye2 calibrate.launch.py \
    name:=eye_to_hand_calib \
    calibration_type:=eye_on_base \
    robot_base_frame:=base_link \
    robot_effector_frame:=tool0 \
    tracking_base_frame:=camera_color_optical_frame \
    tracking_marker_frame:=marker_26 \
    freehand_robot_movement:=true

```

**Result: Calculates transformation base_link → camera_color_optical_frame**

---

**Calibration procedure:**
1. Move the robot to different positions where the marker is clearly visible
2. For each position, click "Take Sample" in the GUI
3. Collect 15-20 samples with varied positions and orientations
4. Click "Compute Calibration"
5. Click "Save Calibration"

**If GUI does not appear (X11 issues in Docker):**
Use command-line interface:
```bash
# 1. Move robot manually (teach pendant) or with MoveIt

# 2. Take sample
ros2 topic pub --once /eye_in_hand_calib/take_sample std_msgs/msg/Empty
# or for eye-to-hand:
ros2 topic pub --once /eye_to_hand_calib/take_sample std_msgs/msg/Empty

# 3. Repeat 15-20 times with varied robot poses

# 4. Compute calibration
ros2 service call /eye_in_hand_calib/compute_calibration easy_handeye2_msgs/srv/ComputeCalibration "{}"

# 5. Save calibration
ros2 service call /eye_in_hand_calib/save_calibration easy_handeye2_msgs/srv/SaveCalibration "{}"
```

**Important:** Use namespace that matches your calibration name parameter.
Results saved in: `~/.ros/easy_handeye/<calibration_name>/` .

---

### Using the Calibration

After calibration, publish the transform in your own launch files:
```bash
# For eye-in-hand
ros2 launch easy_handeye2 publish.launch.py \
    name:=eye_in_hand_calib \
    calibration_type:=eye_in_hand

# For eye-to-hand
ros2 launch easy_handeye2 publish.launch.py \
    name:=eye_to_hand_calib \
    calibration_type:=eye_on_base
```

This will publish the calibrated transform as a static TF.

---

## Testing with Simulation (Optional)
If you want to test the calibration workflow without physical hardware, you can use the `easy_handeye2_demo` package with a simulated robot.

### Eye in hand

**Launch dem**

```bash
# Eye-in-hand simulation
ros2 launch easy_handeye2_demo calibrate.launch.py \
    calibration_type:=eye_in_hand \
    tracking_base_frame:=tr_base \
    tracking_marker_frame:=tr_marker \
    robot_base_frame:=panda_link0 \
    robot_effector_frame:=panda_link8 \
    name:=easy_handeye2
```

What launches:
- RViz with simulated Panda robot
- Simulated tracking system (replaces ArUco)
- Calibration backend (GUI may not appear in Docker)

**Calibration procedure:**
```bash
# 1. Move robot in RViz using MoveIt (drag end-effector, then "Plan & Execute")

# 2. Take sample
ros2 topic pub --once /easy_handeye2/calibration/take_sample std_msgs/msg/Empty

# 3. Repeat 15-20 times with varied poses

# 4. Compute calibration
ros2 service call /easy_handeye2/calibration/compute_calibration easy_handeye2_msgs/srv/ComputeCalibration "{}"

# 5. Save
ros2 service call /easy_handeye2/calibration/save_calibration easy_handeye2_msgs/srv/SaveCalibration "{}"
```

**Verify Simulated Calibration**

```bash
ros2 launch easy_handeye2_demo check_calibration.launch.py \
    calibration_type:=eye_in_hand \
    tracking_base_frame:=tr_base \
    tracking_marker_frame:=tr_marker \
    robot_base_frame:=panda_link0 \
    robot_effector_frame:=panda_link8
```

Move robot - marker should stay fixed relative to end-effector.

### Eye on base

**Launch demo:**
```bash
# Eye-to-hand simulation
ros2 launch easy_handeye2_demo calibrate.launch.py \
    calibration_type:=eye_on_base \
    tracking_base_frame:=tr_base \
    tracking_marker_frame:=tr_marker \
    robot_base_frame:=panda_link0 \
    robot_effector_frame:=panda_link8 \
    name:=easy_handeye2
```

**Calibration procedure:** (same as eye-in-hand above)

**Verify:**
```bash
ros2 launch easy_handeye2_demo check_calibration.launch.py \
    calibration_type:=eye_on_base \
    tracking_base_frame:=tr_base \
    tracking_marker_frame:=tr_marker \
    robot_base_frame:=panda_link0 \
    robot_effector_frame:=panda_link8
```
---

## Troubleshooting

### "Cannot find transform between frames"
- Ensure robot driver is publishing TF (check with `ros2 run tf2_ros tf2_echo base_link tool0`)
- Ensure ArUco detector sees the marker (check with `ros2 topic echo /aruco_poses`)

### "Calibration quality is poor"
- Collect more samples (aim for 20+)
- Ensure varied positions and orientations
- Keep marker fully visible in all samples
- Verify marker size measurement is accurate

### Docker BuildX API errors
- Update Docker BuildX: See [troubleshooting guide](https://github.com/docker/buildx/releases)
- Ensure BuildX version >= v0.19.3

## Project Structure
```
gentle_handling/
├── ws/                          # ROS2 workspace
│   └── src/                     # Source packages (from VCS)
├── calib.repos                  # VCS repository list
├── Dockerfile                   # Container definition
├── .devcontainer.json           # Dev container config
└── README_calib.md                    # This file
```

## Dependencies Installed via APT

The Docker container includes:
- `ros-humble-ur-robot-driver` - UR robot control
- `ros-humble-realsense2-camera` - RealSense driver
- `ros-humble-moveit` - Motion planning (optional)
- `ros-humble-rqt` - Visualization tools
- OpenCV and cv_bridge for image processing

## Supported Hardware

### Robots
- Universal Robots UR3, UR5, UR5e, UR10, UR16
- Other robots with ROS2 drivers (modify launch files accordingly)

### Cameras
- Intel RealSense D435, D435i, D455
- Other RGB-D cameras with ROS2 support

## License

This project is licensed under the Apache License 2.0.

## Maintainer

Davide Sapienza <sapienza.dav@gmail.com>

---

**Note:** For best calibration results, ensure good lighting conditions and keep the ArUco marker flat and rigid during the process.


