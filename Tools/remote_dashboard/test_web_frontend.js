/* Fake DOM/HTTP only. No real browser, ROS, serial or physical output. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {webcrypto} = require('node:crypto');
const source = fs.readFileSync(__dirname+'/dist/web_crawl.js','utf8');
function element() {
  return {disabled:false,hidden:false,textContent:'',value:'rgb',listeners:{},
    addEventListener(name, fn) {(this.listeners[name] ||= []).push(fn);}, setPointerCapture(){},
    set src(value) {this._src=value;if(this.onload)this.onload();}};
}
function fixture() {
  const nodes={}, events={}, intervals=[], timers=[], requests=[];
  const node = id => nodes[id] ||= element();
  let time=100, focused=true, hidden=false, fail=false, prepareWait=null, commandWait=null;
  let state='available', activeOwner=null, ready=true;
  const context = vm.createContext({console,crypto:webcrypto,Uint8Array,AbortController,
    performance:{now:()=>time}, URL:{createObjectURL:()=> 'blob:fake',revokeObjectURL(){}},
    document:{getElementById:node,get hidden(){return hidden;},hasFocus:()=>focused,
      addEventListener:(name,fn)=>{events[name]=fn;}},
    window:{addEventListener:(name,fn)=>{events[name]=fn;}},
    setTimeout:(fn,delay)=>{timers.push({fn,delay});return timers.length;},clearTimeout(){},
    setInterval:(fn,delay)=>{intervals.push({fn,delay});},
    fetch:async (path,options={})=>{
      requests.push({path,options});
      if(fail) throw new Error('Fake offline');
      let payload={};const body=options.body ? JSON.parse(options.body) : {};
      if(path==='/api/bootstrap')payload={key:'fake',boot_id:'test'};
      else if(path==='/api/status')payload={boot_id:'test',mode:'web_crawl_one_shot',
        crawl:{state,owner:activeOwner,ready:ready&&state==='available',reason:'Test status',stop_feedback:null},
        cameras:{rgb:{available:true,age_s:.1},yolo:{available:true,age_s:.1}}};
      else if(path==='/api/crawl/prepare'){
        if(prepareWait)await prepareWait;
        state='prepared';activeOwner=body.owner;payload={token:'fake-token'};
      }else if(path==='/api/crawl/command'){
        if(commandWait)await commandWait;
        if(body.action==='forward')state='running';
      }else if(path==='/api/crawl/stop')state='spent';
      return {ok:true,json:async()=>payload,blob:async()=>({})};
    }});
  vm.runInContext(source,context,{filename:'web_crawl.js'});
  return {node,events,intervals,timers,requests,get:e=>vm.runInContext(e,context),
    set:e=>vm.runInContext(e,context),focus:v=>{focused=v;},hide:v=>{hidden=v;},fail:v=>{fail=v;},
    time:v=>{time=v;},ready:v=>{ready=v;},delayPrepare:p=>{prepareWait=p;},delayCommand:p=>{commandWait=p;}};
}
const flush=()=>new Promise(resolve=>setImmediate(resolve));
async function ready(){const t=fixture();await flush();await t.get('frame()');await flush();return t;}
async function prepare(t){await t.node('prepare').listeners.click[0]();await flush();}
const pointer=id=>({pointerId:id,pointerType:'mouse',button:0,preventDefault(){}});
const commands=t=>t.requests.filter(x=>x.path==='/api/crawl/command').map(x=>JSON.parse(x.options.body));
async function main(){
  let count=0;
  async function test(name,fn){await fn();console.log('PASS '+name);count++;}
  await test('loads disabled until real mode status and decoded image',async()=>{
    const t=fixture();assert(t.node('prepare').disabled);await flush();assert(t.node('prepare').disabled);
    await t.get('frame()');assert(!t.node('prepare').disabled);assert(t.node('forward').disabled);
    assert.equal(commands(t).length,0);
  });
  await test('prepare has no forward command; heartbeat is neutral',async()=>{
    const t=await ready();await prepare(t);assert(t.get('token'));assert.equal(commands(t).length,0);
    await t.get("send('heartbeat')");assert.equal(commands(t)[0].action,'heartbeat');
  });
  await test('hold requests one forward and release cancels',async()=>{
    const t=await ready();await prepare(t);
    t.node('forward').listeners.pointerdown[0](pointer(1));await flush();
    assert.equal(commands(t).filter(x=>x.action==='forward').length,1);
    assert(!t.node('forward').disabled,'held button must still receive release');
    t.node('forward').listeners.pointerup[0](pointer(1));assert.equal(t.get('token'),null);
    assert(t.requests.some(x=>x.path==='/api/crawl/stop'));
  });
  await test('second touch or repeated press cannot replay forward',async()=>{
    const t=await ready();await prepare(t);
    t.node('forward').listeners.pointerdown[0](pointer(1));await flush();
    t.node('forward').listeners.pointerdown[0](pointer(2));await flush();
    assert.equal(commands(t).filter(x=>x.action==='forward').length,1);
    assert.equal(t.get('pointer'),1);
  });
  await test('pointer cancel and lost capture cancel',async()=>{
    for(const name of ['pointercancel','lostpointercapture']){
      const t=await ready();await prepare(t);t.node('forward').listeners.pointerdown[0](pointer(1));await flush();
      t.node('forward').listeners[name][0](pointer(1));assert.equal(t.get('token'),null);
    }
  });
  await test('keyboard hold/release and non-forward Space stop',async()=>{
    const t=await ready();await prepare(t);
    const event={key:'Enter',repeat:false,preventDefault(){}};
    t.node('forward').listeners.keydown[0](event);await flush();assert(t.get('held'));
    t.node('forward').listeners.keyup[0](event);assert(t.get('retired'));
    const u=await ready();await prepare(u);
    u.events.keydown({key:' ',code:'Space',target:u.node('stop'),preventDefault(){}});assert.equal(u.get('token'),null);
  });
  await test('blur, hidden page, page close and offline stop without rearming',async()=>{
    for(const name of ['blur','visibilitychange','pagehide','offline']){
      const t=await ready();await prepare(t);if(name==='visibilitychange')t.hide(true);t.events[name]();
      assert.equal(t.get('token'),null);assert(t.get('retired'));
      t.hide(false);await t.get('poll()');assert(t.node('prepare').disabled);
    }
  });
  await test('unfocused and hidden page cannot prepare',async()=>{
    const t=await ready();t.focus(false);await prepare(t);assert.equal(t.get('token'),null);
    t.focus(true);t.hide(true);await prepare(t);assert.equal(t.get('token'),null);
  });
  await test('stop beats an in-flight prepare response',async()=>{
    const t=await ready();let release;t.delayPrepare(new Promise(r=>{release=r;}));
    const pending=t.node('prepare').listeners.click[0]();t.events.blur();release();await pending;await flush();
    assert.equal(t.get('token'),null);assert(t.get('retired'));assert.equal(commands(t).length,0);
  });
  await test('failed heartbeat cannot retry/reconnect forward',async()=>{
    const t=await ready();await prepare(t);t.fail(true);await t.get("send('heartbeat')");
    assert.equal(t.get('token'),null);t.fail(false);await t.get('poll()');
    assert(t.node('prepare').disabled);assert.equal(commands(t).filter(x=>x.action==='forward').length,0);
  });
  await test('stale status or image cancels before starting',async()=>{
    for(const expression of ['statusAt=-1000','imageAt=-1000']){
      const t=await ready();await prepare(t);t.set(expression);t.node('forward').listeners.pointerdown[0](pointer(1));await flush();
      assert.equal(commands(t).filter(x=>x.action==='forward').length,0);
    }
  });
  await test('view change cancels permit and clears image',async()=>{
    const t=await ready();await prepare(t);t.node('source').value='yolo';t.node('source').listeners.change[0]();
    assert.equal(t.get('token'),null);assert(t.node('camera').hidden);assert.equal(t.get('imageAt'),0);
  });
  await test('completed backend never offers rearm after reload state',async()=>{
    const t=await ready();await prepare(t);t.get('cancel()');await t.get('poll()');
    assert(t.node('prepare').disabled);assert.equal(t.get('current.state'),'spent');
  });
  await test('slow heartbeat cannot enqueue a forward behind it',async()=>{
    const t=await ready();await prepare(t);let release;t.delayCommand(new Promise(r=>{release=r;}));
    const pending=t.get("send('heartbeat')");t.node('forward').listeners.pointerdown[0](pointer(1));release();await pending;
    assert.equal(commands(t).filter(x=>x.action==='forward').length,0);assert(!t.get('held'));
  });
  console.log(count+' one-shot frontend checks passed (fake DOM only).');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
