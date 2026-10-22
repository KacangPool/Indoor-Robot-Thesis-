# LiDAR-only quick start for the WHEELTEC robot

## Purpose

Use this guide to start, inspect, visualize, and briefly record the configured 2D LiDAR without starting the chassis, navigation, mapping, or an automatic follower.

The copied WHEELTEC configuration selects `ls_N10` and starts the local `lsn10` driver. That is strong configuration evidence for a Leishen/LS N10, but the physical LiDAR identity is still unconfirmed. Record a readable device label if possible.

## What the LiDAR view means

A 2D LiDAR does not produce a photograph. In RViz it should look like a top-down ring or outline of points:

- the sensor is at the centre;
- every point is a measured surface at one horizontal height;
- walls tend to appear as straight rows of points;
- a box or a person's legs create a nearer group of points;
- moving an object should move the corresponding points.

It can measure surrounding geometry and distance, but it cannot identify a return as a person, animal, or living being by itself.

In its fixed horizontal mounting it does not measure a full 3D scene. The configured N10 is a **2D** scanner: it measures one plane at the physical height of the LiDAR. A standing person may appear as two small curved clusters where the scan crosses the legs or body, not as a human-shaped figure. A box normally contributes only the edges/faces intersected by that plane, not its top and full height. A 2D scanner can contribute to 3D reconstruction when deliberately swept through accurately measured poses and combined using calibrated transforms; that requires additional mechanics/pose tracking and reconstruction, not a 3D-mode setting. See `SENSOR_2D_3D_EXPLORATION.md` for the controlled RViz comparison and the camera's depth capabilities.

## Safety boundary

- Keep the robot stationary and use the normal lab procedure for preventing unintended wheel motion.
- The sensor-only command below does not launch the chassis, but the LiDAR's scanning head may rotate.
- Do not touch or obstruct a rotating sensor. Follow the lab's optical-sensor safety rules. The candidate N10 datasheet classifies the 905 nm emitter as Class I.
- Do **not** run `roslaunch simple_follower laser_follower.launch`. That is a motion-capable demonstration, not a sensor test.
- Do not change serial permissions, device rules, scan speed, navigation, or mapping settings during the first test.

## 1. Check the existing ROS environment

Open a terminal on the robot and run:

```bash
echo $ROS_DISTRO
rospack find turn_on_wheeltec_robot
rospack find lsn10
```

If a package is not found, load the existing workspace once:

```bash
source ~/wheeltec_robot/devel/setup.bash
```

Then repeat the checks. Do not rebuild or reinstall anything during this baseline test.

## 2. Record the physical and USB/serial identity

The copied `lsn10` driver does not provide camera-style ROS services for retrieving the LiDAR's device type or manufacturer serial number. Use the following evidence in order:

1. **Physical label:** strongest evidence. Photograph all readable manufacturer, model, serial, voltage, and certification text. Do not lift or handle the powered robot merely to reach a label.
2. **Linux USB/serial identity:** useful for identifying the USB-to-serial interface, but it may describe an adapter rather than the LiDAR itself.
3. **Active ROS driver:** confirms which driver/configuration is accepting the data, but a launch-file name is not independent proof of the physical model.

Before launching, run these read-only checks:

```bash
ls -l /dev/wheeltec_lidar
readlink -f /dev/wheeltec_lidar
udevadm info --query=property --name=/dev/wheeltec_lidar | grep -E '^(ID_VENDOR|ID_MODEL|ID_SERIAL|ID_VENDOR_ID|ID_MODEL_ID)='
ls -l /dev/serial/by-id/ 2>/dev/null
lsusb
```

Save or photograph the output and every readable label on the LiDAR. The expected configured serial alias is `/dev/wheeltec_lidar`. Its existence shows that Linux created the alias; it does not by itself prove valid scan data or the N10 model.

The copied WHEELTEC device rules can assign this alias to Silicon Labs (`10c4:ea60`) or WCH (`1a86:55d4`) serial interfaces. Names such as CP210x/CP2102, CH340, CH341, CH343, `0001`, or `54B8001974` can therefore belong to the USB interface and must not be presented as the LiDAR's manufacturer/model/serial.

## 3. Start only the configured LiDAR

Run:

```bash
roslaunch turn_on_wheeltec_robot wheeltec_lidar.launch
```

This is the preferred command. In the copied configuration it selects `ls_N10`, includes the `lsn10` driver, uses `/dev/wheeltec_lidar`, publishes a scan topic, and does not start the robot base.

Leave the terminal open and save any red error messages. The direct driver command below is only a later diagnostic if the WHEELTEC wrapper fails:

```bash
roslaunch lsn10 lsn10.launch
```

Do not run both commands at the same time.

From a second terminal, record which LiDAR driver actually started:

```bash
rosnode list | grep -Ei 'lsn10|m10|ldlidar|rplidar'
rosnode info /lsn10
rosparam get /lsn10
rosservice list | grep -i lsn10
```

For the copied default, `/lsn10` should publish `/scan`, and its parameters should show `/dev/wheeltec_lidar`, frame `laser`, and protocol selection `versions: 1` (230400 baud). It is normal for the last command to return nothing because this driver exposes no device-identity service.

