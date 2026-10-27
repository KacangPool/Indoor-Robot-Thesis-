/* Pure orthographic view state. No DOM, network, timers or robot access. */
(function(root){
  'use strict';
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  function initial(){return {zoom:1,yaw:0,pitch:0,panX:0,panY:0,tool:'orbit'};}
  function update(state,operation,x=0,y=0){
    if(![x,y].every(Number.isFinite))return {...state};
    const s={...state};
    if(operation==='reset')return initial();
    if(operation==='zoom')s.zoom=clamp(s.zoom*clamp(x,0.5,2),0.25,8);
    if(operation==='pan'){s.panX=clamp(s.panX+x,-2000,2000);s.panY=clamp(s.panY+y,-2000,2000);}
    if(operation==='orbit'){s.yaw=((s.yaw+x+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI;s.pitch=clamp(s.pitch+y,0,1.25);}
    if(operation==='oblique'){s.pitch=0.65;s.yaw=-0.35;s.tool='orbit';}
    if(operation==='tool')s.tool=x===1?'pan':'orbit';
    return s;
  }
  function matrix(s,width,height){
    const c=Math.cos(s.yaw),sn=Math.sin(s.yaw),p=Math.cos(s.pitch),z=s.zoom;
    const a=z*c,b=z*sn*p,cc=-z*sn,d=z*c*p;
    return [a,b,cc,d,width/2+s.panX-a*width/2-cc*height/2,height/2+s.panY-b*width/2-d*height/2];
  }
  function project(s,p,width,height){
    const m=matrix(s,width,height);
    return [m[0]*p[0]+m[2]*p[1]+m[4],m[1]*p[0]+m[3]*p[1]+m[5]-(p[2]||0)*s.zoom*Math.sin(s.pitch)];
  }
  // Inverse screen projection on z=0; no inferred body transform or ROS data.
  function headingFromPoint(s,p,width,height){
    if(!Array.isArray(p)||p.length!==2||!p.every(Number.isFinite))return null;
    const m=matrix(s,width,height),det=m[0]*m[3]-m[1]*m[2];
    const centre=project(s,[width/2,height/2,0],width,height);
    if(!Number.isFinite(det)||Math.abs(det)<1e-8||Math.hypot(p[0]-centre[0],p[1]-centre[1])<24)return null;
    const x=p[0]-m[4],y=p[1]-m[5];
    const dx=(m[3]*x-m[2]*y)/det-width/2,dy=(-m[1]*x+m[0]*y)/det-height/2;
    return Math.atan2(-dx,-dy); // scan pixels: right=-laser Y, up=laser X
  }
  function frontUp(s,anchor,angle,width,height){
    if(!Array.isArray(anchor)||anchor.length!==2||!anchor.every(Number.isFinite)||!Number.isFinite(angle))return {...s};
    const result={...s,yaw:-Math.PI/2-angle,pitch:0,panX:0,panY:0};
    const p=project(result,anchor,width,height);
    result.panX=width/2-p[0];result.panY=height/2-p[1];
    return result;
  }
  const api={initial,update,matrix,project,headingFromPoint,frontUp};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  if(root)root.FahadSceneGeometry=api;
})(typeof window!=='undefined'?window:null);
