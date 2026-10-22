# Registered-depth monitor: first full-image statistics

Evidence: `Terminal Reports/depth_check_20261012_142749.txt`, uploaded 2026-10-12. Ten printed snapshots span 2.0-20.4 seconds. The report does not establish why printing ended or whether the original 25-second command completed normally. Input file preserved.

## What was measured

- RGB: `/camera/rgb/image_raw`, 640x480 `rgb8`; initial 27.3 arrivals/s, then 29.5-30.0.
- Depth: `/camera/depth_registered/image_raw`, 640x480 `32FC1`; initial 26.4 arrivals/s, then 29.5-30.0.
- Full-image finite-positive depth fraction: 58.4-60.3%; unweighted mean of the ten printed snapshots 59.38%. This is not a time-weighted statistic or a measurement on every depth frame.
- Minimum retained depth: 0.87-0.96 m; per-snapshot median 3.76-4.03 m; maximum 9.78 m in every snapshot.
- RGB CameraInfo: `camera_rgb_optical_frame`, calibration 640x480, fx/fy approximately 582.8/584.4 px, cx/cy 321.4/246.0, `plumb_bob`. This monitor does not print the depth image frame or registered-depth CameraInfo.
- RGB brightness 107.6-114.9/255; dark pixels 32.3-37.7%, bright pixels 11.5-16.7%. The script defines these as brightness below 30 or above 225, respectively. They describe this imagery, not a pass/fail quality score.

Arrival rates are subscriber observations, not unique-frame inference FPS, camera/depth synchronization, or a sustained benchmark. Although requested alongside YOLO, this report alone does not inventory the detector/filter processes running during acquisition.

## Crucial meaning of 'valid'

Checked the complete `Tools/camera_diagnostics_ros1.py`. It samples full-image pixel statistics at most twice per second, printing the latest analysis every approximately two seconds. It accepts pixels where `isfinite(metres)` and `metres > 0`. There is no physical operating-range, confidence, saturation-code, target-mask or accuracy test.

Thus approximately 59% of pixels contain finite positive numbers; this is not 59% proven accurate measurements. Approximately 40% fail that numerical rule in these sampled frames, but the report cannot separate NaN, infinity, zero or negative values. The median is across all retained scene pixels, not a person's distance. The 32FC1 payload is treated as floating-point metres; it is not automatically divided by 1000 based on its topic name.

The `RuntimeWarning: invalid value encountered in greater` occurs at the validity-comparison line. Statistics continue afterwards, so this is not a demonstrated crash. Invalid-value comparisons are the likely source, but exact invalid values cannot be inspected without pixel data. The final mask excludes nonfinite/nonpositive values. No blanket warning suppression, script fix or package upgrade was implemented.

## Range discrepancy: unresolved, not a new hardware identification

Re-read [Orbbec's original Astra-series specifications](https://www.orbbec.com/products/structured-light-camera/astra-series/) on 2026-10-12: the S variant's stated depth range remains 0.4-2 m. Finite medians near 3.9 m and the repeated 9.78 m maximum do not establish accurate extended range, a different camera model or a known failure mechanism. This report cannot decide whether the discrepancy involves out-of-range/noisy measurements, encoding/conversion or configuration, limiting values, or a hardware/driver mismatch. Do not scale distances or alter camera calibration by guesswork.

Next: compare an identifiable matte target at a measured approximately 1 m with the local depth region; inspect raw/registered depth and current camera settings/identity as needed. Verify RGB/depth boundaries and the earlier CameraInfo discrepancy before assigning depth to RGB boxes. Validate image-time association before live person-distance output. Until then, camera depth is available as a stream, not validated for mapping or control.

## AI harness side discussion

The user's question about an AI harness was treated as conceptual, not authorization to install one or call an API. Using the OpenAI Docs skill, fetched [official agent sandbox documentation](https://developers.openai.com/api/docs/guides/agents/sandboxes). A harness is the orchestration around a model: tool execution/routing, working state, approvals, recovery and tracing. It can support a documentation workflow, but documentation is an application, not its definition.

For this project, an analogous optional workflow could read an uploaded lab report, produce a source-linked summary, distinguish observations from hypotheses, update continuity notes and propose next steps. Existing `AGENTS.md`, `PROJECT_CONTEXT.md`, `CHANGELOG.md` and this app's file tools already supply some useful pieces; the notes alone are not an autonomous harness or guaranteed memory. No new harness, external image upload, recurring monitoring, model choice or architecture commitment was made. A specific product/video name remains to be clarified if that is what the user meant.
