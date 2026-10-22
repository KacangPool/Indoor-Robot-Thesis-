# Analysing many ROS 1 topics without typing each name

Update 2026-10-22 (modular source): the updated Python tools require the sibling
`fahad_core/` folder. Do not follow the older single-file copy steps below alone.
Use the complete bundle instructions in [Tools/README.md](../Tools/README.md).
Original command names and existing installed robot copies are unchanged; this
local refactor was not deployed. See [architecture/verification notes](MODULAR_CODE_ARCHITECTURE.md).

## Live graphical overview

With the relevant robot launch running:

```bash
source ~/wheeltec_robot/devel/setup.bash
rqt_topic
```

`rqt_topic` presents the live topic tree in one window. It is useful for checking topic names, message types, publication rate and bandwidth and for expanding message fields. If the direct command is unavailable, try:

```bash
rqt --standalone rqt_topic
```

Use this while the robot is stationary during diagnosis. Selecting camera point-cloud topics can activate extra processing load.

## Programming-reference report (version 2)

Copy BOTH `Tools/ros_topic_report.sh` and `Tools/ros_message_sample.py` into the same personal directory:

```text
/home/wheeltec/fahad/tools/ros_topic_report.sh
/home/wheeltec/fahad/tools/ros_message_sample.py
```

Then run one command:

```bash
source ~/wheeltec_robot/devel/setup.bash
bash -n ~/fahad/tools/ros_topic_report.sh
bash ~/fahad/tools/ros_topic_report.sh
```

The script:

- inventories all topics, including advertised message types and connection counts;
- by default samples up to 22 selected development interfaces that exist in that run, with RGB/depth/LiDAR before housekeeping topics;
- records publisher/subscriber connections and the installed `rosmsg show` definition for each selected topic;
- shows actual values from one received message, including the first 16 entries of ordinary arrays and nested structures (up to 240 field-preview lines);
- shows up to nine decoded image pixels, up to eight decoded PointCloud2 points, a bounded LiDAR range summary and occupancy-cell counts;
- prints progress markers distinguishing initialization, message waiting and cleanup;
- uses a 15-second deadline per information command and a 25-second deadline per complete sample process, followed by a forced stop after another two seconds if needed;
- saves a uniquely named report under `~/fahad/reports`, with `REPORT COMPLETE` inside the file when the loop finishes.

The Python helper waits ten wall-clock seconds for a message AFTER ROS initialization. The outer deadline includes initialization, waiting, formatting and cleanup, so a slow startup can still consume the sample budget. A deadline is not proof of no data: inspect whether `MESSAGE RECEIVED` or `SAMPLE COMPLETE` appeared first. These time limits handle ordinary stalled child processes, not an unresponsive OS, filesystem or terminal.

The reader only subscribes; it does not publish robot commands, change settings or launch mapping. Subscriptions can activate lazy camera/cloud processing and add load. Use it while stationary, not during navigation or performance benchmarking. `/cmd_vel` and goal topics may be silent; do not send movement commands just to obtain a sample.

For a detailed sample/definition attempt for EVERY topic, including settings and transport variants:

```bash
ROS_TOPIC_REPORT_MODE=all bash ~/fahad/tools/ros_topic_report.sh
```

Start with the default core report. The uploaded inventory contains 188 topics, so all mode can take tens of minutes or longer if many operations time out. Both modes retain the complete inventory; only all mode tries to sample every topic. The all-topic list is a snapshot taken at startup, not continuous discovery.

For a slow robot, an optional larger process budget (the post-initialization message wait remains ten seconds):

```bash
ROS_TOPIC_QUERY_TIMEOUT=30s ROS_TOPIC_SAMPLE_TIMEOUT=45s bash ~/fahad/tools/ros_topic_report.sh
```

Use the ROS Python interpreter (normally `python` for Melodic), not an unrelated virtual environment. No pip installation is needed for the helper. It uses the robot's installed ROS libraries. If copying from Windows produces errors mentioning `\r`, convert only the copied personal files to Unix line endings before retrying.

Ten offline tests cover the formatting and selected numeric decoders. Live ROS subscription, PointCloud2 decoding against installed messages, Python 2 execution and the Bash wrapper have not been tested on this Windows machine. The robot-side syntax check above is still required. The separate camera diagnostic script remains the tool for sustained camera rates/valid-depth statistics; this report is a one-message reference, not a full benchmark or ML dataset.

## Quick inventory without message samples

For just connection/type information, without message contents:

```bash
mkdir -p ~/fahad/reports
timeout --kill-after=2s 15s rostopic list -v | tee ~/fahad/reports/rostopic_inventory.txt
```

It shows topic names, types, publishers and subscribers, but not message contents.

## Why not print all raw messages continuously

Camera images, depth images, point clouds and LaserScan arrays contain thousands or millions of values and may publish around 10-30 times per second. Echoing them all concurrently would create an unreadable terminal stream, add processing load and obscure the small metadata fields needed for diagnosis.

Version 1 hid all arrays, including useful calibration, ranges and transforms. Version 2 previews them and labels truncation. Large binary images/clouds are decoded selectively, not fully printed. Nine image pixels can all be invalid while other pixels are valid; the first eight cloud points can be NaN while later points are usable. Never treat these examples as whole-sensor quality measurements.

See `ROS_TOPIC_PROGRAMMING_REFERENCE.md` for the uploaded report findings, field meanings and development uses.

Avoid `rosbag record -a` on this robot for an unbounded recording. Previous measurement found raw RGB alone at roughly 27.4 MB/s; RGB, depth and point clouds together can fill storage rapidly. Use a short, explicitly selected topic list once the experiment question is defined.
