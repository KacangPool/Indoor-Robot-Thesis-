# v0.12 — plain LiDAR plane and honest point colours

2026-10-22. Local display update, not deployed or physically tested by tools.

User's `/map` output has no publishers and the dashboard reader as subscriber.
That establishes no published OccupancyGrid at that moment, not that the LiDAR is
off. Later `/scan` output registers `/lsn10` and the dashboard reader, but an
eight-second `rostopic hz /scan` check receives no new messages. User clarifies
the Hub had been closed. This is not proof of a healthy active scan, nor proof
that closing the Hub automatically shuts down the LiDAR hardware/node. Hub close
normally stops/disconnects its own control/SSH path, not every background ROS node.
Repeat after Connect & prepare with the robot stationary; do not launch duplicates.

## Display

- Removed decorative radar rings, crosshairs and axis labels from scan-only view.
  Plain neutral canvas, actual current returns and illustrative origin car remain.
  No shaded free-floor sectors are invented between laser endpoints.
- One fixed point-colour scale, no selector: sensor distance, red at 0 m through
  yellow/green/cyan to blue at 4 m. Scan-only display radius remains 4 m; mapped
  overlays can include farther points, saturated blue at 4+ m.
- Mapped points retain their original laser-relative ranges alongside transformed
  coordinates. Colour never uses distance from the arbitrary map origin. Missing
  corresponding range is shown mint rather than an invented distance colour.
- Existing real OccupancyGrid layer is retained when available. Its unknown/
  occupancy shading is map data, not radar decoration. Missing `/map` remains
  labelled scan-only, not falsely shown as a working SLAM map.
- Speed, steering, drive/fault guards, map/TF freshness, networking, vendor files
  and mapping startup remain unchanged. No SLAM, navigation or drivers started.

## Colour interpretation

RViz point colours depend on the chosen colour transformer; the photograph alone
does not establish its configuration. This implementation explicitly chooses
distance. A point colour is not a person/chair/table/material label. ROS LaserScan
provides geometric ranges and optional device-specific intensity, not object classes.
Intensity is not a unique material/object identifier or calibrated absorption.
Camera detection plus verified geometric association is still needed for the
project's semantic labels; it has not been added by recolouring points.

Primary definitions:
[LaserScan](https://raw.githubusercontent.com/ros/common_msgs/noetic-devel/sensor_msgs/msg/LaserScan.msg),
[OccupancyGrid](https://raw.githubusercontent.com/ros/common_msgs/noetic-devel/nav_msgs/msg/OccupancyGrid.msg).

## Update/check

At standstill, close old dashboard tabs and Hub, reopen Hub and Connect & prepare.
Use one new v0.12 page. In a robot SSH terminal, while the Hub is connected:

```bash
timeout -k 2s 8s rostopic info /scan
timeout -k 2s 10s rostopic hz /scan
```

A registered publisher alone is insufficient: expect actual rate output. If
there are still no messages, provide the Hub's LiDAR log and fresh status rather
than starting a second driver. Mapping needs its own `/map` publisher and TF;
activating LiDAR alone does not generate an occupancy map.

## Verification

251 dashboard fake-ROS/loopback Python tests, 116 JS checks (91 frontend,
11 geometry/ramp, 14 historical one-shot) pass; 45 Hub tests run, 44 pass and
one Windows symlink-privilege skip. Added checks for no decorative strokes,
near/middle/far colours, stale-point hiding and sensor-range map colours.
JS syntax and Python3.6 grammar pass; no actual Jetson/Python2 or robot execution.

Disconnected synthetic scan inspected at 1280x720, labelled synthetic/no robot;
all control POSTs rejected. Preview assets under `tmp/hud_v012_review/`, not
training data or live integration. Local preview stopped after checking. Actual
scan stream, display on robot/phone and mapping availability remain unverified.
