/* Pointer joystick: normalized UI input only, no network or motor access. */
(function(root){
  'use strict';
  function axes(dx,dy,radius,mode='circular'){
    if(![dx,dy,radius].every(Number.isFinite)||radius<=0)return {throttle:0,steering:0,x:0,y:0};
    const distance=Math.hypot(dx,dy),scale=distance>radius?radius/distance:1;
    const x=mode==='independent'?Math.max(-1,Math.min(1,dx/radius)):dx*scale/radius;
    const y=mode==='steering'?0:mode==='independent'?Math.max(-1,Math.min(1,dy/radius)):dy*scale/radius;
    const steerX=mode==='steering'?Math.max(-1,Math.min(1,dx/radius)):x;
    return {throttle:-y||0,steering:steerX||0,x:steerX||0,y:y||0};
  }
  function rampSpeed(speed,braking,elapsed){
    if(![speed,elapsed].every(Number.isFinite))return 0;
    const dt=Math.max(0,Math.min(.15,elapsed));
    const current=Math.max(0,Math.min(.30,speed));
    if(dt===0)return current;
    if(braking)return Math.max(0,current-.08*dt);
    // Smoothstep: five seconds of healthy held input, not wall-clock catch-up.
    // Invert the curve to resume continuously from the current speed, including
    // after an opposing-key deceleration. Release/Brake do not use this easing.
    const phase=.5-Math.sin(Math.asin(1-2*current/.30)/3);
    const t=Math.min(1,phase+dt/5);
    return .30*t*t*(3-2*t);
  }
  function bind(options){
    const pad=options.pad,knob=options.knob,readout=options.readout;
    let pointer=null,last={throttle:0,steering:0,x:0,y:0};
    function paint(value){
      const box=pad.getBoundingClientRect(),travel=Math.min(box.width,box.height)*.30;
      last=value;knob.style.setProperty('--stick-x',(value.x*travel)+'px');knob.style.setProperty('--stick-y',(value.y*travel)+'px');
      readout.textContent=options.mode && options.mode()==='steering'?'Steering '+Math.round(value.steering*100)+'% · travel from held pedal/key':'Throttle '+Math.round(value.throttle*100)+'% · steering '+Math.round(value.steering*100)+'%';
    }
    function reset(){
      const id=pointer;pointer=null;paint({throttle:0,steering:0,x:0,y:0});
      if(id!==null&&pad.hasPointerCapture&&pad.hasPointerCapture(id))pad.releasePointerCapture(id);
    }
    function sample(event){
      const box=pad.getBoundingClientRect();
      const value=axes(event.clientX-box.left-box.width/2,event.clientY-box.top-box.height/2,Math.min(box.width,box.height)*.38,options.mode?options.mode():'circular');
      paint(value);options.onMove(value);
    }
    pad.addEventListener('pointerdown',event=>{
      if(pad.disabled||pointer!==null||!options.enabled()||(event.pointerType==='mouse'&&event.button!==0))return;
      event.preventDefault();if(!options.onStart(event.pointerId,event))return;pointer=event.pointerId;
      try{pad.setPointerCapture(pointer);}catch(_){reset();options.onEnd('captureerror');return;}
      sample(event);
    });
    pad.addEventListener('pointermove',event=>{if(pointer!==event.pointerId)return;event.preventDefault();sample(event);});
    pad.addEventListener('dragstart',event=>event.preventDefault());
    ['pointerup','pointercancel','lostpointercapture'].forEach(name=>pad.addEventListener(name,event=>{
      if(pointer!==event.pointerId)return;reset();options.onEnd(name);
    }));
    pad.addEventListener('keydown',event=>{if(event.key===' '||event.key==='Enter'){event.preventDefault();options.onEnd('keyboard');}});
    reset();return {reset,value:()=>last};
  }
  const api={axes,bind,rampSpeed};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  if(root)root.FahadJoystick=api;
})(typeof window!=='undefined'?window:null);
