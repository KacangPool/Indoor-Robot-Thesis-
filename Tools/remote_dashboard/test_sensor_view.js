'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const view=require('./dist/sensor_view.js');
assert.equal(view.rangeColour(0),'hsl(0,90%,65%)');
assert.equal(view.rangeColour(4),'hsl(240,90%,65%)');
const nodes={};const ui=id=>nodes[id] ||= {textContent:'',className:'',width:640,height:360,
  getContext:()=>new Proxy({},{get:()=>()=>{}})};
const renderer=view.create({ui,pill:()=>{},seconds:value=>value+' s',getMap:()=>null,canUseMap:()=>false});
renderer.drawScan({available:true,points:[[1,0]],valid_samples:1});
assert.match(ui('scan-colour-note').textContent,/distance from laser/);
renderer.drawOccupancy({width:1,height:1,resolution:1,origin:{x:0,y:0,yaw:0},cells:[-1],overlay:{},frame:'map',age_s:0});
assert.match(ui('scan-colour-note').textContent,/Car hidden/);renderer.reset();
const text=fs.readFileSync(__dirname+'/dist/sensor_view.js','utf8');
for(const forbidden of ['fetch(', 'setInterval(', 'setTimeout(', '/api/drive/', 'window.FahadJoystick'])assert(!text.includes(forbidden));
let surfaces=0,uploads=0;
const dom={createElement:()=>{surfaces++;return {getContext:()=>({
  createImageData:(w,h)=>({data:new Uint8ClampedArray(w*h*4)}),
  putImageData:()=>uploads++
})};}};
const rasterView=view.create({ui,pill:()=>{},seconds:String,getMap:()=>null,canUseMap:()=>false,document:dom});
const map={width:2,height:1,resolution:1,origin:{x:0,y:0,yaw:0},cells:[-1,0],overlay:{},frame:'map',age_s:0};
rasterView.drawOccupancy(map);rasterView.drawOccupancy(map);
assert.equal(surfaces,1);assert.equal(uploads,1); // unchanged cells reuse one raster
rasterView.reset();rasterView.drawOccupancy(map);
assert.equal(surfaces,2);assert.equal(uploads,2); // disconnect/reset invalidates cache
const rays={available:true,range_min_m:0.1,ray_width_rad:0.01,observed_rays:[[0,1],[1,4],[2,NaN],[3,0],[4,Infinity]]};
const sectors=view.observedSectors(rays);
assert.equal(sectors.length,2);assert.equal(sectors[0].inner,0.1);
assert.equal(sectors[0].outer,0.97);assert.equal(sectors[1].outer,3.97);
assert.equal(sectors[0].half,0.005);assert.equal(sectors[1].angle,1); // no interpolation across gap
assert.equal(view.observedSectors({...rays,observed_rays:[[0,100]]})[0].outer,15.97);
for(const override of [{available:false},{range_min_m:-1},{range_min_m:NaN},{ray_width_rad:0},{ray_width_rad:1}])
  assert.deepEqual(view.observedSectors({...rays,...override}),[]);
