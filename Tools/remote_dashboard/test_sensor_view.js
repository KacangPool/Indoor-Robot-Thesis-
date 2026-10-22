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
console.log('6 standalone sensor-view checks passed: colours, scan, map, side-effect boundary, injected raster, cache reset.');
