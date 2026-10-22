/* Local console. Default rehearsal; live mode requires explicit robot-side flag. */
'use strict';
const ui = id => document.getElementById(id);
const owner = Array.from(crypto.getRandomValues(new Uint8Array(16)), b => b.toString(16).padStart(2, '0')).join('');
let key = null, bootId = null, generation = null, sequence = 0, desired = 'neutral';
let connected = false, busy = false, arming = false, safetyEpoch = 0, frameBusy = false;
let source = 'rgb', objectUrl = null, pointer = null, imageReady = false;
let keyboardSource = null;
let lastStatus = null, lastStatusAt = 0;
let driveMode = false, steeringMode = false, imageDecodedAt = 0;
let joystickInput = {throttle:0,steering:0};
let stick = null;
let sessionMode = false, motion = 0, releasePending = false, sendPending = false;
const clientEvents = [];
let lastCommandRtt = null;
let travelPedal = null;
let pendingTravel = null, manualStopLock = false;
let mapView=null, mapFetchedAt=0, mapBusy=false;
const travelKeysDown = new Set();
const brakesHeld = new Set();
const steeringKeysDown = new Set(), steeringKeysActive = new Set();
const steeringKey = event => ({KeyA:-1,KeyD:1})[event.code];
function updateKeyboardSteering(){
  joystickInput.steering=steeringKeysActive.has('KeyA')===steeringKeysActive.has('KeyD')?0:steeringKeysActive.has('KeyA')?-1:1;
  ui('steering-left').classList.toggle('active',joystickInput.steering<0);
  ui('steering-right').classList.toggle('active',joystickInput.steering>0);
  ui('joystick-readout').textContent='A / D steering · '+(joystickInput.steering<0?'LEFT':joystickInput.steering>0?'RIGHT':'CENTRED');
}
const travelKey = event => ({KeyW:1,ArrowUp:1,KeyS:-1,ArrowDown:-1})[event.code];
const splitMode = () => sessionMode && ui('joystick-mode').value==='steering';
const directions = Array.from(document.querySelectorAll('.direction'));
const labels = {neutral:'READY', forward:'FORWARD', forward_left:'FORWARD · LEFT ARC',
  forward_right:'FORWARD · RIGHT ARC', reverse:'REVERSE', reverse_left:'REVERSE · LEFT ARC', reverse_right:'REVERSE · RIGHT ARC',joystick:'JOYSTICK'};

const sensorView=window.FahadSensorView.create({ui,pill,seconds,document,
  getMap:()=>mapView,canUseMap:()=>connected && performance.now()-mapFetchedAt < 1800});

function diagnosticReport() {
  const c=lastStatus && lastStatus.control;
  return {version:lastStatus && lastStatus.version,client_events:clientEvents.slice(),
    dashboard_connected:connected,
    last_command_roundtrip_ms:lastCommandRtt,backend_disable_events:c && c.disable_events || [],
    backend_last_disable:c && c.last_disable || null,backend_readiness:c && c.readiness,
    heartbeat_lease_ms:c && c.timeout_ms,reported_speed_fault_limit_m_s:c && c.reported_speed_fault_limit_m_s,reported_yaw_fault_limit_rad_s:c && c.reported_yaw_fault_limit_rad_s,cameras:lastStatus && lastStatus.cameras};
}
function renderDiagnostics() {
  const backend=lastStatus && lastStatus.control && lastStatus.control.last_disable;
  ui('last-client-stop').textContent=clientEvents.length?clientEvents[clientEvents.length-1].reason:'None recorded on this page';
  ui('last-backend-stop').textContent=backend?backend.reason:'None recorded by this server';
  ui('diagnostic-output').textContent=JSON.stringify(diagnosticReport(),null,2);
}

