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
assert(css.includes("'camera lidar readings' 'camera controls readings'"));
assert(css.includes('.camera-stage img{object-fit:fill}'));
console.log('Sensor-view checks passed: colours, map cache, bounded individual rays, stale/invalid rejection, blind zone, metric resize, layout and unverified heading.');