assert.equal(view.observedSectors({...rays,observed_rays:Array(2000).fill([0,1])}).length,720);
const drawn=[];nodes.scan.getContext=()=>new Proxy({fillText:(s)=>drawn.push(s)},{get:(o,k)=>o[k]||(()=>{})});
nodes.scan.clientWidth=900;nodes.scan.clientHeight=320;
renderer.drawScan({...rays,points:[[1,0]],valid_samples:1});
assert.equal(nodes.scan.width,900);assert.equal(nodes.scan.height,320);
assert.match(ui('scan-colour-note').textContent,/NOT guaranteed traversable/);
assert(drawn.some(s=>s.includes('car heading unverified')));
const css=fs.readFileSync(__dirname+'/dist/controls.css','utf8');
assert(css.includes("'camera lidar controls' 'camera lidar readings'"));
assert(css.includes('.camera-stage img{object-fit:fill}'));
console.log('Sensor-view checks passed: colours, map cache, bounded individual rays, stale/invalid rejection, blind zone, metric resize, layout and unverified heading.');
const geometry=require('./dist/scene_geometry.js');let state=geometry.initial();
assert.deepEqual(geometry.project(state,[25,40,0],640,480),[25,40]);
for(let i=0;i<100;i++)state=geometry.update(state,'zoom',2);
assert.equal(state.zoom,8);for(let i=0;i<100;i++)state=geometry.update(state,'zoom',.5);assert.equal(state.zoom,.25);
state=geometry.update(geometry.initial(),'oblique');
const low=geometry.project(state,[320,240,0],640,480),high=geometry.project(state,[320,240,10],640,480);
assert(high[1]<low[1]);assert.deepEqual(geometry.update(state,'reset'),geometry.initial());
assert.deepEqual(geometry.update(state,'pan',NaN,1),state);
let tick=1000;const eventNodes={};
const eventUI=id=>eventNodes[id]||=(Object.assign({listeners:{},width:640,height:360,textContent:'',
  addEventListener(k,fn){this.listeners[k]=fn;},setPointerCapture(){},hasPointerCapture(){return false;},
  getContext:()=>new Proxy({},{get:()=>()=>{}})}));
const interactive=view.create({ui:eventUI,pill:()=>{},seconds:String,getMap:()=>null,canUseMap:()=>false,now:()=>tick});
interactive.renderScan({available:true,age_s:0,points:[[1,0]],valid_samples:1});
eventUI('scene-zoom-in').listeners.click();assert.equal(interactive.viewState().zoom,1.25);
eventUI('scene-orbit').listeners.click();assert(interactive.viewState().pitch>0);
eventUI('scan').listeners.pointerdown({pointerId:1,button:0,clientX:10,clientY:10,preventDefault(){}});
eventUI('scan').listeners.pointermove({pointerId:1,clientX:30,clientY:30,preventDefault(){}});
assert.notEqual(interactive.viewState().yaw,0);
tick=4000;eventUI('scene-zoom-in').listeners.click();assert.match(eventUI('scan-colour-note').textContent,/No current scan/);
console.log('Orthographic view bounds, reset, pointer orbit, input isolation and stale redraw checks passed.');

// Heading selection and follow are display-only: rotate the whole scene, never
// rewrite scan points, guess velocity heading or manufacture a body transform.
const close=(a,b)=>assert(Math.abs(a-b)<1e-9,`${a} != ${b}`);
const angleClose=(a,b)=>{close(Math.sin(a-b),0);close(Math.cos(a-b),1);};
for(const yaw of [0,Math.PI/2,Math.PI,-Math.PI/2,.37]){
  const s=geometry.update(geometry.update(geometry.initial(),'orbit',.4,.5),'pan',30,-20);
  const p=geometry.project(s,[320-Math.sin(yaw)*100,240-Math.cos(yaw)*100,0],640,480);
  angleClose(geometry.headingFromPoint(s,p,640,480),yaw);
  const anchor=[200,170],angle=-Math.PI/2-yaw,front=geometry.frontUp(s,anchor,angle,640,480);
  const origin=geometry.project(front,anchor,640,480);
  const nose=geometry.project(front,[anchor[0]+Math.cos(angle)*50,anchor[1]+Math.sin(angle)*50,0],640,480);
  close(origin[0],320);close(origin[1],240);close(nose[0],320);assert(nose[1]<240);
}
assert.equal(geometry.headingFromPoint(geometry.initial(),[320,240],640,480),null);
assert.equal(geometry.headingFromPoint(geometry.initial(),[NaN,0],640,480),null);
assert.deepEqual(geometry.frontUp(geometry.initial(),[0,0],NaN,640,480),geometry.initial());