function pill(id, text, kind = '') { ui(id).textContent = text; ui(id).className = 'pill' + (kind ? ' ' + kind : ''); }
function updateControls(note) {
  if(splitMode() && pointer===null)updateKeyboardSteering();
  const status = lastStatus && lastStatus.control;
  const liveReady = !driveMode || (status && status.ready && imageReady && performance.now()-imageDecodedAt < 1000 && performance.now()-lastStatusAt < 1000 && ui('drive-ack').checked && !document.hidden && document.hasFocus());
  ui('arm').disabled = !connected || Boolean(generation) || arming || !liveReady;
  ui('arm').hidden = sessionMode && Boolean(generation);
  ui('arm').textContent = driveMode ? generation ? 'Controls enabled' : status && status.stage === 'stopping' ? 'Stopping · waiting for feedback' : steeringMode ? 'Enable driving controls' : 'Enable forward controls' : generation ? 'Rehearsal enabled · no motors' : 'Enable rehearsal';
  if(splitMode() && !generation && liveReady && !manualStopLock)ui('arm').textContent=arming?'Enabling from fresh travel input…':'Ready · hold W/S or a travel pedal to enable';
  directions.forEach(button => {
    button.disabled = !connected || !generation || (sessionMode && (releasePending || !['armed','holding'].includes(status.stage))) || (driveMode && !(status.allowed_actions || ['forward']).includes(button.dataset.action));
    button.classList.toggle('active', Boolean(generation) && button.dataset.action === desired);
  });
  ui('joystick-panel').hidden = !steeringMode || !stick;
  ui('joystick-pad').disabled = !connected || !generation || !steeringMode || (sessionMode && !splitMode() && (releasePending || !['armed','holding'].includes(status.stage)));
  ui('pedal-controls').hidden = !splitMode();
  ui('direction-controls').hidden = splitMode();
  ui('stick-up').textContent=splitMode()?'STEERING ONLY':'FORWARD';
  ui('stick-down').textContent=splitMode()?'TRAVEL: W / S':'REVERSE';
  ui('joystick-pad').ariaLabel=splitMode()?'Steering only: drag left or right. Hold W or S, or a travel pedal, to move. Releasing travel requests stop.':'Joystick: drag up or down to travel, left or right to steer. Release to stop.';
  ui('joystick-pad').classList.toggle('independent',['independent','steering'].includes(ui('joystick-mode').value));
  for(const id of ['pedal-forward','pedal-reverse']) {
    const pendingButton=pendingTravel && pendingTravel.button===ui(id);
    const readyToPress=generation?['armed','holding'].includes(status && status.stage):liveReady && !manualStopLock && !arming;
    ui(id).disabled=!splitMode() || !connected || brakesHeld.size>0 || releasePending || (!readyToPress && !pendingButton);
  }
  ui('pedal-brake').disabled=!splitMode() || (!generation && !pendingTravel);
  ui('pedal-speed-value').textContent=(travelPedal?travelPedal.direction*travelPedal.speed:0).toFixed(3)+' m/s ramp request';
  ui('intent').textContent = generation ? labels[desired] : 'DISABLED';
  ui('speed-request').textContent = ((generation && status && Number.isFinite(status.requested_linear_m_s)) ? status.requested_linear_m_s : 0).toFixed(3)+' m/s';
  const ceiling = status && (status.joystick_speed_request_m_s || status.speed_request_m_s);
  ui('speed-limit').textContent = steeringMode && Number.isFinite(ceiling) ? ceiling.toFixed(2)+' m/s' : '—';
  if (note) ui('control-note').textContent = note;
}
const operation = name => '/api/'+(driveMode ? 'drive' : 'rehearsal')+'/'+name;
async function request(path, body) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), driveMode ? 450 : 1200);
  try {
    const options = {cache:'no-store', signal:controller.signal, credentials:'same-origin'};
    if (body !== undefined) Object.assign(options, {method:'POST', headers:{'Content-Type':'application/json', 'X-Dashboard-Key':key || ''}, body:JSON.stringify(body)});
    const response = await fetch(path, options);
    if (!response.ok) {
      let payload={};try{payload=await response.json();}catch(_){}
      const error=new Error(payload.error || 'HTTP request rejected');error.status=response.status;error.control=payload.control;
      throw error;
    }
    return await response.json();
  } finally { clearTimeout(timer); }
}
function clearInput() {
  steeringKeysActive.clear();
  const pending=pendingTravel;pendingTravel=null;
  if(pending && pending.button && pending.button.hasPointerCapture && pending.button.hasPointerCapture(pending.id))pending.button.releasePointerCapture(pending.id);
  retireTravel();
  desired = 'neutral'; pointer = null; keyboardSource = null;
  joystickInput = {throttle:0,steering:0};
  if (stick) stick.reset();
  updateKeyboardSteering();
}
function applySessionStatus(status) {
  if (!sessionMode || !status || typeof status.sequence !== 'number') return;
  if (!status.armed || status.owner !== owner) { stop(status.reason || 'Session disabled'); return; }
  if (status.sequence < sequence) return;
  if (lastStatus) lastStatus.control = status;
  if (status.stage === 'braking' || (desired !== 'neutral' && motion <= status.retired_motion)) {
    if(splitMode()){retireTravel();desired='neutral';joystickInput.throttle=0;}
    else clearInput();
  }
  updateControls(status.reason);
}
function releaseHold(preserveSteering=false) {
  if (!sessionMode || !generation) { stop(); return; }
  if(preserveSteering){retireTravel();desired='neutral';joystickInput.throttle=0;}
  else clearInput();
  releasePending = true; sendPending = false;
  const current = generation, issued = ++sequence;
  updateControls('Released; checking stationary feedback. Session stays enabled.');
  // Release is allowed to overtake an in-flight drive request. Its higher
  // sequence invalidates the old request, rather than queueing behind it.
  request(operation('command'), {owner,generation:current,sequence:issued,action:'neutral',motion})
    .then(status => { if (generation === current && issued === sequence) applySessionStatus(status); })
    .catch(() => { if (generation === current) stop('Release request failed; session disabled.'); })
    .finally(() => { if (generation === current) { releasePending = false; updateControls(); } });
}
function startInput(action) {
  if (sessionMode) motion++;
  desired = action; updateControls();
  if (sessionMode) { sendPending = true; heartbeat(); }
}
function advanceTravelRamp() {
  if(!splitMode() || !travelPedal)return true;
  const now=performance.now(),pedal=travelPedal;
  pedal.speed=window.FahadJoystick.rampSpeed(pedal.speed,pedal.braking,(now-pedal.updatedAt)/1000);
  pedal.updatedAt=now;
  if(pedal.braking && pedal.speed<=0){releaseHold(true);return false;}
  const ceiling=lastStatus && lastStatus.control && lastStatus.control.joystick_speed_request_m_s;
  if(!Number.isFinite(ceiling) || Math.abs(ceiling-.30)>1e-9){stop('Speed configuration mismatch; load the matching dashboard and backend.');return false;}
  joystickInput.throttle=pedal.speed>0?pedal.direction*(.12+.88*pedal.speed/ceiling):0;
  return true;
}
function retireTravel() {
  const old=travelPedal;travelPedal=null;
  if(old && old.button && old.button.hasPointerCapture && old.button.hasPointerCapture(old.id))old.button.releasePointerCapture(old.id);
}
function startTravel(direction,kind,id,button=null) {
  if(!splitMode() || !generation || !connected || brakesHeld.size>0 || releasePending || !lastStatus || !['armed','holding'].includes(lastStatus.control.stage))return false;
  if((kind==='key' && travelKeysDown.size>1) || (kind==='pointer' && travelKeysDown.size>0)) {releaseHold(true);return false;}
  if(travelPedal){releaseHold(true);return false;}
  travelPedal={direction,kind,id,button,speed:0,updatedAt:performance.now(),braking:false};motion++;
  joystickInput.throttle=0;
  desired='joystick';sendPending=true;updateControls();heartbeat();return true;
}
function releaseTravel(kind,id) {
  if(pendingTravel && pendingTravel.kind===kind && pendingTravel.id===id){stop('Travel released while enabling; no movement queued.');return;}
  if(kind==='key' && travelPedal && travelPedal.kind==='key') {
    const remaining=[...travelKeysDown].filter(code=>['KeyW','ArrowUp','KeyS','ArrowDown'].includes(code));
    if(remaining.length) {
      const opposite=remaining.find(code=>travelKey({code})!==travelPedal.direction);
      travelPedal.id=opposite || remaining[0];travelPedal.braking=Boolean(opposite);return;
    }
  }
  if(travelPedal && travelPedal.kind===kind && travelPedal.id===id)releaseHold(true);
}
function beginTravel(direction,kind,id,button=null) {
  if(generation)return startTravel(direction,kind,id,button);
  updateControls();
  if(!splitMode() || pendingTravel || arming || manualStopLock || ui('arm').disabled || brakesHeld.size || (kind==='key' && travelKeysDown.size!==1))return false;
  const press={direction,kind,id,button,epoch:safetyEpoch};pendingTravel=press;
  armControls().then(ok=>{
    if(!ok || pendingTravel!==press)return;
    const held=kind==='pointer' || travelKeysDown.has(id) && travelKeysDown.size===1;
    pendingTravel=null;
    if(!held || press.epoch!==safetyEpoch || !connected || document.hidden || !document.hasFocus() || !ui('drive-ack').checked || brakesHeld.size) {stop('Fresh travel confirmation lost while enabling; no movement queued.');return;}
    if(!startTravel(direction,kind,id,button))stop('Travel input changed while enabling; release and press afresh.');
  });
  return true;
}
function stop(note,forceNotify=false) {
  const previousGeneration=generation,owned=Boolean(generation || arming);
  note = note || (driveMode ? 'Stop requested. After cleanup, enable again on this page; no terminal restart.' : 'Rehearsal stopped. Enable again for another direction.');
  if (generation || arming) {
    clientEvents.push({at:new Date().toISOString(),reason:note,requested_intent:desired,last_command_roundtrip_ms:lastCommandRtt});
    if(clientEvents.length>20)clientEvents.shift();
    ui('drive-alert').hidden=false;ui('drive-alert').textContent=note;
  }
  safetyEpoch++;
  generation = null; releasePending = false; sendPending = false;
  clearInput();
  updateControls(note);
  renderDiagnostics();
  if (key && (owned || forceNotify)) request(operation('stop'),forceNotify?{}:{owner,generation:previousGeneration}).catch(() => {});
}
function hideImage(title, note) {
  if (driveMode && (generation || arming)) stop('Camera unavailable; stop requested. Enable again deliberately.');
  imageReady = false; ui('camera').hidden = true; ui('camera-empty').hidden = false;
  ui('camera-empty-title').textContent = title; ui('camera-empty-note').textContent = note;
  if (objectUrl) { URL.revokeObjectURL(objectUrl); objectUrl = null; }
}
function disconnected() {
  mapView=null;mapFetchedAt=0;sensorView.reset();
  connected = false;
  stop('Dashboard connection lost; controls disabled. Nothing will resume automatically.');
  hideImage('Dashboard connection lost', 'Old images are hidden. Check the robot and SSH connection.');
  pill('connection', 'Disconnected', 'warn'); pill('image-state', 'NO CONNECTION', 'warn');
  ui('image-age').textContent = '—'; ui('backend-health').textContent = 'Disconnected';
  ['rgb-health','yolo-health','scan-health'].forEach(id => { ui(id).textContent = 'Unknown'; });
  renderScan({state:'disconnected',available:false});
}
function seconds(value) { return value === null || value === undefined ? '—' : value.toFixed(1) + ' s'; }
function renderScan(scan){return sensorView.renderScan(scan);}
function drawScan(scan){return sensorView.drawScan(scan);}
function drawOccupancy(map){return sensorView.drawOccupancy(map);}
function rangeColour(value){return window.FahadSensorView.rangeColour(value);}

