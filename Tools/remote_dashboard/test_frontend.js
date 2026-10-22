/* Unit tests of browser logic using a fake DOM; no browser, network or robot. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {webcrypto} = require('node:crypto');
const source = fs.readFileSync(__dirname + '/dist/app.js','utf8');

function element(action) {
  const names = new Set();
  return {textContent:'', disabled:false, hidden:false, checked:false, dataset:{action}, listeners:{},
    classList:{toggle:(name,on) => on ? names.add(name) : names.delete(name), contains:name => names.has(name)},
    addEventListener(name,fn) { (this.listeners[name] ||= []).push(fn); },
    style:{setProperty(){}},setPointerCapture() {},hasPointerCapture(){return false;},
    getBoundingClientRect(){return {left:0,top:0,width:220,height:220};},
    getContext() { return new Proxy({}, {get:() => () => {}}); },
    width:640,height:360};
}
function fixture(options={}) {
  const nodes = {}, dirs = ['forward_left','forward','forward_right','reverse_left','reverse','reverse_right'].map(element);
  const node = id => nodes[id] ||= element();
  let focused = true, hidden = false, fail = false, armed = false, controllingOwner = null, gen = 0, delayedArm = null, now=100;
  const car = Boolean(options.ackermann || options.session);
  let drive = Boolean(options.drive || car), readyFlag = true;
  let stage='disabled',serverSequence=0,retired=0,delayCommand=null,rejection=null;
  const requests = [], events = {}, timers = [], intervals = [];
  const snapshot = () => ({mode:car?'ros_manual_ackermann':drive?'ros_manual_forward':'preview',motor_output:drive,boot_id:'test-boot',control:{armed,owner:controllingOwner,reason:'Stopped',ready:readyFlag&&!armed,stage:options.session?stage:armed?'armed':'disabled',readiness:readyFlag?null:'Waiting for feedback',allowed_actions:car?['forward','forward_left','forward_right','reverse','reverse_left','reverse_right','joystick']:['forward'],...(options.session?{session_persistent:true,joystick_speed_request_m_s:.30,sequence:serverSequence,retired_motion:retired,motion_ready:stage==='armed',max_hold_s:null}:{})},
    cameras:{rgb:{available:drive,age_s:drive?.1:null,topic:'/camera/rgb/image_raw'},yolo:{available:drive,age_s:drive?.1:null,topic:'/darknet_ros/detection_image'}},
    scan:{available:false,age_s:null},ros_error:null});
  const context = vm.createContext({console,crypto:webcrypto,Uint8Array,AbortController,
    URLSearchParams,URL:{createObjectURL:() => 'blob:unit-test',revokeObjectURL(){}},performance:{now:() => now},
    document:{getElementById:node,querySelectorAll:() => dirs,hasFocus:() => focused,get hidden(){return hidden;},
      addEventListener:(name,fn) => { events[name] = fn; }},
    window:{location:{search:options.search||''},FahadSensorView:require('./dist/sensor_view.js'),FahadJoystick:car?require('./dist/joystick.js'):undefined,addEventListener:(name,fn) => { events[name] = fn; }},
    setTimeout:(fn,delay) => {timers.push({fn,delay}); return timers.length;},clearTimeout(){},
    setInterval:(fn,delay) => {intervals.push({fn,delay});},
    fetch:async (path,requestOptions={}) => {
      requests.push({path,options:requestOptions});
      if (fail) throw typeof fail==='object'?fail:new Error('Offline');
      if(path.endsWith('/command') && rejection)return {ok:false,status:rejection.status,json:async()=>rejection.payload};
      let payload,okay=true;
      if (path === '/api/bootstrap') payload = {key:'test-key',boot_id:'test-boot'};
      else if (path === '/api/status') payload = snapshot();
      else if (path.endsWith('/arm')) {
        if (delayedArm) await delayedArm;
        armed = true; stage='armed';serverSequence=0;retired=0;controllingOwner = JSON.parse(requestOptions.body).owner; payload = {generation:'generation-'+(++gen)};
      } else if (path.endsWith('/stop')) {armed=false;stage='disabled';controllingOwner=null;payload={};}
      else if (path.endsWith('/command') && options.session) {
        const body=JSON.parse(requestOptions.body);
        if(delayCommand&&body.action!=='neutral')await delayCommand;
        if(!armed||body.sequence<=serverSequence)okay=false;
        else {
          serverSequence=body.sequence;
          if(body.action==='neutral') {retired=Math.max(retired,body.motion);if(stage==='holding')stage='braking';}
          else if(body.motion<=retired)okay=false;
          else if(stage==='braking')retired=Math.max(retired,body.motion);
          else if(body.action!=='joystick' || Math.abs(body.throttle)>.12 || stage==='holding')stage='holding';
        }
        payload=snapshot().control;
      }
      else payload = {};
      return {ok:okay,json:async () => payload};
    }});
  vm.runInContext(source,context,{filename:'app.js'});
  return {context,node,dirs,events,requests,timers,intervals,
    get:expression => vm.runInContext(expression,context),
    focus:value => {focused=value;}, hide:value => {hidden=value;}, fail:value => {fail=value;},
    delayArm:promise => {delayedArm=promise;}, block:value => {readyFlag=!value;},
    delayCommand:promise=>{delayCommand=promise;},finishBrake:()=>{stage='armed';},serverStage:()=>stage,advance:ms=>{now+=ms;},reject:value=>{rejection=value;}};
}
const flush = () => new Promise(resolve => setImmediate(resolve));
async function ready(options) {const test=fixture(options);await flush();return test;}
async function enable(test) {await test.node('arm').listeners.click[0]();await flush();}

async function main() {
  let count=0;
  async function check(name,fn) {await fn();console.log('PASS '+name);count++;}
  await check('served HTML defaults to separate held travel and steering layout',async()=>{
    const html=fs.readFileSync(__dirname+'/dist/index.html','utf8');assert.match(html,/<option value="steering" selected>/);
  });
  await check('hub YOLO link selects view without enabling driving',async()=>{
    const t=await ready({search:'?view=yolo'});assert.equal(t.get('source'),'yolo');assert.equal(t.get('generation'),null);
    assert(!t.requests.some(x=>x.path.endsWith('/arm')));
  });
  await check('unknown hub view is ignored',async()=>{
    const t=await ready({search:'?view=untrusted'});assert.equal(t.get('source'),'rgb');
  });
  await check('starts disabled and clearly indicates preview',async () => {
    const t=await ready();assert.equal(t.get('generation'),null);assert.equal(t.node('intent').textContent,'DISABLED');
    assert.match(t.node('mode').textContent,/preview/);assert(t.dirs.every(x=>x.disabled));
  });
  await check('explicit enable remains motor-free and heartbeat is neutral',async () => {
    const t=await ready();await enable(t);assert(t.get('generation'));await t.get('heartbeat()');
    const sent=t.requests.filter(x=>x.path.endsWith('/command')).pop();assert.equal(JSON.parse(sent.options.body).action,'neutral');
    assert(t.requests.every(x=>!x.path.includes('cmd_vel')));
  });
  await check('pointer hold requests an arc; release disables',async () => {
    const t=await ready();await enable(t);
    t.dirs[0].listeners.pointerdown[0]({pointerId:1,pointerType:'mouse',button:0,preventDefault(){}});
    assert.equal(t.get('desired'),'forward_left');await t.get('heartbeat()');
    t.dirs[0].listeners.pointerup[0]({pointerId:1});assert.equal(t.get('generation'),null);
  });
  await check('pointer cancellation disables',async () => {
    const t=await ready();await enable(t);
    t.dirs[1].listeners.pointerdown[0]({pointerId:1,pointerType:'touch',preventDefault(){}});
    t.dirs[1].listeners.pointercancel[0]({pointerId:1});assert.equal(t.get('generation'),null);
  });
  await check('second touch cannot override the held direction',async () => {
    const t=await ready();await enable(t);
    for (const [index,id] of [[0,1],[2,2]]) t.dirs[index].listeners.pointerdown[0]({pointerId:id,pointerType:'touch',preventDefault(){}});
    assert.equal(t.get('desired'),'forward_left');
  });
  await check('window blur and page hiding disable',async () => {
    const t=await ready();await enable(t);t.events.blur();assert.equal(t.get('generation'),null);
    await enable(t);t.hide(true);t.events.visibilitychange();assert.equal(t.get('generation'),null);
  });
  await check('hidden or unfocused page cannot enable',async () => {
    const t=await ready();t.focus(false);await enable(t);assert.equal(t.get('generation'),null);
    t.focus(true);t.hide(true);await enable(t);assert.equal(t.get('generation'),null);
  });
  await check('offline disables, then reconnect does not enable',async () => {
    const t=await ready();await enable(t);t.events.offline();assert.equal(t.get('generation'),null);
    await t.get('poll()');assert.equal(t.get('generation'),null);assert.equal(t.get('connected'),true);
  });
  await check('failed heartbeat disables without queued command replay',async () => {
    const t=await ready();await enable(t);t.fail(true);await t.get('heartbeat()');assert.equal(t.get('generation'),null);
    t.fail(false);await t.get('heartbeat()');assert.equal(t.get('generation'),null);
  });
  await check('stop beats an in-flight enable response',async () => {
    const t=await ready();let release;t.delayArm(new Promise(resolve=>{release=resolve;}));
    const pending=t.node('arm').listeners.click[0]();t.events.blur();release();await pending;await flush();
    assert.equal(t.get('generation'),null);
  });
  await check('Space stops outside a direction control',async () => {
    const t=await ready();await enable(t);
    t.events.keydown({key:' ',code:'Space',target:t.node('stop'),preventDefault(){}});
    assert.equal(t.get('generation'),null);
  });
  await check('switching the camera source clears the old image',async () => {
    const t=await ready();t.node('source').value='yolo';t.node('source').listeners.change[0]();
    assert.equal(t.get('source'),'yolo');assert.equal(t.node('camera').hidden,true);
  });
  async function live() {
    const t=await ready({drive:true});
    t.get('imageReady=true;imageDecodedAt=100;ui("drive-ack").checked=true;updateControls()');
    return t;
  }
  await check('live mode requires physical acknowledgement and decoded image',async () => {
    const t=await ready({drive:true});assert(t.node('arm').disabled);
    t.get('imageReady=true;imageDecodedAt=100;updateControls()');assert(t.node('arm').disabled);
    t.node('drive-ack').checked=true;t.node('drive-ack').listeners.change[0]();assert(!t.node('arm').disabled);
    assert.match(t.node('safety-title').textContent,/Live motor/);
  });
  await check('live uses drive endpoints and only forward is available',async () => {
    const t=await live();await enable(t);
    assert(t.requests.some(x=>x.path==='/api/drive/arm'));
    assert(!t.dirs[1].disabled);assert(t.dirs.filter((x,i)=>i!==1).every(x=>x.disabled));
    t.dirs[0].listeners.pointerdown[0]({pointerId:1,pointerType:'mouse',button:0,preventDefault(){}});
    assert.equal(t.get('desired'),'neutral');
  });
  await check('live forward hold/release stops without terminal restart',async () => {
    const t=await live();await enable(t);
    t.dirs[1].listeners.pointerdown[0]({pointerId:1,pointerType:'mouse',button:0,preventDefault(){}});
    await t.get('heartbeat()');
    const command=t.requests.filter(x=>x.path==='/api/drive/command').pop();assert.equal(JSON.parse(command.options.body).action,'forward');
    t.dirs[1].listeners.pointerup[0]({pointerId:1});await flush();await t.get('poll()');
    assert.equal(t.get('generation'),null);assert(t.requests.some(x=>x.path==='/api/drive/stop'));
    await enable(t);assert(t.get('generation'));assert.equal(t.get('desired'),'neutral');
  });
  await check('backend readiness blocks reenable while stopping',async () => {
    const t=await live();t.block(true);await t.get('poll()');assert(t.node('arm').disabled);
    await enable(t);assert.equal(t.get('generation'),null);
  });
  await check('live missing image or stale status stops before heartbeat',async () => {
    for(const code of ['imageReady=false','imageDecodedAt=-2000','lastStatusAt=-2000']){
      const t=await live();await enable(t);t.get(code);await t.get('heartbeat()');assert.equal(t.get('generation'),null);
      assert(!t.requests.some(x=>x.path==='/api/drive/command'));
    }
  });
  await check('live removing physical acknowledgement stops',async () => {
    const t=await live();await enable(t);t.node('drive-ack').checked=false;t.node('drive-ack').listeners.change[0]();
    assert.equal(t.get('generation'),null);assert(t.node('arm').disabled);
  });
  await check('live view change and image loss request stop',async () => {
    const t=await live();await enable(t);t.node('source').value='yolo';t.node('source').listeners.change[0]();assert.equal(t.get('generation'),null);
    assert(t.requests.some(x=>x.path==='/api/drive/stop'));
  });
  await check('live reconnect never restores a held command',async () => {
    const t=await live();await enable(t);t.events.offline();await flush();await t.get('poll()');
    assert.equal(t.get('generation'),null);assert.equal(t.get('desired'),'neutral');
  });
  await check('live blur and page hiding stop',async () => {
    for(const action of ['blur','visibilitychange']){
      const t=await live();await enable(t);if(action==='visibilitychange')t.hide(true);t.events[action]();assert.equal(t.get('generation'),null);
    }
  });
  async function car(){const t=await ready({ackermann:true});t.get('imageReady=true;imageDecodedAt=100;ui("drive-ack").checked=true;updateControls()');await enable(t);return t;}
  const event=(x,y,id=1)=>({clientX:x,clientY:y,pointerId:id,pointerType:'touch',preventDefault(){}});
  await check('car mode enables six buttons and exposes joystick',async()=>{
    const t=await car();assert(t.dirs.every(x=>!x.disabled));assert(!t.node('joystick-panel').hidden);assert(!t.node('joystick-pad').disabled);
    assert.match(t.node('control-title').textContent,/WASD/);
  });
  await check('car buttons publish reverse arcs through guarded command endpoint',async()=>{
    const t=await car();t.dirs[3].listeners.pointerdown[0]({pointerId:1,pointerType:'mouse',button:0,preventDefault(){}});
    await t.get('heartbeat()');const command=t.requests.filter(x=>x.path==='/api/drive/command').pop();assert.equal(JSON.parse(command.options.body).action,'reverse_left');
    t.dirs[3].listeners.pointerup[0]({pointerId:1});assert.equal(t.get('generation'),null);
  });
  await check('joystick drag sends bounded throttle and steering then centres on release',async()=>{
    const t=await car(),pad=t.node('joystick-pad');pad.listeners.pointerdown[0](event(110,40));await t.get('heartbeat()');
    let command=JSON.parse(t.requests.filter(x=>x.path==='/api/drive/command').pop().options.body);
    assert.equal(command.action,'joystick');assert(command.throttle>0);assert.equal(command.steering,0);
    pad.listeners.pointermove[0](event(60,55));await t.get('heartbeat()');
    command=JSON.parse(t.requests.filter(x=>x.path==='/api/drive/command').pop().options.body);assert(command.steering<0);assert(Math.abs(command.throttle)<=1);
    pad.listeners.pointerup[0](event(60,55));assert.equal(t.get('generation'),null);assert.equal(t.get('joystickInput.throttle'),0);assert.equal(t.get('stick.value().steering'),0);
  });
  await check('second touch and arrow cannot override held joystick',async()=>{
    const t=await car(),pad=t.node('joystick-pad');pad.listeners.pointerdown[0](event(110,40));
    pad.listeners.pointerdown[0](event(110,180,2));assert(t.get('joystickInput.throttle')>0);
    t.dirs[4].listeners.pointerdown[0]({pointerId:2,pointerType:'touch',preventDefault(){}});assert.equal(t.get('desired'),'joystick');
  });
  await check('joystick cancel or lost capture stops and returns to centre',async()=>{
    for(const name of ['pointercancel','lostpointercapture']){const t=await car(),pad=t.node('joystick-pad');pad.listeners.pointerdown[0](event(110,40));pad.listeners[name][0](event(110,40));assert.equal(t.get('generation'),null);assert.equal(t.get('stick.value().throttle'),0);}
  });
  await check('blur and camera switch centre the joystick with no automatic resume',async()=>{
    const t=await car();t.node('joystick-pad').listeners.pointerdown[0](event(110,40));t.events.blur();assert.equal(t.get('generation'),null);assert.equal(t.get('stick.value().throttle'),0);
    await t.get('poll()');assert.equal(t.get('desired'),'neutral');
  });
  async function session(){const t=await ready({session:true});t.get('imageReady=true;imageDecodedAt=100;ui("drive-ack").checked=true;updateControls()');await enable(t);return t;}
  const press=(t,index=1,id=1)=>t.dirs[index].listeners.pointerdown[0]({pointerId:id,pointerType:'mouse',button:0,preventDefault(){}});
  const release=(t,index=1,id=1)=>t.dirs[index].listeners.pointerup[0]({pointerId:id});
  await check('session enables once then hides Enable during normal operation',async()=>{
    const t=await session();assert(t.node('arm').hidden);assert(t.dirs.every(x=>!x.disabled));
    assert.match(t.node('control-help').textContent,/Enable once/);assert(!t.node('safety-note').textContent.includes('two-second'));
  });
  await check('session first press sends intent immediately rather than waiting for heartbeat',async()=>{
    const t=await session();press(t);await flush();
    const body=JSON.parse(t.requests.find(x=>x.path.endsWith('/command')).options.body);
    assert.equal(body.action,'forward');assert.equal(body.motion,1);
  });
  await check('normal release keeps session but sends higher-sequence neutral and blocks until ready',async()=>{
    const t=await session(),token=t.get('generation');press(t);await flush();release(t);await flush();
    assert.equal(t.get('generation'),token);assert.equal(t.get('desired'),'neutral');assert(t.node('arm').hidden);assert(t.dirs.every(x=>x.disabled));
    const bodies=t.requests.filter(x=>x.path.endsWith('/command')).map(x=>JSON.parse(x.options.body));
    assert.equal(bodies.at(-1).action,'neutral');assert(bodies.at(-1).sequence>bodies[0].sequence);
    assert(!t.requests.some(x=>x.path.endsWith('/stop')));
  });
  await check('fresh press after feedback uses a new motion ID without another Enable',async()=>{
    const t=await session();press(t);await flush();release(t);await flush();t.finishBrake();await t.get('heartbeat()');
    assert(t.dirs.every(x=>!x.disabled));press(t,4,2);await flush();
    const body=JSON.parse(t.requests.filter(x=>x.path.endsWith('/command')).at(-1).options.body);
    assert.equal(body.action,'reverse');assert.equal(body.motion,2);assert.equal(t.requests.filter(x=>x.path.endsWith('/arm')).length,1);
  });
  await check('a press made while braking is not queued or resumed',async()=>{
    const t=await session();press(t);await flush();release(t);await flush();press(t,4,2);
    assert.equal(t.get('desired'),'neutral');t.finishBrake();await t.get('heartbeat()');assert.equal(t.get('desired'),'neutral');
  });
  await check('delayed held command cannot override release or unnecessarily disable session',async()=>{
    const t=await session();let finish;t.delayCommand(new Promise(resolve=>{finish=resolve;}));press(t);release(t);await flush();
    const token=t.get('generation');finish();await flush();await flush();
    assert.equal(t.get('generation'),token);assert.equal(t.get('desired'),'neutral');assert.equal(t.serverStage(),'armed');
    assert(!t.requests.some(x=>x.path.endsWith('/stop')));
  });
  await check('session Stop still disables and clears pending input',async()=>{
    const t=await session();press(t);await flush();t.node('stop').listeners.click[0]();await flush();
    assert.equal(t.get('generation'),null);assert(!t.node('arm').hidden);assert.equal(t.get('desired'),'neutral');
  });
  await check('session blur hidden offline and capture cancellation require Enable again',async()=>{
    for(const kind of ['blur','hidden','offline','pointercancel','lostpointercapture']){
      const t=await session();press(t);await flush();
      if(kind==='hidden'){t.hide(true);t.events.visibilitychange();}
      else if(kind==='pointercancel'||kind==='lostpointercapture')t.dirs[1].listeners[kind][0]({pointerId:1});
      else t.events[kind]();
      await flush();assert.equal(t.get('generation'),null);assert.equal(t.get('desired'),'neutral');
    }
  });
  await check('session joystick release centres while keeping session enabled',async()=>{
    const t=await session(),pad=t.node('joystick-pad');pad.listeners.pointerdown[0](event(110,40));await flush();pad.listeners.pointerup[0](event(110,40));await flush();
    assert(t.get('generation'));assert.equal(t.get('stick.value().throttle'),0);assert.equal(t.get('desired'),'neutral');assert.equal(t.serverStage(),'braking');
  });
  await check('session joystick capture loss disables rather than retaining a session',async()=>{
    const t=await session(),pad=t.node('joystick-pad');pad.listeners.pointerdown[0](event(110,40));await flush();pad.listeners.lostpointercapture[0](event(110,40));assert.equal(t.get('generation'),null);
  });
  await check('session joystick updates do not create an unbounded request queue',async()=>{
    const t=await session(),pad=t.node('joystick-pad');pad.listeners.pointerdown[0](event(110,40));await flush();
    const before=t.requests.filter(x=>x.path.endsWith('/command')).length;
    for(let i=0;i<100;i++)pad.listeners.pointermove[0](event(100,45));await flush();
    assert.equal(t.requests.filter(x=>x.path.endsWith('/command')).length,before);await t.get('heartbeat()');
    assert.equal(t.requests.filter(x=>x.path.endsWith('/command')).length,before+1);
  });
  await check('session keyboard release keeps session; Escape still disables',async()=>{
    const t=await session();t.dirs[1].listeners.keydown[0]({key:'Enter',repeat:false,preventDefault(){}});await flush();
    t.dirs[1].listeners.keyup[0]({key:'Enter',preventDefault(){}});await flush();assert(t.get('generation'));
    t.events.keydown({key:'Escape',target:t.node('stop'),preventDefault(){}});assert.equal(t.get('generation'),null);
  });
  await check('session stale camera or failed heartbeat disables without replay',async()=>{
    for(const failure of ['camera','network']){const t=await session();press(t);await flush();if(failure==='camera')t.get('imageReady=false');else t.fail(true);await t.get('heartbeat()');assert.equal(t.get('generation'),null);}
  });
  await check('backend fault with retired sequence disables the session immediately',async()=>{
    const t=await session();press(t);await flush();t.get('applySessionStatus({sequence:0,armed:false,owner:null,reason:"Sensor fault"})');
    assert.equal(t.get('generation'),null);assert.equal(t.get('desired'),'neutral');
  });
  await check('browser stop reason survives generic polling and repeated stop',async()=>{
    const t=await session();press(t);await flush();t.events.blur();
    assert.match(t.node('last-client-stop').textContent,/lost focus/);
    t.get('stop("Stopped by operator");renderDiagnostics()');
    assert.match(t.node('last-client-stop').textContent,/lost focus/);
    const report=t.get('diagnosticReport()');assert(!('key' in report));assert(!('owner' in report));assert(!('generation' in report));
  });
  await check('capture loss is explicit and never automatically resumes',async()=>{
    const t=await session();t.node('joystick-pad').listeners.pointerdown[0]({pointerId:7,pointerType:'mouse',button:0,clientX:110,clientY:20,preventDefault(){}});await flush();
    t.node('joystick-pad').listeners.lostpointercapture[0]({pointerId:7});
    assert.equal(t.get('generation'),null);assert.match(t.node('last-client-stop').textContent,/lostpointercapture/);
  });
  await check('independent joystick sends full corner inputs; changing layout stops',async()=>{
    const t=await session();t.node('joystick-mode').value='independent';
    t.node('joystick-pad').listeners.pointerdown[0]({pointerId:7,pointerType:'mouse',button:0,clientX:220,clientY:0,preventDefault(){}});await flush();
    assert.equal(t.get('joystickInput.throttle'),1);assert.equal(t.get('joystickInput.steering'),1);
    t.node('joystick-mode').listeners.change[0]();assert.equal(t.get('generation'),null);
  });
  const keyEvent=(t,code,extra={})=>({code,key:code==='KeyW'?'w':code==='KeyS'?'s':code,target:t.node('joystick-pad'),repeat:false,preventDefault(){},...extra});
  const split=async()=>{const t=await session();t.node('joystick-mode').value='steering';t.get('updateControls()');return t;};
  const rampTick=async(t,ms=100)=>{t.advance(ms);t.get('imageDecodedAt=performance.now();lastStatusAt=performance.now()');await t.get('heartbeat()');await flush();};
  const freshSplit=async()=>{const t=await ready({session:true});t.get('ui("joystick-mode").value="steering";imageReady=true;imageDecodedAt=performance.now();ui("drive-ack").checked=true;updateControls()');return t;};
  const steer=(t,id=77,x=220)=>t.node('joystick-pad').listeners.pointerdown[0]({pointerId:id,pointerType:'touch',clientX:x,clientY:0,preventDefault(){}});
  await check('pedal mode key and steering have independent simultaneous input',async()=>{
    const t=await split();steer(t);t.events.keydown(keyEvent(t,'KeyW'));await flush();
    await rampTick(t);
    assert.equal(t.get('desired'),'joystick');assert.equal(t.get('joystickInput.steering'),1);
    const before=t.get('joystickInput.throttle');assert(before>0);
    const command=JSON.parse(t.requests.filter(x=>x.path.endsWith('/command')).pop().options.body);
    assert.equal(command.action,'joystick');assert.equal(command.throttle,before);assert.equal(command.steering,1);
    t.node('joystick-pad').listeners.pointermove[0]({pointerId:77,clientX:0,clientY:220,preventDefault(){}});
    assert.equal(t.get('joystickInput.throttle'),before);assert.equal(t.get('joystickInput.steering'),-1);
    assert.equal(t.node('pedal-controls').hidden,false);assert.equal(t.node('direction-controls').hidden,true);
  });
  await check('releasing travel brakes but keeps steering grip and healthy session',async()=>{
    const t=await split();steer(t);t.events.keydown(keyEvent(t,'KeyW'));await flush();
    await rampTick(t);
    t.events.keyup(keyEvent(t,'KeyW'));await flush();
    assert(t.get('generation'));assert.equal(t.get('desired'),'neutral');assert.equal(t.get('joystickInput.throttle'),0);
    assert.equal(t.get('pointer'),'stick:77');assert.equal(t.get('joystickInput.steering'),1);
    assert.equal(t.node('joystick-pad').disabled,false);assert.equal(t.node('pedal-forward').disabled,true);
    t.finishBrake();await t.get('poll()');t.events.keydown(keyEvent(t,'KeyS'));await flush();await rampTick(t);
    assert(t.get('joystickInput.throttle')<0);assert.equal(t.get('motion'),2);
  });
  await check('releasing steering centres it without releasing a held travel key',async()=>{
    const t=await split();t.events.keydown(keyEvent(t,'KeyW'));await flush();steer(t);await flush();
    const before=t.get('joystickInput.throttle');t.node('joystick-pad').listeners.pointerup[0]({pointerId:77});await flush();
    assert(t.get('generation'));assert.equal(t.get('joystickInput.throttle'),before);assert.equal(t.get('joystickInput.steering'),0);
    assert.equal(t.get('desired'),'joystick');assert.equal(t.get('travelPedal.id'),'KeyW');
  });
  await check('brake does not replay a still-held key after stationary feedback',async()=>{
    const t=await split();t.events.keydown(keyEvent(t,'KeyW'));await flush();t.events.keydown(keyEvent(t,'KeyB'));await flush();
    t.finishBrake();await t.get('poll()');t.events.keydown(keyEvent(t,'KeyW',{repeat:true}));await flush();
    assert.equal(t.get('desired'),'neutral');assert.equal(t.get('travelPedal'),null);assert(t.get('generation'));
    t.events.keyup(keyEvent(t,'KeyW'));t.events.keyup(keyEvent(t,'KeyB'));t.events.keydown(keyEvent(t,'KeyW'));await flush();assert.equal(t.get('desired'),'joystick');
  });
  await check('held brake prevents new travel and release cannot replay blocked key',async()=>{
    const t=await split();t.events.keydown(keyEvent(t,'KeyB'));await flush();t.events.keydown(keyEvent(t,'KeyW'));await flush();
    assert.equal(t.get('desired'),'neutral');t.events.keyup(keyEvent(t,'KeyB'));await flush();assert.equal(t.get('desired'),'neutral');
    t.events.keydown(keyEvent(t,'KeyW',{repeat:true}));assert.equal(t.get('desired'),'neutral');
    t.events.keyup(keyEvent(t,'KeyW'));t.events.keydown(keyEvent(t,'KeyW'));await flush();assert.equal(t.get('desired'),'joystick');
  });
  await check('touch brake has priority and cancelled brake disables the session',async()=>{
    const t=await split();t.node('pedal-brake').listeners.pointerdown[0]({pointerId:33,pointerType:'touch',preventDefault(){}});await flush();
    t.events.keydown(keyEvent(t,'KeyW'));assert.equal(t.get('travelPedal'),null);
    t.node('pedal-brake').listeners.pointercancel[0]({pointerId:33});assert.equal(t.get('generation'),null);
  });
  await check('opposite travel key decelerates to zero with no automatic reversal',async()=>{
    const t=await split();t.events.keydown(keyEvent(t,'KeyW'));await flush();for(let i=0;i<5;i++)await rampTick(t);
    const before=t.get('travelPedal.speed');t.events.keydown(keyEvent(t,'KeyS'));await flush();await rampTick(t);
    assert(t.get('travelPedal.speed')<before);assert(t.get('joystickInput.throttle')>0);
    t.events.keyup(keyEvent(t,'KeyW'));await rampTick(t);await rampTick(t);
    assert.equal(t.get('desired'),'neutral');assert.equal(t.get('travelPedal'),null);
    t.finishBrake();await t.get('poll()');t.events.keydown(keyEvent(t,'KeyS',{repeat:true}));assert.equal(t.get('desired'),'neutral');
    t.events.keyup(keyEvent(t,'KeyS'));t.events.keydown(keyEvent(t,'KeyS'));await flush();await rampTick(t);
    assert(t.get('joystickInput.throttle')<0);
  });
  await check('touch pedal plus second-finger steering releases travel independently',async()=>{
    const t=await split();t.node('pedal-forward').listeners.pointerdown[0]({pointerId:11,pointerType:'touch',preventDefault(){}});await flush();steer(t,22);await flush();
    assert.equal(t.get('travelPedal.id'),11);assert.equal(t.get('pointer'),'stick:22');assert.equal(t.get('joystickInput.steering'),1);
    t.node('pedal-forward').listeners.pointerup[0]({pointerId:11});await flush();
    assert.equal(t.get('desired'),'neutral');assert.equal(t.get('pointer'),'stick:22');assert(t.get('generation'));
  });
  await check('captured pedal cancellation disables all input',async()=>{
    for(const name of ['pointercancel','lostpointercapture']) {
      const t=await split();t.node('pedal-forward').listeners.pointerdown[0]({pointerId:11,pointerType:'touch',preventDefault(){}});await flush();
      t.node('pedal-forward').listeners[name][0]({pointerId:11});assert.equal(t.get('generation'),null);assert.equal(t.get('travelPedal'),null);
    }
  });
  await check('split keyboard cannot resume after focus loss, Stop or unticking',async()=>{
    for(const action of ['blur','stop','ack']) {
      const t=await split();t.events.keydown(keyEvent(t,'KeyW'));await flush();
      if(action==='blur')t.events.blur();else if(action==='stop')t.node('stop').listeners.click[0]();else {t.node('drive-ack').checked=false;t.node('drive-ack').listeners.change[0]();}
      assert.equal(t.get('generation'),null);assert.equal(t.get('travelPedal'),null);
      t.node('drive-ack').checked=true;await t.get('poll()');await enable(t);t.events.keydown(keyEvent(t,'KeyW',{repeat:true}));await flush();
      assert.equal(t.get('desired'),'neutral');
    }
  });
  await check('keyboard travel ignores editing, shortcuts, repeats and pre-enable holds',async()=>{
    for(const extra of [{ctrlKey:true},{altKey:true},{metaKey:true},{target:{tagName:'INPUT'}},{target:{tagName:'TEXTAREA'}},{target:{isContentEditable:true}},{repeat:true}]) {
      const t=await split();t.events.keydown(keyEvent(t,'KeyW',extra));await flush();assert.equal(t.get('travelPedal'),null);
    }
    const t=await ready({session:true});t.node('joystick-mode').value='steering';t.events.keydown(keyEvent(t,'KeyW'));await enable(t);
    t.events.keydown(keyEvent(t,'KeyW',{repeat:true}));await flush();assert.equal(t.get('desired'),'neutral');
  });
  await check('pedal accelerates gradually without slider and stays bounded',async()=>{
    const t=await split();t.events.keydown(keyEvent(t,'KeyW'));await flush();assert.equal(t.get('travelPedal.speed'),0);
    await rampTick(t);assert(Math.abs(t.get('travelPedal.speed')-.0003552)<1e-10);
    for(let i=0;i<55;i++)await rampTick(t);
    assert.equal(t.get('joystickInput.throttle'),1);assert.equal(t.get('travelPedal.speed'),.3);
    assert.match(t.node('pedal-speed-value').textContent,/0.300/);
    t.events.keyup(keyEvent(t,'KeyW'));await flush();assert.equal(t.get('joystickInput.throttle'),0);
    assert(!fs.readFileSync(__dirname+'/dist/index.html','utf8').includes('id="pedal-speed"'));
  });
  await check('mismatched backend speed cannot receive scaled pedal travel',async()=>{
    const t=await split();t.events.keydown(keyEvent(t,'KeyW'));await flush();
    t.get('lastStatus.control.joystick_speed_request_m_s=.10');await rampTick(t);
    assert.equal(t.get('generation'),null);assert.match(t.node('drive-alert').textContent,/configuration mismatch/);
  });
  await check('HUD preserves unique IDs and keeps telemetry left of framed vision',async()=>{
    const html=fs.readFileSync(__dirname+'/dist/index.html','utf8');const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
    assert.equal(ids.length,new Set(ids).size);
    for(const id of [...source.matchAll(/\bui\('([^']+)'\)/g)].map(m=>m[1]))assert(ids.includes(id),'Missing UI node '+id);
    const css=fs.readFileSync(__dirname+'/dist/controls.css','utf8');assert(css.includes("'readings camera controls' 'readings lidar controls'"));
    assert.match(css,/object-fit:contain/);assert.match(css,/@media\(max-width:1099px\)/);
  });
  await check('disable reason stays beside Enable until deliberate reenable',async()=>{
    const t=await split();t.events.keydown(keyEvent(t,'KeyW'));await flush();t.events.blur();
    assert.equal(t.node('drive-alert').hidden,false);assert.match(t.node('drive-alert').textContent,/lost focus/);
    await t.get('poll()');assert.match(t.node('drive-alert').textContent,/lost focus/);await enable(t);assert.equal(t.node('drive-alert').hidden,true);
  });
  await check('fresh healthy travel key explicitly enables without a separate click',async()=>{
    const t=await freshSplit();t.events.keydown(keyEvent(t,'KeyW'));await flush();
    assert(t.get('generation'));assert.equal(t.get('travelPedal.id'),'KeyW');assert.equal(t.get('travelPedal.speed'),0);
    await rampTick(t);assert(t.get('joystickInput.throttle')>0);
    assert.equal(t.requests.filter(x=>x.path.endsWith('/arm')).length,1);
  });
  await check('fresh touch pedal can enable and releasing during arm queues no travel',async()=>{
    const t=await freshSplit();let finish;const delayed=new Promise(resolve=>finish=resolve);t.delayArm(delayed);
    t.node('pedal-forward').listeners.pointerdown[0]({pointerId:11,pointerType:'touch',preventDefault(){}});
    assert(t.get('pendingTravel'));assert.equal(t.node('pedal-forward').disabled,false);
    t.node('pedal-forward').listeners.pointerup[0]({pointerId:11});finish();await flush();
    assert.equal(t.get('generation'),null);assert.equal(t.get('pendingTravel'),null);
    assert(!t.requests.some(x=>x.path.endsWith('/command')));
  });
  await check('keyup during delayed key enable cannot produce late motion',async()=>{
    const t=await freshSplit();let finish;t.delayArm(new Promise(resolve=>finish=resolve));
    t.events.keydown(keyEvent(t,'KeyW'));t.events.keyup(keyEvent(t,'KeyW'));finish();await flush();
    assert.equal(t.get('generation'),null);assert(!t.requests.some(x=>x.path.endsWith('/command')));
  });
  await check('pending capture cancel or Brake cannot later enable motion',async()=>{
    for(const action of ['cancel','brake','stop']) {
      const t=await freshSplit();let finish;t.delayArm(new Promise(resolve=>finish=resolve));
      t.node('pedal-forward').listeners.pointerdown[0]({pointerId:11,pointerType:'touch',preventDefault(){}});
      if(action==='cancel')t.node('pedal-forward').listeners.pointercancel[0]({pointerId:11});
      else if(action==='brake')t.events.keydown(keyEvent(t,'KeyB'));else t.node('stop').listeners.click[0]();
      finish();await flush();assert.equal(t.get('generation'),null);assert.equal(t.get('pendingTravel'),null);
      assert(!t.requests.some(x=>x.path.endsWith('/command')));
    }
  });
  await check('input pressed while unready cannot queue enable when readiness returns',async()=>{
    const t=await freshSplit();t.block(true);await t.get('poll()');t.events.keydown(keyEvent(t,'KeyW'));await flush();
    assert.equal(t.get('generation'),null);t.block(false);await t.get('poll()');t.events.keydown(keyEvent(t,'KeyW',{repeat:true}));await flush();
    assert.equal(t.get('generation'),null);t.events.keyup(keyEvent(t,'KeyW'));t.events.keydown(keyEvent(t,'KeyW'));await flush();assert(t.get('generation'));
  });
  await check('recovered fault requires fresh key, not a held-key automatic resume',async()=>{
    const t=await freshSplit();t.events.keydown(keyEvent(t,'KeyW'));await flush();await rampTick(t);t.events.blur();await flush();await t.get('poll()');
    t.events.keydown(keyEvent(t,'KeyW',{repeat:true}));assert.equal(t.get('generation'),null);
    t.events.keyup(keyEvent(t,'KeyW'));t.events.keydown(keyEvent(t,'KeyW'));await flush();assert(t.get('generation'));assert.equal(t.get('travelPedal.speed'),0);
  });
  await check('explicit Stop locks fresh-key enable until deliberate acknowledgement',async()=>{
    const t=await freshSplit();t.events.keydown(keyEvent(t,'KeyW'));await flush();t.node('stop').listeners.click[0]();await flush();
    t.events.keyup(keyEvent(t,'KeyW'));await t.get('poll()');t.events.keydown(keyEvent(t,'KeyW'));await flush();assert.equal(t.get('generation'),null);
    t.node('drive-ack').checked=false;t.node('drive-ack').listeners.change[0]();t.node('drive-ack').checked=true;t.node('drive-ack').listeners.change[0]();
    assert.equal(t.get('generation'),null);t.events.keyup(keyEvent(t,'KeyW'));t.events.keydown(keyEvent(t,'KeyW'));await flush();assert(t.get('generation'));
  });
  await check('backend rejection displays its specific reason instead of heartbeat blame',async()=>{
    const t=await split();t.events.keydown(keyEvent(t,'KeyW'));await flush();
    t.reject({status:400,payload:{error:'Invalid command',control:{armed:false,owner:null,stage:'stopping',sequence:0,last_disable:{reason:'Unexpected reported speed (vx=-0.102)'},reason:'Stopped'}}});
    await rampTick(t);assert.equal(t.get('generation'),null);assert.match(t.node('drive-alert').textContent,/Unexpected reported speed/);assert(!/heartbeat/i.test(t.node('drive-alert').textContent));
  });
  await check('network timeout is distinguished from rejected command',async()=>{
    const t=await split();t.events.keydown(keyEvent(t,'KeyW'));await flush();t.fail({name:'AbortError'});await rampTick(t);
    assert.match(t.node('drive-alert').textContent,/timed out/);assert.equal(t.get('generation'),null);
  });
  await check('inactive page blur and disconnection cannot issue global Stop',async()=>{
    const t=await ready({session:true});const before=t.requests.filter(x=>x.path.endsWith('/stop')).length;
    t.events.blur();t.events.offline();await flush();
    assert.equal(t.requests.filter(x=>x.path.endsWith('/stop')).length,before);
    t.node('stop').listeners.click[0]();await flush();
    const sent=t.requests.filter(x=>x.path.endsWith('/stop')).pop();assert.deepEqual(JSON.parse(sent.options.body),{});
  });
  await check('automatic owned-page stop includes generation but explicit Stop stays global',async()=>{
    const t=await split();const generation=t.get('generation');t.events.blur();await flush();
    const sent=t.requests.filter(x=>x.path.endsWith('/stop')).pop();const body=JSON.parse(sent.options.body);
    assert.equal(body.generation,generation);assert.equal(body.owner,t.get('owner'));
  });
  await check('stale successful status cannot undo a newer release/braking state',async()=>{
    const t=await session();press(t);await flush();release(t);await flush();
    t.get('applySessionStatus({sequence:1,armed:true,owner,stage:"holding",retired_motion:0})');
    assert.equal(t.get('lastStatus.control.stage'),'braking');assert(t.dirs.every(x=>x.disabled));assert.equal(t.get('desired'),'neutral');
  });
  await check('session speed readout distinguishes requested speed and proportional ceiling',async()=>{
    const t=await session();t.get('Object.assign(lastStatus.control,{requested_linear_m_s:.042,joystick_speed_request_m_s:.08});updateControls()');
    assert.equal(t.node('speed-request').textContent,'0.042 m/s');assert.equal(t.node('speed-limit').textContent,'0.08 m/s');
    t.get('Object.assign(lastStatus.control,{requested_linear_m_s:-.08});updateControls()');assert.equal(t.node('speed-request').textContent,'-0.080 m/s');
    t.node('stop').listeners.click[0]();assert.equal(t.node('speed-request').textContent,'0.000 m/s');
  });
  await check('LiDAR connected without messages is not displayed as live',async()=>{
    const t=await ready();t.get('renderScan({state:"waiting_messages",available:false,publisher_connections:1,messages_received:0})');
    assert.match(t.node('scan-state').textContent,/WAITING/);assert.equal(t.node('scan-connections').textContent,'1');assert.equal(t.node('scan-minimum').textContent,'— m');
  });
  await check('LiDAR live readout includes arrival rate source frame and distances',async()=>{
    const t=await ready();t.get('renderScan({state:"live",available:true,publisher_connections:1,messages_received:25,arrival_rate_hz:12.5,last_message_age_s:.1,minimum_m:1.25,valid_samples:300,samples:360,frame:"laser",publisher:"/lsn10",topic:"/scan",points:[[1,1]]})');
    assert.equal(t.node('scan-state').textContent,'LIVE SCAN');assert.equal(t.node('scan-rate').textContent,'12.5 Hz');assert.equal(t.node('scan-publisher').textContent,'/lsn10');assert.equal(t.node('scan-frame').textContent,'laser');assert.equal(t.node('scan-minimum').textContent,'1.25 m');assert.equal(t.node('scan-count').textContent,'300 / 360');
  });
  await check('LiDAR no connection multiple sources invalid and stale states never look live',async()=>{
    const t=await ready();
    for(const state of ['no_publisher','multiple_publishers','invalid','stale']){
      t.get('renderScan('+JSON.stringify({state,available:false,points:[[1,1]],minimum_m:1,frame:'old',error:state==='invalid'?'Bad geometry':null})+')');
      assert.notEqual(t.node('scan-state').textContent,'LIVE SCAN');assert.equal(t.node('scan-minimum').textContent,'— m');assert.equal(t.node('scan-frame').textContent,'—');
    }
  });
  await check('LiDAR invalid ranges are shown as incoming data without an invented distance',async()=>{
    const t=await ready();t.get('renderScan({state:"no_valid_returns",available:true,minimum_m:null,valid_samples:0,samples:360,frame:"laser",points:[]})');
    assert.match(t.node('scan-state').textContent,/NO VALID/);assert.equal(t.node('scan-minimum').textContent,'— m');assert.equal(t.node('scan-count').textContent,'0 / 360');
  });
  await check('LiDAR old points are not drawn when data is unavailable',async()=>{
    const t=await ready();let arcs=0;
    t.node('scan').getContext=()=>new Proxy({arc:()=>arcs++},{get:(object,name)=>object[name]||(()=>{})});
    t.get('drawScan({available:true,points:[[1,1]],valid_samples:1})');assert.equal(arcs,1);arcs=0;
    t.get('drawScan({available:false,points:[[1,1]]})');assert.equal(arcs,0);
  });
  await check('single scan fallback cannot imply a free-floor map or expose old colour options',async()=>{
    const t=await ready();t.get('drawScan({available:true,points:[[1,1]],valid_samples:1})');
    assert.match(t.node('scan-colour-note').textContent,/SCAN ONLY/);assert.match(t.node('scan-colour-note').textContent,/unknown/);
    assert(!fs.readFileSync(__dirname+'/dist/index.html','utf8').includes('id="scan-colour"'));
  });
  await check('plain scan plane has no radar decorations and fixed labelled distance colours',async()=>{
    const t=await ready();let strokes=0;const colours=[];
    t.node('scan').getContext=()=>new Proxy({stroke:()=>strokes++},{get:(obj,name)=>obj[name]||(()=>{}),set:(obj,name,value)=>{if(name==='fillStyle')colours.push(value);obj[name]=value;return true;}});
    t.get('drawScan({available:true,points:[[0,0],[2,0],[4,0]],valid_samples:3})');
    assert.equal(strokes,0);for(const hue of [0,120,240])assert(colours.includes('hsl('+hue+',90%,65%)'));
    assert.equal(t.get('rangeColour(NaN)'),'#8ad8bd');assert.equal(t.get('rangeColour(-1)'),'#8ad8bd');
    assert.match(t.node('scan-colour-note').textContent,/distance from laser/);assert.match(t.node('scan-colour-note').textContent,/Not object classes/);
  });
  await check('map overlay colour uses sensor ranges not transformed map coordinates',async()=>{
    const t=await ready(),colours=[];
    t.node('scan').getContext=()=>new Proxy({},{get:(obj,name)=>obj[name]||(()=>{}),set:(obj,name,value)=>{if(name==='fillStyle')colours.push(value);obj[name]=value;return true;}});
    t.get('drawOccupancy({width:1,height:1,resolution:100,origin:{x:0,y:0,yaw:0},cells:[0],frame:"map",age_s:0,overlay:{scan:[[20,20],[30,30]],scan_ranges_m:[1,3]}})');
    assert(colours.includes('hsl(60,90%,65%)'));assert(colours.includes('hsl(180,90%,65%)'));
  });
  await check('W A D travel and steering are independent; both steering keys centre',async()=>{
    const t=await split();t.events.keydown(keyEvent(t,'KeyW'));await flush();await rampTick(t);const throttle=t.get('joystickInput.throttle');
    t.events.keydown(keyEvent(t,'KeyA'));assert.equal(t.get('joystickInput.steering'),-1);assert.equal(t.get('joystickInput.throttle'),throttle);
    t.events.keydown(keyEvent(t,'KeyD'));assert.equal(t.get('joystickInput.steering'),0);
    t.events.keyup(keyEvent(t,'KeyA'));assert.equal(t.get('joystickInput.steering'),1);
    t.events.keyup(keyEvent(t,'KeyD'));assert.equal(t.get('joystickInput.steering'),0);assert(t.get('travelPedal'));
  });
  await check('steering alone never starts travel and release survives normal braking',async()=>{
    const t=await split();t.events.keydown(keyEvent(t,'KeyD'));assert.equal(t.get('desired'),'neutral');await rampTick(t);
    assert.equal(JSON.parse(t.requests.filter(r=>r.path.endsWith('/command')).pop().options.body).action,'neutral');
    t.events.keydown(keyEvent(t,'KeyW'));await flush();await rampTick(t);t.events.keyup(keyEvent(t,'KeyW'));await flush();
    assert.equal(t.get('joystickInput.steering'),1);assert.equal(t.get('joystickInput.throttle'),0);
    t.events.keyup(keyEvent(t,'KeyD'));assert.equal(t.get('joystickInput.steering'),0);
  });
  await check('faulted or pre-enable steering cannot replay held keys after enabling',async()=>{
    const t=await freshSplit();t.events.keydown(keyEvent(t,'KeyA'));await enable(t);
    t.events.keydown(keyEvent(t,'KeyA',{repeat:true}));assert.equal(t.get('joystickInput.steering'),0);
    t.events.keyup(keyEvent(t,'KeyA'));t.events.keydown(keyEvent(t,'KeyA'));assert.equal(t.get('joystickInput.steering'),-1);
    t.events.blur();assert.equal(t.get('joystickInput.steering'),0);await t.get('poll()');await enable(t);
    t.events.keydown(keyEvent(t,'KeyA',{repeat:true}));assert.equal(t.get('joystickInput.steering'),0);
  });
  await check('editable shortcuts and mouse pad cannot steer keyboard mode',async()=>{
    for(const extra of [{ctrlKey:true},{altKey:true},{metaKey:true},{target:{tagName:'INPUT'}},{target:{isContentEditable:true}}]){
      const t=await split();t.events.keydown(keyEvent(t,'KeyA',extra));assert.equal(t.get('joystickInput.steering'),0);
    }
    const t=await split();t.node('joystick-pad').listeners.pointerdown[0]({pointerId:1,pointerType:'mouse',button:0,clientX:220,clientY:100,preventDefault(){}});
    assert.equal(t.get('pointer'),null);assert.equal(t.get('joystickInput.steering'),0);
  });
  await check('map is rendered only from valid cached data and expires on disconnect',async()=>{
    const t=await ready();t.get('mapView={available:true,revision:1,width:2,height:2,resolution:.1,origin:{x:0,y:0,yaw:0},cells:[0,-1,100,0],frame:"map",age_s:20,overlay:{robot:{x:.1,y:.1,yaw:0}}};mapFetchedAt=performance.now();drawScan(null)');
    assert.match(t.node('scan-colour-note').textContent,/MAP map/);assert.match(t.node('scan-colour-note').textContent,/not to scale/);
    t.events.offline();assert.equal(t.get('mapView'),null);assert(!t.node('scan-colour-note').textContent.startsWith('MAP'));
  });
  await check('missing TF never produces a pretend mapped robot pose',async()=>{
    const t=await ready();t.get('drawOccupancy({width:1,height:1,resolution:1,origin:{x:0,y:0,yaw:1.57},cells:[-1],frame:"map",age_s:0,overlay:{}})');
    assert.match(t.node('scan-colour-note').textContent,/Car hidden/);assert.match(t.node('scan-colour-note').textContent,/Not guaranteed drivable/);
  });
  await check('map icon respects translated rotated grid origin and bottom-up rows',async()=>{
    const t=await ready();let position=null;
    t.node('scan').getContext=()=>new Proxy({translate:(x,y)=>position=[x,y]},{get:(obj,name)=>obj[name]||(()=>{})});
    t.get('drawOccupancy({width:2,height:2,resolution:1,origin:{x:10,y:20,yaw:Math.PI/2},cells:[0,0,0,0],frame:"map",age_s:0,overlay:{robot:{x:10,y:21,yaw:Math.PI/2}}})');
    assert(Math.abs(position[0]-320)<1e-9);assert(Math.abs(position[1]-347)<1e-9);
  });
  await check('disconnect clears LiDAR telemetry and does not preserve a live badge',async()=>{
    const t=await ready();t.get('renderScan({state:"live",available:true,publisher_connections:1,arrival_rate_hz:10,minimum_m:1,valid_samples:1,samples:1,frame:"laser",points:[[1,1]]})');t.events.offline();
    assert.equal(t.node('scan-state').textContent,'UNKNOWN');assert.equal(t.node('scan-rate').textContent,'—');assert.equal(t.node('scan-connections').textContent,'—');
  });
  console.log(count+' frontend unit checks passed. Fake DOM only; not a robot/browser benchmark.');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
