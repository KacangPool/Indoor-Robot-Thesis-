'use strict';
const assert=require('node:assert/strict');
const joystick=require('./dist/joystick.js');
let count=0;
function test(name,fn){fn();count++;console.log('PASS '+name);}
test('centre and invalid geometry stay zero',()=>{for(const value of [[0,0,100],[0,0,0],[NaN,0,1],[1,Infinity,1]]){const a=joystick.axes(...value);assert.equal(a.throttle,0);assert.equal(a.steering,0);}});
test('up/down travel and left/right steering signs',()=>{assert(joystick.axes(0,-100,100).throttle>0);assert(joystick.axes(0,100,100).throttle<0);assert(joystick.axes(-100,0,100).steering<0);assert(joystick.axes(100,0,100).steering>0);});
test('drag beyond pad clamps to circular input range',()=>{const a=joystick.axes(1e6,1e6,100);assert(Math.abs(a.throttle)<=1);assert(Math.abs(a.steering)<=1);assert(Math.abs(Math.hypot(a.x,a.y)-1)<1e-10);});
test('every normalized drag remains bounded',()=>{for(let x=-400;x<=400;x+=20)for(let y=-400;y<=400;y+=20){const a=joystick.axes(x,y,100);assert(Math.abs(a.throttle)<=1);assert(Math.abs(a.steering)<=1);}});
test('independent corners retain full throttle and steering',()=>{const a=joystick.axes(100,-100,100,'independent');assert.equal(a.throttle,1);assert.equal(a.steering,1);assert(joystick.axes(100,-100,100).throttle<1);});
test('independent mode remains bounded in every direction',()=>{for(let x=-400;x<=400;x+=20)for(let y=-400;y<=400;y+=20){const a=joystick.axes(x,y,100,'independent');assert(Math.abs(a.throttle)<=1);assert(Math.abs(a.steering)<=1);}assert.equal(joystick.axes(100,0,100,'independent').throttle,0);});
test('steering-only mode ignores vertical drag and never supplies throttle',()=>{for(let x=-400;x<=400;x+=20)for(let y=-400;y<=400;y+=20){const a=joystick.axes(x,y,100,'steering');assert.equal(a.throttle,0);assert.equal(a.y,0);assert.equal(a.steering,Math.max(-1,Math.min(1,x/100)));}});
test('S-curve is bounded monotonic and reaches only 0.30',()=>{let v=0;for(let i=0;i<100;i++){const next=joystick.rampSpeed(v,false,.1);assert(next>=v);assert(next<=.3);v=next;}assert.equal(v,.3);assert(Math.abs(joystick.rampSpeed(0,false,.1)-.0003552)<1e-12);});
test('ramp braking never reverses and scheduler gaps cannot catch up',()=>{let v=.3;for(let i=0;i<50;i++)v=joystick.rampSpeed(v,true,.1);assert.equal(v,0);assert.equal(joystick.rampSpeed(0,true,.1),0);assert(Math.abs(joystick.rampSpeed(0,false,20)-.0007938)<1e-12);assert.equal(joystick.rampSpeed(0,false,NaN),0);});
test('five-second profile is slow then fast then levels off',()=>{let v=0;const values=[0];for(let i=0;i<50;i++){v=joystick.rampSpeed(v,false,.1);values.push(v);}assert(Math.abs(values[10]-.0312)<1e-10);assert(Math.abs(values[25]-.15)<1e-10);assert(Math.abs(values[40]-.2688)<1e-10);assert(values[25]-values[20]>values[5]-values[0]);assert(values[50]-values[45]<values[25]-values[20]);});
test('zero elapsed and resumed acceleration preserve speed without jump',()=>{for(const v of [0,.03,.15,.29,.3]){assert.equal(joystick.rampSpeed(v,false,0),v);const next=joystick.rampSpeed(v,false,.01);assert(next>=v);assert(next-v<.001);}assert.equal(joystick.rampSpeed(0,false,-1),0);});
console.log(count+' joystick geometry checks passed.');