let time=1000,currentMap=null;const frontNodes={},transforms=[],labels=[];
const frontUI=id=>frontNodes[id]||={listeners:{},width:640,height:480,textContent:'',
  addEventListener(k,fn){this.listeners[k]=fn;},setAttribute(){},
  getBoundingClientRect:()=>({left:100,top:50,width:320,height:240}),
  getContext:()=>new Proxy({transform:(...v)=>transforms.push(v),fillText:s=>labels.push(s)},{get:(o,k)=>o[k]||(()=>{})})};
const frontView=view.create({ui:frontUI,pill(){},seconds:String,getMap:()=>currentMap,canUseMap:()=>!!currentMap,now:()=>time});
const scan={available:true,age_s:0,frame:'laser',points:[[1,0]],valid_samples:1};
const original=JSON.stringify(scan);
frontView.renderScan(scan);assert.match(frontUI('scene-heading').textContent,/Front unknown/);
const click=id=>frontUI(id).listeners.click();
const mark=(x=260,y=230)=>{click('scene-mark-front');frontUI('scan').listeners.pointerdown({pointerId:9,button:0,clientX:x,clientY:y,preventDefault(){}});};
mark(); // CSS-scaled click below centre => nose at laser -X, not +X.
assert.equal(frontView.viewState().followFront,true);angleClose(frontView.viewState().manualFront.yaw,Math.PI);
assert.match(frontUI('scene-heading').textContent,/operator mark/);assert(labels.some(s=>s.includes('manual front')));
const south=transforms.at(-1);close(south[0],-1);close(south[3],-1);
assert.equal(JSON.stringify(scan),original);assert.equal(scan.robot_pose,undefined);
click('scene-zoom-in');close(frontView.viewState().zoom,1.25);assert(frontView.viewState().followFront);
click('scene-orbit');assert.equal(frontView.viewState().followFront,false);
click('scene-reset');assert(frontView.viewState().followFront);assert(frontView.viewState().manualFront);
// Fresh TF overrides manual display mark; lateral offset is centred too.
frontView.renderScan({...scan,robot_pose:{x:.1,y:.2,yaw:Math.PI/2},vx:-.1});
assert.match(frontUI('scene-heading').textContent,/body \+X/);
let matrix=transforms.at(-1);close(matrix[0],0);close(matrix[1],1);
const bodyPixel=[320-.2*54,240-.1*54];
close(matrix[0]*bodyPixel[0]+matrix[2]*bodyPixel[1]+matrix[4],320);
close(matrix[1]*bodyPixel[0]+matrix[3]*bodyPixel[1]+matrix[5],240);
frontView.renderScan({...scan,robot_pose:{x:.1,y:.2,yaw:Math.PI/2},vx:.1});
assert.deepEqual(transforms.at(-1),matrix); // reverse does not flip the nose
// A manual laser-frame mark cannot supply a missing map-frame body pose.
currentMap={available:true,width:2,height:2,resolution:1,origin:{x:0,y:0,yaw:.3},cells:[-1,0,0,0],overlay:{},frame:'map',age_s:0};
frontView.drawScan(scan);assert.match(frontUI('scene-heading').textContent,/Front unknown/);
assert(frontUI('scene-mark-front').disabled);
currentMap={...currentMap,overlay:{robot:{x:1,y:1,yaw:.8}}};frontView.drawScan(scan);
matrix=transforms.at(-1);close(Math.atan2(matrix[1],matrix[0]),-.5*Math.PI+.8-.3);
currentMap=null;frontView.renderScan({...scan,frame:'other_laser'});assert.equal(frontView.viewState().manualFront,null);
frontView.renderScan(scan);mark();click('scene-clear-front');assert.equal(frontView.viewState().manualFront,null);
mark();time=5000;click('scene-zoom-in');assert.match(frontUI('scene-heading').textContent,/Front unknown/);
click('scene-mark-front');assert.equal(frontView.viewState().markingFront,false);
frontView.reset();assert.equal(frontView.viewState().manualFront,null);
console.log('Front-up checks passed: inverse click geometry, scaled canvas, TF precedence, reverse, map/scan frames, freshness, reset and no sensor mutation.');
