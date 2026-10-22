# GitHub connection and Hochschule Merseburg Wi-Fi

2026-10-22. User approved creating **private** `KacangPool/indoor-sar-robot` and
identified Hochschule Merseburg as the campus. This does not authorize public
hosting, exposing robot ports or disabling existing connection/motion guards.

## GitHub: what is connected and what is pending

- Local Git already has source-only history. Working tree was clean before this
  documentation update; no remote is configured.
- The GitHub connector recognizes authenticated login `KacangPool`. That proves
  the account connection here, not access to every private repository or an
  independent browser login.
- The repository lookup returned 404: it is not currently accessible through the
  connector. Absence versus private-repository permission cannot be distinguished
  from that response alone.
- Available connector tools do not include repository creation. GitHub CLI is
  not installed on this laptop. The controlled in-app browser redirects
  `github.com/new` to sign-in, including after the user reports signing in and
  the page is refreshed. User's usual browser may have a different session.
- No repository has been created by this assistant, no code pushed, no permissions
  expanded, and no authentication token/password retrieved or requested in chat.

### Complete the private repository setup

In the user's already signed-in browser, visit [GitHub's new-repository page](https://github.com/new):

1. Verify owner **KacangPool**, name **indoor-sar-robot**, visibility **Private**.
2. Leave README, .gitignore and licence initialization off: local source history
   already exists and this session adds a project README.
3. Create the repository and report completion/link. Do not paste passwords or tokens.
4. Verify actual owner/name/private visibility and whether the repository is empty
   before configuring `origin` and pushing the existing `main` history. Do not
   overwrite an unexpected remote history or force-push.
5. If the connector cannot see the new private repository, authorize only this
   repository through its account/repository connection interface. Any interactive
   sign-in or permission confirmation remains a user action.

This app can already work on local project files. GitHub provides a remote source
copy/history and collaboration, not automatic live access to the robot. Only
committed files are shared, not an entire ChatGPT conversation or all project data.
Optional Codex cloud/review setup is separate from the local desktop workflow and
is not configured here. No need to install ChatGPT or GitHub tools on the old Jetson
just to continue editing locally and deploying reviewed personal bundles by SSH.

Official context: [local projects](https://learn.chatgpt.com/docs/projects),
[Codex GitHub review integration](https://learn.chatgpt.com/docs/third-party/github),
and [optional cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments).
An existing account connection does not guarantee browser authentication,
repository scope or identical capabilities in a separate ChatGPT session.

## Campus Wi-Fi: possible, not yet demonstrated

Yes, in principle: both devices join the campus infrastructure and communicate
through that network. They need not stay within each other's direct Wi-Fi range;
each must remain within useful access-point coverage. Actual routing/peer policy,
latency, congestion, roaming and packet loss still matter. The same eduroam SSID
does not guarantee the same reachable network, including across institutions.

Hochschule Merseburg publishes Linux and manual setup instructions using easyroam,
institutional sign-in/second factor and certificate profiles. Its public WLAN page
does not establish that laptop-to-robot SSH is permitted or that current Linux
installers support this old Jetson environment. Use the institution's setup and
confirm the robot's actual OS/architecture before installing anything.
[University WLAN guidance](https://www.hs-merseburg.de/hochschule/einrichtungen/it-servicezentrum/service/wlan/).

The user accepts a temporary thesis arrangement. The outstanding peer-access
question is a **technical reachability condition**, not a request for additional
security machinery. Keep the working SSH tunnel; it already protects the dashboard
without requiring a public web server. An institutional Wi-Fi name alone does not
make every connected device or service trusted. Do not disable certificate checks:
[NetworkManager guidance](https://www.networkmanager.dev/docs/api/latest/settings-802-1x.html).

### Next lab test — stationary and with a local fallback

1. Keep a monitor/keyboard or other known local recovery path for the first network
   change. Switching one Wi-Fi adapter from robot hotspot to campus client mode can
   end the current SSH session; simultaneous AP/client support is unconfirmed.
2. Inspect Ubuntu version, CPU architecture and NetworkManager/interface state.
   Obtain the approved easyroam Linux/manual profile locally; don't place certificate
   or private-key material in Git or chat. No guessed EAP/CA settings or upgrades.
3. Connect the robot using the approved profile, then check its assigned address
   locally. The hotspot address `192.168.0.100` is not assumed on campus Wi-Fi.
4. From laptop **PowerShell**, with both devices on campus Wi-Fi, test the actual
   robot address on TCP22 using `Test-NetConnection ROBOT_IP -Port 22`. Replace
   ROBOT_IP first. Ping failure alone does not prove SSH is blocked.
5. If TCP22 succeeds, verify the SSH host identity and inspect status without
   starting motion. Then test the existing tunnel and read-only camera view.
6. The Hub currently accepts only private IPv4 addresses. Campus addressing may
   differ; inspect the assigned address before deciding whether scoped support is
   needed. Do not remove the guard wholesale or assume a globally numbered campus
   address means the robot is publicly reachable.
7. Test stationary message freshness and disconnection/roaming behaviour before
   any supervised movement. The current stopping guards must not be loosened just
   to tolerate an unreliable link. Coverage is not guaranteed outside campus.

If peer traffic is blocked, ask the network team for an approved robotics/lab/IoT
network or a permitted routed connection. Do not try to bypass institutional
network isolation. Network registration/WLAN/eduroam contact is published at
[ITZ service overview](https://www.hs-merseburg.de/hochschule/einrichtungen/it-servicezentrum/service/serviceuebersicht/).
No university email was sent and no policy/permission is assumed.

Verification: read local Git/configuration/tunnel source, connector login and
repository lookup, controlled browser state, official OpenAI and university/network
documentation. No new runtime code, Wi-Fi changes, package installs, credential
handling, robot access, measurements or connectivity test occurred. Missing live
scan and camera–LiDAR calibration/association questions are unchanged.
