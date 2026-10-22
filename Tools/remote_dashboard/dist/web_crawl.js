/* Dedicated one-shot mode. Never used by the default read-only page. */
'use strict';
const el = id => document.getElementById(id);
const owner = Array.from(crypto.getRandomValues(new Uint8Array(16)), b => b.toString(16).padStart(2, '0')).join('');
let key = null, boot = null, token = null, sequence = 0, epoch = 0;
let online = false, busy = false, preparing = false, held = false, attempted = false, retired = false;
let current = null, statusAt = 0, imageAt = 0, imageUrl = null, source = 'rgb', frameBusy = false;
let pointer = null, keyboard = false;
const activePage = () => !document.hidden && document.hasFocus();
function update(note) {
  const fresh = online && performance.now() - statusAt < 600;
  el('prepare').disabled = !fresh || retired || preparing || Boolean(token) || !activePage() || !current || !current.ready || !imageAt || performance.now()-imageAt >= 1000;
  // Keep a held button enabled so native release/capture/key events still arrive.
  el('forward').disabled = !fresh || retired || !token || (attempted && !held) || !activePage();
  el('state').textContent = current ? current.state.toUpperCase() : 'DISCONNECTED';
  if (note) el('note').textContent = note;
}
async function req(path, body) {
  const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 450);
  try {
    const options = {cache:'no-store', credentials:'same-origin', signal:controller.signal};
    if (body !== undefined) Object.assign(options, {method:'POST', headers:{'Content-Type':'application/json','X-Dashboard-Key':key || ''},body:JSON.stringify(body)});
    const result = await fetch(path, options);
    if (!result.ok) throw new Error('Rejected or disconnected');
    return await result.json();
  } finally { clearTimeout(timer); }
}
function cancel(note = 'Stop requested. This permit will not resume.') {
  epoch++; token = null; held = false; pointer = null; keyboard = false; retired = true;
  update(note);
  if (key) req('/api/crawl/stop', {}).catch(() => {});
}
function loseConnection() {
  online = false; el('connection').textContent = 'Disconnected';
  if (token || preparing || held) cancel('Connection lost. No automatic resumption.');
  el('camera').hidden = true; el('camera-empty').hidden = false; imageAt = 0;
  update('Connection unavailable. Watch the physical robot; Stop is best effort.');
}
async function poll() {
  try {
    if (!key) { const data = await req('/api/bootstrap'); key = data.key; boot = data.boot_id; }
    const data = await req('/api/status');
    if (data.boot_id !== boot || data.mode !== 'web_crawl_one_shot' || !data.crawl) {
      retired = true; throw new Error('Wrong/restarted mode; reload deliberately');
    }
    online = true; statusAt = performance.now(); current = data.crawl;
    el('connection').textContent = 'One-shot backend connected';
    if (token && (current.owner !== owner || current.state === 'spent')) { token = null; held = false; retired = true; }
    if (current.state === 'spent') retired = true;
    const image = data.cameras[source];
    el('camera-note').textContent = image.available ? 'Message arrival age: '+image.age_s.toFixed(2)+' s (not exposure latency)' : 'No recent selected camera message';
    if (!image.available) { el('camera').hidden = true; el('camera-empty').hidden = false; imageAt = 0; if (token) cancel('Camera unavailable. Stop requested.'); }
    let note = current.readiness || current.reason;
    if (current.stop_feedback !== null) note += current.stop_feedback ? ' Recent near-zero odometry after zero requests; not independent stop proof.' : ' STOP NOT VERIFIED BY FEEDBACK. Check physically; power off if needed.';
    update(note);
  } catch (_) { loseConnection(); }
  setTimeout(poll, 200);
}
async function frame() {
  if (online && !frameBusy && !document.hidden) {
    frameBusy = true; const selected = source;
    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 700);
    try {
      const response = await fetch('/api/frame/'+selected, {cache:'no-store',signal:controller.signal});
      if (!response.ok) throw new Error('No recent image');
      const blob = await response.blob();
      if (selected === source && online) {
        const url = URL.createObjectURL(blob), old = imageUrl; imageUrl = url;
        el('camera').onload = () => { if (url === imageUrl && online) { imageAt = performance.now(); el('camera').hidden = false; el('camera-empty').hidden = true; update(); } if (old) URL.revokeObjectURL(old); };
        el('camera').onerror = () => { imageAt = 0; if (token) cancel('Image decode failed'); };
        el('camera').src = url;
      }
    } catch (_) {
      imageAt = 0; el('camera').hidden = true; el('camera-empty').hidden = false;
      if (token) cancel('No camera preview. Stop requested.');
    } finally { clearTimeout(timer); frameBusy = false; }
  }
  setTimeout(frame, 330);
}
el('prepare').addEventListener('click', async () => {
  update(); if (el('prepare').disabled) return;
  preparing = true; const version = epoch; update();
  try {
    const result = await req('/api/crawl/prepare', {owner});
    if (version !== epoch || !online || !activePage()) { cancel(); return; }
    token = result.token; sequence = 0;
    update('Prepared. Hold Forward now; release ends the trial.');
  } catch (_) { cancel('Prepare failed or expired. No automatic retry.'); }
  finally { preparing = false; update(); }
});
async function send(action) {
  if (!token || busy || !online || retired) return false;
  if (!activePage() || performance.now()-statusAt >= 600 || !imageAt || performance.now()-imageAt >= 1000) { cancel('Page/camera status stale. Stop requested.'); return false; }
  busy = true; const sentToken = token;
  try {
    await req('/api/crawl/command', {owner,token:sentToken,sequence:++sequence,action});
    return true;
  } catch (_) { if (token === sentToken) cancel('Command rejected/expired. No automatic retry.'); return false; }
  finally { busy = false; update(); }
}
function begin() {
  update(); if (el('forward').disabled || attempted) return false;
  if (busy) { update('Heartbeat in progress; release and hold Forward again.'); return false; }
  attempted = true; held = true;
  send('forward'); update('One forward action requested. Keep watching the robot.');
  return true;
}
el('forward').addEventListener('pointerdown', event => {
  if (event.pointerType === 'mouse' && event.button !== 0) return;
  event.preventDefault();
  if (begin()) { pointer = event.pointerId; el('forward').setPointerCapture(event.pointerId); }
});
['pointerup','pointercancel','lostpointercapture'].forEach(name => el('forward').addEventListener(name, event => {
  if (pointer === event.pointerId && held) cancel('Released. Stop requested; this attempt is spent.');
}));
el('forward').addEventListener('keydown', event => {
  if ((event.key === 'Enter' || event.key === ' ') && !event.repeat) { event.preventDefault(); if (begin()) keyboard = true; }
});
el('forward').addEventListener('keyup', event => {
  if (keyboard && (event.key === 'Enter' || event.key === ' ')) { event.preventDefault(); cancel('Key released. Stop requested.'); }
});
el('source').addEventListener('change', () => {
  if (token || preparing) cancel('View changed. Stop requested.');
  source = el('source').value; imageAt = 0; el('camera').hidden = true; el('camera-empty').hidden = false;
});
el('stop').addEventListener('click', () => cancel());
window.addEventListener('keydown', event => {
  if (event.key === 'Escape' || (event.code === 'Space' && event.target !== el('forward'))) { event.preventDefault(); cancel(); }
});
function pageLost() { if (token || preparing || held) cancel('Page inactive. Stop requested.'); }
window.addEventListener('blur', pageLost);
window.addEventListener('pagehide', pageLost);
window.addEventListener('offline', loseConnection);
document.addEventListener('visibilitychange', () => { if (document.hidden) pageLost(); });
setInterval(() => { if (token) send('heartbeat'); update(); }, 100);
setInterval(() => { if (online && performance.now()-statusAt >= 600) loseConnection(); }, 100);
update(); poll(); frame();