### Identification conclusion rule

- Label explicitly says Leishen/LSLiDAR and N10: **confirmed N10**; record its manufacturer serial separately if shown.
- Label is unreadable, but `/lsn10` publishes a valid scan using the configured N10 protocol: **probable/configured N10**, not physically confirmed.
- USB output only shows CP210x/CH34x: **serial interface identified only**; LiDAR model remains unknown.
- A different driver node starts, such as `rplidarNode` or `ldlidar`: stop and preserve the output before assigning a model name.

## 4. Confirm that scan data is arriving

Open a second terminal, source the workspace if needed, and run:

```bash
rosnode list | grep lsn10
rostopic list | grep scan
rostopic type /scan
rostopic hz /scan
```

Let the rate check run for about 15 seconds, then press `Ctrl+C`. Expected results are:

- topic type `sensor_msgs/LaserScan`;
- a reasonably stable scan rate within the candidate N10's configured 6-12 Hz range.

Capture one message:

```bash
rostopic echo -n 1 /scan
```

It should contain fields such as `angle_min`, `angle_max`, `ranges`, and `intensities`. A long list of numbers is normal.

## 5. See what the LiDAR sees in RViz

On the robot's graphical desktop, run:

```bash
rviz
```

In RViz:

1. set **Global Options > Fixed Frame** to `laser`;
2. choose **Add > By display type > LaserScan**;
3. set its topic to `/scan`;
4. under **Views**, select **TopDownOrtho** so the scan is viewed from directly above;
5. if the points are difficult to see, use the Points or Flat Squares style and try a visible size between `0.02` and `0.05`.

Place a matte cardboard box at roughly 0.5 m, 1 m, and 2 m, using a tape measure if available. Move it sideways while watching RViz. The corresponding cluster should move. Avoid using glass, mirrors, glossy black material, or a person as the only first target because reflectivity and shape complicate the check.

For a deliberately recognizable test, place the stationary robot in front of:

1. one large flat wall, which should produce an approximately straight row of points;
2. a room corner, which should produce an L-shaped pair of rows;
3. a large matte cardboard box, which should introduce a nearer short edge or corner;
4. a standing person, who will usually produce only one or two small curved clusters at scan height.

Do not expect filled surfaces, colours, a head/body silhouette, height, floor, ceiling, or a rotatable 3D object. If those are required, visualize the Astra S depth point cloud instead, using an available topic such as `/camera/depth_registered/points`.

The N10-specific datasheet gives a 360-degree field, 6-12 Hz scan rate, 4,500 points per second, and a qualified range of 0.02-12 m at 70% reflectivity. Treat these as candidate specifications until the physical sensor identity is confirmed and measure actual performance on the robot.

## 6. Make a short scan recording

In a third terminal, create a known folder and record approximately 20 seconds:

```bash
mkdir -p ~/thesis_lidar_test
cd ~/thesis_lidar_test
pwd
rosbag record -O lsn10_test.bag /scan
```

Press `Ctrl+C` once, then inspect the saved file:

```bash
rosbag info lsn10_test.bag
ls -lh lsn10_test.bag
```

The `.bag` file is stored in the folder printed by `pwd`. Copy it, the terminal outputs, the RViz screenshot, and the device-label photograph to approved lab storage.

## 7. Stop cleanly

Return to the first terminal and press `Ctrl+C`. Wait for the node to stop and the scanning head to settle before disconnecting or powering down the hardware.

## Pass criteria for the first test

The initial LiDAR test passes if:

- `/dev/wheeltec_lidar` exists;
- the driver starts without persistent serial errors;
- `/scan` publishes repeatedly at a stable rate;
- RViz shows plausible surrounding geometry over most of the 360-degree view;
- a matte target moved between known positions appears at approximately the expected distances;
- a short bag records and `rosbag info` can read it.

## Troubleshooting boundaries

### The serial device cannot be opened

Save these outputs and the launch error:

```bash
ls -l /dev/wheeltec_lidar
lsusb
dmesg | tail -n 30
```

Check only the normal power and cable connections. Do not use `chmod 777`, replace device rules, or reinstall a driver during the first inspection.

### `/scan` exists but no useful ranges appear

- Test with a large matte object at 0.5-2 m.
- Make sure nothing covers the LiDAR window.
- Save one `/scan` message and the driver output.
- Do not change the `/rev_order` speed control during the baseline.

### RViz reports a fixed-frame error

Set the fixed frame to `laser`. This sensor-only view deliberately avoids depending on the full robot transform tree.

### There is no graphical desktop over SSH

Skip RViz, record the `/scan` bag, and copy it to another ROS computer for visualization. Do not install a desktop environment merely for this test.

## Evidence to bring back

- LiDAR label photograph;
- complete `lsusb` and `/dev/wheeltec_lidar` output;
- launch-terminal output;
- `rostopic list | grep scan`;
- measured `/scan` rate;
- one `/scan` message;
- RViz screenshot with the test target;
- target distances and observed behaviour;
- `lsn10_test.bag` and its `rosbag info` output.
