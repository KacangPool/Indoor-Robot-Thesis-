# Inspection of uploaded RTAB-Map test.db

Inspected on 2026-09-16. Source: `Terminal Reports/test.db` (106,496 bytes). No WAL or SHM sidecar was present in the uploaded Terminal Reports folder. Conclusions apply to this uploaded snapshot, not to files that may subsequently change on the robot.

## Conclusion

The uploaded file is a structurally valid RTAB-Map SQLite database with no saved mapping observations or map. It is an initialized database, not a usable room map. It cannot provide the reference map required by the copied localization-mode `3d_navigation.launch`.

The absence of map data is established by querying the tables and saved-map fields, rather than inferred from the file size. It does not establish why the database is empty or whether maps exist elsewhere on the robot.

## Evidence

| Check | Result |
|---|---|
| SQLite integrity check | `ok` |
| Database schema version stored in Admin | `0.20.23` (not independent proof of currently installed software version) |
| Node rows: stored map positions/observations | 0 |
| Data rows: stored camera/depth/scan records | 0 |
| Link rows: relationships between map positions | 0 |
| Feature / Word / GlobalDescriptor rows | 0 / 0 / 0 |
| Statistics rows | 0 |
| Admin rows / Info rows | 1 / 2 |
| Saved optimized occupancy map | NULL |
| Saved optimized cloud, node IDs and poses | All NULL |
| Preview image / last localization | Both NULL |
| Admin time_enter | `2023-03-02 13:22:32` (stored value; timezone unspecified) |
| Info summaries | Both report zero STM size, last sign added and dictionary size |

The file occupies space because the database structure and metadata exist even when map observations are absent.

## Verification and preservation

- Opened with Python SQLite using URI `mode=ro` and additionally enabled `PRAGMA query_only=ON`.
- Ran `PRAGMA integrity_check`, inspected the table schema, counted every table and checked saved map/cloud fields without modifying the database.
- SHA-256 before inspection completion: `380F935B734C15B6DF826A6C8028D72F58A38E6C4BF7648E41875A1962BA7148`.
- Verified the same SHA-256 after inspection/documentation work.
- No robot access, launch execution, map creation, configuration edits or motion occurred.

## Implication for the next lab session

Launching the existing navigation setup with this file will not yield a previously mapped room to navigate through. A mapping session, or locating another valid existing database, must precede map-based navigation.

For a new session, prepare a separate reviewed mapping launch under the user's `~/fahad` folder and use a new explicit database path there. The vendor mapping include resets its default database at startup. No custom launch has been created or run as part of this inspection.

Mapping will require observations from different positions, correct camera/LiDAR transforms and working odometry. Establish supervised manual driving and the physical stop procedure before moving the robot. Keep camera tilt fixed or update its transform to match. Camera/LiDAR viewers and stationary depth testing can continue while these prerequisites are resolved.

AMCL was subsequently confirmed discoverable. Remaining checks are depth validity/registration, scan quality, odometry/TF and live-versus-copied launch compatibility. AMCL availability is a navigation prerequisite, not evidence that map creation has occurred.