async function pollMap(){
  if(connected && !mapBusy){
    mapBusy=true;
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),1500),expectedBoot=bootId;
    try{
      const response=await fetch('/api/map?revision='+(mapView?mapView.revision:''),{cache:'no-store',signal:controller.signal});
      if(!response.ok)throw new Error('No map');
      const next=await response.json();
      if(!connected || bootId!==expectedBoot)throw new Error('Map response belongs to old connection');
      if(next.available){
        if(!next.cells && mapView && next.revision===mapView.revision)next.cells=mapView.cells;
        if(!Number.isInteger(next.width)||!Number.isInteger(next.height)||next.width<=0||next.height<=0||next.width*next.height>65536||!Array.isArray(next.cells)||next.cells.length!==next.width*next.height||!next.origin||![next.resolution,next.origin.x,next.origin.y,next.origin.yaw].every(Number.isFinite)||next.resolution<=0||!next.cells.every(v=>Number.isInteger(v)&&v>=-1&&v<=100))throw new Error('Invalid map');
      }
      mapView=next;mapFetchedAt=performance.now();drawScan(lastStatus && lastStatus.scan);
      ui('map-state').textContent=next.available?'MAP · '+next.frame:next.error || '/map unavailable · scan only';
    }catch(_){mapView=null;ui('map-state').textContent='Map unavailable · scan only';if(connected)drawScan(lastStatus && lastStatus.scan);}
    finally{clearTimeout(timer);mapBusy=false;}
  }
  setTimeout(pollMap,1000);
}
async function poll() {
  const polledGeneration = generation;
  try {
    if (!key) { const bootstrap = await request('/api/bootstrap'); key = bootstrap.key; bootId = bootstrap.boot_id; }
    const status = await request('/api/status');
    if (status.boot_id !== bootId) { key = null; bootId = null; stop('Backend restarted. Reload/re-enable deliberately.'); throw new Error('Restart'); }
    const nextDrive = ['ros_manual_forward','ros_manual_ackermann'].includes(status.mode) && status.motor_output === true;
    if (nextDrive !== driveMode && generation) stop('Mode changed. Enable again deliberately.');
    driveMode = nextDrive;
    steeringMode = driveMode && status.mode === 'ros_manual_ackermann';
    const nextSession = steeringMode && status.control.session_persistent === true;
    if (nextSession !== sessionMode && generation) stop('Control profile changed; enable again.');
    sessionMode = nextSession;
    const previousControl = lastStatus && lastStatus.control, reportedControl = status.control;
    connected = true; lastStatus = status; lastStatusAt = performance.now();
    if (sessionMode && generation && reportedControl.armed && reportedControl.owner === owner && reportedControl.sequence < sequence && previousControl) lastStatus.control = previousControl;
    pill('connection', 'Dashboard connected', 'ok');
    const preview = status.mode === 'preview';
    ui('mode').textContent = driveMode ? steeringMode ? 'LIVE · car-like controls' : 'LIVE · supervised forward' : preview ? 'Interface preview · no robot' : 'ROS viewer · read-only';
    ui('safety-title').textContent = driveMode ? 'Live motor output is enabled on this server.' : 'Motor output is disconnected in this mode.';
    ui('safety-note').textContent = driveMode ? sessionMode ? splitMode()?' Held travel: 5 s S-curve to 0.30 m/s. Release/B requests zero. No collision protection; stopping distance unmeasured.':' Buttons request 0.03 m/s; joystick up to '+(status.control.joystick_speed_request_m_s || .03).toFixed(2)+' m/s depending on pull. Enable once; release requests stop. No verified hardware watchdog or obstacle avoidance.' : ' Maximum speed request 0.03 m/s; two-second hold limit. Release requests stop. Car-like curves only: no sideways/spin, obstacle avoidance or verified hardware watchdog.' : ' Controls below are rehearsal only. No browser action can drive the robot.';
    ui('control-title').textContent = driveMode ? steeringMode ? 'Keyboard driving · WASD' : 'Manual forward control' : 'Driving rehearsal';
    ui('control-kind').textContent = driveMode ? steeringMode ? 'LIVE · ACKERMANN' : 'LIVE · FORWARD ONLY' : 'NO MOTORS';
    ui('control-help').textContent = driveMode ? sessionMode ? splitMode()?'When checked, healthy and stationary, press fresh W/↑ or S/↓ to enable and ramp travel; A/D steers. Release steering centres it; both A+D centre too. Opposite travel key slows to zero, never automatic reverse. Release travel or B requests zero; Space/Escape disables. Held keys never resume after faults. No collision protection.':'Enable once, then hold a direction. Release requests zero and preserves a healthy session. Faults still disable.' : steeringMode ? 'Enable, then hold a direction. Release requests stop. Re-enable after cleanup and stationary feedback.' : 'Enable, then hold Forward. Release requests stop. Re-enable after cleanup and stationary feedback.' : 'Enable, then hold a direction. Releasing it ends the rehearsal. The car turns in arcs, not on the spot.';
    ui('drive-confirmation').hidden = !driveMode;
    ui('stop').textContent = driveMode ? 'Stop / disable · Space or Escape' : 'Stop rehearsal · Space';
    ui('intent-label').textContent = driveMode ? 'Requested intent' : 'Rehearsed intent';
    ui('motor-health').textContent = driveMode ? steeringMode ? 'Live capability · car-like motion' : 'Live capability · forward only' : 'Disconnected';
    ui('next-step').textContent = driveMode ? 'Direct physical observation required. Release is software stop, not a physical emergency stop. Firmware fault stopping remains unverified.' : 'Viewing/rehearsal only. Explicit robot-side opt-in is required for live control.';
    ui('backend-health').textContent = preview ? 'Preview backend' : 'ROS reader';
    for (const name of ['rgb','yolo']) ui(name+'-health').textContent = preview ? 'No robot connected' : status.cameras[name].available ? 'Recent message' : 'No recent image';
    ui('ros-note').textContent = status.ros_error || (driveMode ? 'Reads existing sensors and publishes bounded travel/yaw or zero requests to the isolated controller. No drivers or mapping are launched.' : preview ? 'Preview mode uses no ROS or robot connection. No sensor data are simulated as real.' : 'Reads existing ROS topics only. No drivers, mapping or motors are started.');
    const camera = status.cameras[source];
    ui('camera-topic').textContent = camera.topic;
    ui('image-age').textContent = camera.available ? 'Message received ' + seconds(camera.age_s) + ' ago' : 'No recent message';
    if (!camera.available) {
      hideImage(preview ? 'Interface preview · no camera' : 'No recent camera image', camera.error || (preview ? 'Connect the robot later to see its camera here.' : 'Start the existing camera/YOLO node separately. Frames older than 2 s are hidden.'));
      pill('image-state', preview ? 'PREVIEW ONLY' : 'NO RECENT IMAGE', preview ? '' : 'warn');
    } else { pill('image-state', imageReady ? 'RECENT MESSAGE' : 'LOADING IMAGE', imageReady ? 'ok' : ''); }
    renderScan(status.scan);
    // A poll sent before arm completed must not invalidate the new generation.
    if (generation && generation === polledGeneration && (!reportedControl.armed || reportedControl.owner !== owner)) stop(reportedControl.reason);
    if (generation && generation === polledGeneration) applySessionStatus(reportedControl);
    if (driveMode && !generation) ui('control-note').textContent = status.control.readiness || status.control.reason;
    renderDiagnostics();
    updateControls();
  } catch (_) { disconnected(); }
  setTimeout(poll, 500);
}
async function frame() {
  if (!frameBusy && connected && lastStatus && lastStatus.cameras[source].available && !document.hidden) {
    frameBusy = true;
    const selected = source;
    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 1200);
    try {
      const response = await fetch('/api/frame/'+selected, {cache:'no-store', signal:controller.signal});
      if (!response.ok) throw new Error('No recent image');
      const blob = await response.blob();
      if (selected === source && connected && performance.now()-lastStatusAt < 1500) {
        const next = URL.createObjectURL(blob), old = objectUrl;
        objectUrl = next;
        ui('camera').onload = () => { if (objectUrl === next && connected) { imageReady = true; imageDecodedAt = performance.now(); ui('camera').hidden = false; ui('camera-empty').hidden = true; updateControls(); } if (old) URL.revokeObjectURL(old); };
        ui('camera').onerror = () => hideImage('Image could not be decoded', 'Check the camera message encoding.');
        ui('camera').src = next;
      }
    } catch (_) {
      if (selected === source) { hideImage('No recent camera image', 'Waiting for a fresh, decodable image.'); pill('image-state','NO IMAGE','warn'); }
    } finally { clearTimeout(timer); frameBusy = false; }
  }
  setTimeout(frame, 330);
}
ui('source').addEventListener('change', () => { source = ui('source').value; hideImage('Switching camera view', 'Waiting for the selected source.'); });
ui('joystick-mode').addEventListener('change',()=>{
  if(generation || arming)stop('Joystick layout changed; enable again deliberately.');
  if(stick)stick.reset();
  ui('joystick-pad').classList.toggle('independent',['independent','steering'].includes(ui('joystick-mode').value));
  updateControls();
});
ui('drive-ack').addEventListener('change', () => { manualStopLock=!ui('drive-ack').checked;if (driveMode && !ui('drive-ack').checked) stop('Physical setup confirmation removed.'); updateControls(); });
async function armControls() {
  updateControls();
  if (ui('arm').disabled) return false;
  if (!connected || arming || generation || document.hidden || !document.hasFocus()) return false;
  arming = true; const epoch = safetyEpoch; updateControls();
  try {
    const result = await request(operation('arm'), {owner});
    if (epoch !== safetyEpoch || !connected || document.hidden || !document.hasFocus()) { stop(); return false; }
    generation = result.generation; sequence = 0; desired = 'neutral'; motion = 0; releasePending = false;
    ui('drive-alert').hidden=true;
    manualStopLock=false;
    if (sessionMode && lastStatus) Object.assign(lastStatus.control,{armed:true,owner,stage:'armed',sequence:0,retired_motion:0});
    updateControls(driveMode ? sessionMode ? 'Session enabled. Hold to drive; release to stop. No re-enable between normal holds.' : 'LIVE: hold an available control while watching the robot. Release requests stop; two-second maximum per hold.' : 'Rehearsal only: hold one direction. Release, switch tabs or lose connection to disable.');
    return true;
  } catch (_) { stop('Could not enable. Another browser may own the controls, or readiness/connection expired.');return false; }
  finally { arming = false; updateControls(); }
}
ui('arm').addEventListener('click',armControls);
directions.forEach(button => {
  button.addEventListener('pointerdown', event => {
    if(splitMode())return;
    if (button.disabled || !generation || pointer !== null || keyboardSource || (event.pointerType === 'mouse' && event.button !== 0)) return;
    event.preventDefault(); pointer = event.pointerId;
    try { button.setPointerCapture(event.pointerId); } catch (_) { stop('Pointer capture failed; session disabled.'); return; }
    startInput(button.dataset.action);
  });
  ['pointerup','pointercancel','lostpointercapture'].forEach(name => button.addEventListener(name, event => {
    if (pointer === event.pointerId) { if (name === 'pointerup') releaseHold(); else stop('Input cancelled; session disabled.'); }
  }));
  button.addEventListener('keydown', event => {
    if(splitMode())return;
    if (!button.disabled && pointer===null && !keyboardSource && (event.key === 'Enter' || event.key === ' ') && generation && !event.repeat) { event.preventDefault(); keyboardSource=button;startInput(button.dataset.action); }
  });
  button.addEventListener('keyup', event => { if ((event.key === 'Enter' || event.key === ' ') && keyboardSource === button) { event.preventDefault(); releaseHold(); } });
});
for(const [id,direction] of [['pedal-forward',1],['pedal-reverse',-1]]) {
  const button=ui(id);
  button.addEventListener('pointerdown',event=>{
    if(button.disabled || (event.pointerType==='mouse' && event.button!==0))return;
    event.preventDefault();
    if(!beginTravel(direction,'pointer',event.pointerId,button))return;
    try{button.setPointerCapture(event.pointerId);}catch(_){stop('Travel pedal capture failed; session disabled.');}
  });
  button.addEventListener('pointerup',event=>releaseTravel('pointer',event.pointerId));
  for(const name of ['pointercancel','lostpointercapture'])button.addEventListener(name,event=>{
    if([travelPedal,pendingTravel].some(p=>p && p.kind==='pointer' && p.id===event.pointerId))stop('Travel pedal '+name+'; session disabled.');
  });
  button.addEventListener('dragstart',event=>event.preventDefault());
}
ui('pedal-brake').addEventListener('pointerdown',event=>{
  if(!splitMode() || (!generation && !pendingTravel) || (event.pointerType==='mouse' && event.button!==0))return;
  event.preventDefault();brakesHeld.add('pointer:'+event.pointerId);releaseHold(true);
  try{ui('pedal-brake').setPointerCapture(event.pointerId);}catch(_){brakesHeld.delete('pointer:'+event.pointerId);stop('Brake capture failed; session disabled.');}
});
ui('pedal-brake').addEventListener('pointerup',event=>{
  brakesHeld.delete('pointer:'+event.pointerId);
  if(ui('pedal-brake').hasPointerCapture && ui('pedal-brake').hasPointerCapture(event.pointerId))ui('pedal-brake').releasePointerCapture(event.pointerId);
  updateControls();
});
for(const name of ['pointercancel','lostpointercapture'])ui('pedal-brake').addEventListener(name,event=>{
  if(brakesHeld.delete('pointer:'+event.pointerId))stop('Brake '+name+'; session disabled.');
});
ui('pedal-brake').addEventListener('click',()=>{if(splitMode() && generation && !releasePending)releaseHold(true);});
async function heartbeat() {
  if (generation && connected && !busy && !releasePending) {
    if (document.hidden || !document.hasFocus()) { stop('Driving page lost focus or was hidden; session disabled.'); return; }
    if (driveMode && (!imageReady || performance.now()-imageDecodedAt >= 1000)) { stop('Browser camera preview is missing or older than 1 s; stop requested.'); return; }
    if (driveMode && performance.now()-lastStatusAt >= 1000) { stop('Browser status is older than 1 s; stop requested.'); return; }
    if (driveMode && !ui('drive-ack').checked) { stop('Physical setup confirmation unavailable; stop requested.'); return; }
    if(!advanceTravelRamp())return;
    busy = true; const current = generation;
    const body = {owner, generation:current, sequence:++sequence, action:desired};
    sendPending = false;
    if (sessionMode) body.motion = motion;
    if (desired === 'joystick') Object.assign(body,joystickInput);
    const issuedAt=performance.now();
    try { const result = await request(operation('command'), body); lastCommandRtt=Math.round(performance.now()-issuedAt);if (current === generation && body.sequence === sequence) applySessionStatus(result); }
    catch (error) {
      if (current === generation && body.sequence === sequence) {
        lastCommandRtt=Math.round(performance.now()-issuedAt);
        if(error.control && lastStatus)lastStatus.control=error.control;
        const reason=error.control && !error.control.armed && (error.control.last_disable && error.control.last_disable.reason || error.control.readiness || error.control.reason);
        stop(reason?'Command rejected by backend: '+reason:error.name==='AbortError'?'Command request timed out; session disabled.':error.status?'Command rejected (HTTP '+error.status+'); session disabled.':'Command connection failed; session disabled.');
      }
    }
    finally { busy = false; if (sendPending && generation && !releasePending) heartbeat(); }
  }
}
ui('stop').addEventListener('click', () => {manualStopLock=true;stop(undefined,true);});
window.addEventListener('keydown', event => {
  if(steeringKey(event)){
    if(event.repeat || steeringKeysDown.has(event.code))return;
    steeringKeysDown.add(event.code);
    const editable=['INPUT','SELECT','TEXTAREA'].includes(event.target && event.target.tagName) || Boolean(event.target && event.target.isContentEditable);
    if(splitMode() && generation && connected && !editable && !event.ctrlKey && !event.altKey && !event.metaKey){
      event.preventDefault();if(pointer!==null){stop('Conflicting steering inputs; release and press afresh.');return;}steeringKeysActive.add(event.code);updateKeyboardSteering();updateControls();
    }
    return;
  }
  const direction=travelKey(event);
  if(direction) {
    if(event.repeat || travelKeysDown.has(event.code))return;
    travelKeysDown.add(event.code);
    const editable=['INPUT','SELECT','TEXTAREA'].includes(event.target && event.target.tagName) || Boolean(event.target && event.target.isContentEditable);
    if(splitMode() && !editable && !event.ctrlKey && !event.altKey && !event.metaKey) {
      event.preventDefault();
      if(travelPedal && travelPedal.kind==='key') {
        if(direction!==travelPedal.direction)travelPedal.braking=true;
      } else beginTravel(direction,'key',event.code);
      return;
    }
  }
  if(event.code==='KeyB') {
    if(event.repeat)return;
    brakesHeld.add('key');
    if(splitMode() && !event.ctrlKey && !event.altKey && !event.metaKey && !['INPUT','SELECT','TEXTAREA'].includes(event.target && event.target.tagName) && !(event.target && event.target.isContentEditable)) {
      event.preventDefault();if(generation || pendingTravel)releaseHold(true);return;
    }
  }
  if (event.key === 'Escape' || (event.code === 'Space' && (splitMode() || !event.target.classList.contains('direction')))) { event.preventDefault();manualStopLock=true;stop(undefined,true); }
});
window.addEventListener('keyup',event=>{
  if(steeringKey(event)){steeringKeysDown.delete(event.code);const wasActive=steeringKeysActive.delete(event.code);if(splitMode() && wasActive)updateKeyboardSteering();}
  if(travelKey(event)){travelKeysDown.delete(event.code);releaseTravel('key',event.code);}
  if(event.code==='KeyB'){brakesHeld.delete('key');updateControls();}
});
window.addEventListener('blur', () => stop('Driving window lost focus; session disabled.'));
document.addEventListener('visibilitychange', () => { if (document.hidden) stop('Page hidden. Rehearsal disabled.'); });
window.addEventListener('pagehide', () => stop('Page closed. Rehearsal disabled.'));
window.addEventListener('offline', disconnected);
if (window.FahadJoystick) stick = window.FahadJoystick.bind({
  pad:ui('joystick-pad'),knob:ui('joystick-knob'),readout:ui('joystick-readout'),
  mode:()=>ui('joystick-mode').value || 'circular',
  enabled:()=>connected && steeringMode && Boolean(generation) && !ui('joystick-pad').disabled,
  onStart:(id,event)=>{if (!generation || pointer!==null || keyboardSource || steeringKeysActive.size || (splitMode() && event.pointerType!=='touch')) return false;pointer='stick:'+id;if(splitMode())return true;if(sessionMode){motion++;sendPending=true;}desired='joystick';return true;},
  onMove:value=>{joystickInput=splitMode()?{throttle:travelPedal?joystickInput.throttle:0,steering:value.steering}:{throttle:value.throttle,steering:value.steering};updateControls();if(sessionMode&&sendPending)heartbeat();},
  onEnd:why=>{
    if(why==='pointerup' && splitMode()){pointer=null;joystickInput.steering=0;updateControls();}
    else if(why==='pointerup')releaseHold();
    else stop('Joystick '+why+'; session disabled. Release and enable deliberately.');
  }
});
setInterval(() => { heartbeat(); updateControls(); }, 100);
setInterval(() => { if (connected && performance.now()-lastStatusAt > 1600) disconnected(); }, 200);
if (window.location && typeof URLSearchParams !== 'undefined') {
  const initialView = new URLSearchParams(window.location.search).get('view');
  if (['rgb','yolo'].includes(initialView)) {source=initialView;ui('source').value=source;}
}
drawScan(null); updateControls(); poll(); frame();
pollMap();
