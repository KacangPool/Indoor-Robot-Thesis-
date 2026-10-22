# Windows Robot Hub and dashboard v0.6

Current source is v0.7: see `ROBOT_HUB_V07_OPERATING_NOTES.md` for working
indicators, stop-reason collection, independent joystick layout, LiDAR colours,
disconnection and shutdown. Ceiling remains 0.10 m/s; v0.6 startup notes below
remain applicable but do not describe all current features.

Prepared 2026-10-21. Local implementation, not yet deployed/physically verified.

Use `Tools/robot_hub/Start Robot Hub.cmd` to launch the native laptop app. Read
`Tools/robot_hub/README.md` for first-use steps, migration from existing terminals,
privacy, update/backups, checks and limitations. Keep both the `robot_hub` and
`remote_dashboard` source folders in their current locations.

Normal intended routine: power robot on, join robot Wi-Fi, open the hub, enter
password, acknowledge stationary setup, **Connect & prepare**, then open the
browser workspace. No manual ROS/tunnel terminals should be needed when the
hub starts the services after a normal fresh boot. This is not yet a confirmed
live startup result, and conflicts may still require diagnosis.

The hub configures only the established camera/YOLO, sensor-only LiDAR wrapper,
isolated base and personal dashboard. It does not launch mapping/navigation.
Startup never sends a driving command. Driving remains explicit held input in
the website, which is retained for other devices with a trusted connection.

v0.6 joystick maximum request is **0.10 m/s**; buttons remain 0.03 m/s. Actual
speed is not guaranteed. Existing feedback guards remain unchanged, so overshoot
near 0.10 m/s can fault; this requires observation, not automatic guard raising.
No physical emergency stop, obstacle avoidance or proven firmware/host-failure
stop is introduced. Closing the hub does not shut the robot down.

Latest user observation: LiDAR began working after its driver was activated.
This supports an inactive-driver explanation for the prior no-publisher graph,
not measured scan quality/rate or physical LiDAR model confirmation. User still
reports a 0.03 m/s ceiling; deployment mismatch, buttons rather than joystick,
and deflection remain possible explanations, not an established diagnosis.

First live acceptance: stay stationary while connecting; check running v0.6,
joystick limit 0.1, recent camera/YOLO and scans, and base readiness. Then briefly
test a small straight input/release, followed by modestly larger inputs only if
normal stopping is observed, with direct sight and physical power-off reachable.
Do not test disconnect/host-fault stopping by allowing unattended motion. Save
a hub status report and logs on any failure; do not launch duplicate drivers.
