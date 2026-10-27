/* Reusable read-only scan/map renderer. No fetch, timers, ROS or drive access. */
(function(root){
  'use strict';
const geometry=typeof module!=='undefined'&&module.exports?require('./scene_geometry.js'):root.FahadSceneGeometry;
// Operator-reported orientation, ONLY a display preset for this scan frame.
// Never export this as TF, sensor calibration, body position or driving intent.
function reportedFront(scan){
  return scan&&scan.available&&scan.frame==='laser'?{x:0,y:0,yaw:Math.PI,source:'reported preset'}:null;
}
function rangeColour(distance){
  return Number.isFinite(distance) && distance>=0?'hsl('+Math.round(Math.min(1,distance/4)*240)+',90%,65%)':'#8ad8bd';
}

// Pure display geometry. Angular sampling bins are a visibility sketch, NOT
// measured optical beam footprints or proof of clearance between rays. No joins
// across missing bins; infinite/no-return readings never imply empty space.
function observedSectors(scan){
  if(!scan || !scan.available || !Number.isFinite(scan.range_min_m) || scan.range_min_m<0 ||
     !Number.isFinite(scan.ray_width_rad) || scan.ray_width_rad<=0 || scan.ray_width_rad>0.1)return [];
  const inner=scan.range_min_m,half=scan.ray_width_rad/2;
  return (Array.isArray(scan.observed_rays)?scan.observed_rays:[]).slice(0,720).flatMap(ray=>{
    if(!Array.isArray(ray) || ray.length!==2 || !ray.every(Number.isFinite))return [];
    const [angle,distance]=ray,outer=Math.min(16,distance)-0.03;
    return distance>0 && outer>inner?[{angle,half,inner,outer}]:[];
  });
}

function create(options){
  const {ui,pill,seconds,getMap,canUseMap,document:dom}=options;
  const now=options.now||(()=>Date.now());
  let mapRaster=null,view=geometry.initial(),lastScan=null,expiresAt=0,drag=null;
  let followFront=true,markingFront=false,manualFront=null;
  let fixedMap=true,renderView=geometry.initial();
  const zoomLabel=ui('scene-zoom');
  function repaint(){drawScan(now()<expiresAt?lastScan:{available:false});}
  function action(name,x,y){
    if(['orbit','oblique','pan','tool'].includes(name)){followFront=false;markingFront=false;fixedMap=false;}
    if(name==='reset'){followFront=true;markingFront=false;}
    view=geometry.update(view,name,x,y);repaint();
  }
  function listen(id,event,handler,opts){const node=ui(id);if(node&&typeof node.addEventListener==='function')node.addEventListener(event,handler,opts);}
  for(const [id,operation,x] of [['scene-zoom-in','zoom',1.25],['scene-zoom-out','zoom',0.8],['scene-reset','reset',0],['scene-orbit','oblique',0]])
    listen(id,'click',()=>action(operation,x,0));
  listen('scene-pan','click',()=>action('tool',view.tool==='pan'?0:1,0));
  listen('scene-front','click',()=>{followFront=fixedMap?true:!followFront;fixedMap=false;markingFront=false;repaint();});
  listen('scene-map','click',()=>{fixedMap=true;followFront=true;markingFront=false;view=geometry.initial();repaint();});
  listen('scene-mark-front','click',()=>{
    if(now()>=expiresAt||!lastScan||!lastScan.frame||canUseMap())return;
    markingFront=!markingFront;followFront=false;fixedMap=false;drag=null;view=geometry.initial();repaint();
  });
  listen('scene-clear-front','click',()=>{manualFront=null;markingFront=false;repaint();});
  listen('scene-flip-front','click',()=>{
    if(now()>=expiresAt||!lastScan||canUseMap()||validPose(lastScan.robot_pose))return;
    const front=manualFront&&manualFront.frame===lastScan.frame?manualFront:reportedFront(lastScan);
    if(!front)return;
    manualFront={frame:lastScan.frame,yaw:front.yaw+Math.PI};markingFront=false;followFront=true;view=geometry.initial();repaint();
  });
  listen('scan','wheel',event=>{if(!Number.isFinite(event.deltaY))return;event.preventDefault();action('zoom',Math.exp(-Math.max(-500,Math.min(500,event.deltaY))*0.002),0);},{passive:false});
  listen('scan','pointerdown',event=>{
    if(drag||event.isPrimary===false||(event.button!==undefined&&event.button!==0)||![event.clientX,event.clientY].every(Number.isFinite))return;
    if(markingFront){
      event.preventDefault();
      if(now()>=expiresAt||!lastScan||!lastScan.frame||canUseMap()){markingFront=false;repaint();return;}
      const canvas=ui('scan'),r=canvas.getBoundingClientRect();
      if(!(r.width>0&&r.height>0))return;
      const point=[(event.clientX-r.left)*canvas.width/r.width,(event.clientY-r.top)*canvas.height/r.height];
      const yaw=geometry.headingFromPoint(view,point,canvas.width,canvas.height);
      if(yaw!==null){manualFront={frame:lastScan.frame,yaw};markingFront=false;followFront=true;}
      repaint();return;
    }
    event.preventDefault();drag={id:event.pointerId,x:event.clientX,y:event.clientY};
    try{ui('scan').setPointerCapture(event.pointerId);}catch(_){drag=null;}
  });
  listen('scan','pointermove',event=>{
    if(!drag||drag.id!==event.pointerId||![event.clientX,event.clientY].every(Number.isFinite))return;
    event.preventDefault();const dx=event.clientX-drag.x,dy=event.clientY-drag.y;drag.x=event.clientX;drag.y=event.clientY;
    action(view.tool==='pan'?'pan':'orbit',view.tool==='pan'?dx:dx*.008,view.tool==='pan'?dy:dy*.008);
  });
  for(const name of ['pointerup','pointercancel','lostpointercapture'])listen('scan',name,event=>{
    if(!drag||drag.id!==event.pointerId)return;drag=null;
    if(name==='pointerup'&&ui('scan').hasPointerCapture&&ui('scan').hasPointerCapture(event.pointerId))ui('scan').releasePointerCapture(event.pointerId);
  });
  function validPose(p){return p&&[p.x,p.y,p.yaw].every(Number.isFinite);}
  function viewLabel(front,usingMap){
    if(zoomLabel)zoomLabel.textContent=view.zoom.toFixed(2)+'× · '+(fixedMap&&usingMap?'FIXED MAP':followFront&&front?'FRONT UP · '+front.source:(view.pitch?'3D view / flat data':'Top view')+' · '+view.tool);
    const pan=ui('scene-pan');if(pan&&typeof pan.setAttribute==='function')pan.setAttribute('aria-pressed',String(view.tool==='pan'));
    const button=ui('scene-front');if(button&&typeof button.setAttribute==='function')button.setAttribute('aria-pressed',String(followFront&&!(fixedMap&&usingMap)));
    const mapButton=ui('scene-map');if(mapButton&&typeof mapButton.setAttribute==='function')mapButton.setAttribute('aria-pressed',String(fixedMap));
    const mark=ui('scene-mark-front');if(mark){mark.textContent=markingFront?'Click towards the nose…':'Mark front';mark.disabled=now()>=expiresAt||!lastScan||!lastScan.frame||canUseMap();}
    const clear=ui('scene-clear-front');if(clear)clear.disabled=!manualFront;
    const flip=ui('scene-flip-front');if(flip)flip.disabled=now()>=expiresAt||!lastScan||canUseMap()||validPose(lastScan.robot_pose)||(!manualFront&&!reportedFront(lastScan));
    const note=ui('scene-heading');if(note)note.textContent=markingFront?'With driving disabled, click away from the centre towards the physical nose. Display only—not calibration.':
      fixedMap&&usingMap?'Fixed room/grid view: car moves only from fresh map body TF. No SLAM or map saving is started by this button.':
      front?(fixedMap?'No /map: current scan fallback, NOT a growing room map. ':'')+(front.source==='manual mark'?'FRONT = operator mark at laser origin, not a measured body pose.':front.source==='reported preset'?'FRONT = reported-direction display preset; unverified mounting. Flip front corrects it.':'FRONT = body +X from fresh TF. Icon is not the footprint.')+(followFront?' Nose stays up; approaching obstacles move down.':' Free view; Front-up restores nose-up.'):
      'Front unknown: use Mark front on a fresh scan, or supply verified body TF. No direction inferred from driving commands.';
  }
function renderScan(scan) {
  if(lastScan&&scan.frame!==lastScan.frame)markingFront=false;
  lastScan=scan;expiresAt=scan&&scan.available?now()+Math.max(0,2-(scan.age_s||0))*1000:0;
  if(manualFront&&scan.frame!==manualFront.frame)manualFront=null;
  const descriptions = {
    preview:['PREVIEW ONLY','No robot connected. This is not simulated LiDAR data.'],
    waiting:['CHECKING ROS','Waiting for the /scan subscriber connection and first message.'],
    no_publisher:['NO ROS CONNECTION','No /scan publisher connection. Check the LiDAR-only ROS driver; do not launch duplicates.'],
    waiting_messages:['CONNECTED · WAITING','ROS connection exists, but no scan message has arrived yet.'],
    multiple_publishers:['MULTIPLE ROS SOURCES','More than one /scan connection. Points are hidden to avoid mixing sources; inspect rostopic info /scan.'],
    live:['LIVE SCAN','Receiving valid planar scan messages. Dots show measured geometry, not object identity.'],
    no_valid_returns:['LIVE · NO VALID RANGES','Scan messages are arriving, but none of the current ranges are finite and within the message limits.'],
    invalid:['INVALID SCAN',scan.error || 'Messages arrived but LaserScan geometry or ranges could not be processed.'],
    stale:['STALE SCAN','No recent valid scan. Old points are hidden; check the ROS LiDAR driver and data stream.'],
    disconnected:['UNKNOWN','Dashboard disconnected. ROS connection/data state is unknown; old points are hidden.']
  };
  const state = scan.state || (scan.available ? 'live' : 'waiting');
  const description = descriptions[state] || descriptions.waiting;
  pill('scan-state', description[0], state==='live' ? 'ok' : state==='preview' ? '' : 'warn');
  ui('scan-health').textContent = description[0];
  ui('scan-note').textContent = description[1];
  ui('scan-topic').textContent = scan.topic || '/scan';
  ui('scan-connections').textContent = Number.isInteger(scan.publisher_connections) ? String(scan.publisher_connections) : '—';
  ui('scan-publisher').textContent = scan.available && scan.publisher ? scan.publisher : '—';
  ui('scan-rate').textContent = Number.isFinite(scan.arrival_rate_hz) ? scan.arrival_rate_hz.toFixed(1)+' Hz' : '—';
  ui('scan-messages').textContent = Number.isInteger(scan.messages_received) ? String(scan.messages_received) : '—';
  ui('scan-minimum').textContent = scan.available && Number.isFinite(scan.minimum_m) ? scan.minimum_m.toFixed(2)+' m' : '— m';
  ui('scan-age').textContent = seconds(scan.last_message_age_s === undefined ? scan.age_s : scan.last_message_age_s);
  ui('scan-count').textContent = scan.available ? scan.valid_samples+' / '+scan.samples : '—';
  ui('scan-frame').textContent = scan.available ? scan.frame : '—';
  drawScan(scan);
}
function drawScan(scan) {
  const canvas = ui('scan');
  // Match the drawing buffer to the panel, rather than stretching a fixed
  // 640x360 bitmap. Keep identical metric scale horizontally and vertically.
  if(canvas.clientWidth>0 && canvas.clientHeight>0){
    const width=Math.max(1,Math.min(1920,Math.round(canvas.clientWidth))),height=Math.max(1,Math.min(1080,Math.round(canvas.clientHeight)));
    if(canvas.width!==width || canvas.height!==height){canvas.width=width;canvas.height=height;}
  }
  const mapView=getMap();
  const ctx = canvas.getContext('2d'), cx = canvas.width/2, cy = canvas.height/2;
  const scale = Math.max(1,(Math.min(canvas.width,canvas.height)/2 - 24)/4);
  ctx.clearRect(0,0,canvas.width,canvas.height);
  const pose=scan&&scan.available&&scan.robot_pose;
  const known=validPose(pose);
  const manual=scan&&scan.available&&manualFront&&scan.frame===manualFront.frame?manualFront:null;
  const usingMap=mapView&&mapView.available&&canUseMap();
  const mapRobot=usingMap&&mapView.overlay&&mapView.overlay.robot;
  const validMapRobot=validPose(mapRobot);
  const front=usingMap?(validMapRobot?{...mapRobot,source:'TF'}:null):known?{...pose,source:'TF'}:manual?{x:0,y:0,yaw:manual.yaw,source:'manual mark'}:reportedFront(scan);
  let displayView=view;
  if(followFront&&front&&!(fixedMap&&usingMap)){
    const anchor=usingMap?mapPixel(mapView,front.x,front.y,canvas):[cx-front.y*scale,cy-front.x*scale];
    const angle=usingMap?-(front.yaw-mapView.origin.yaw):-Math.PI/2-front.yaw;
    displayView=geometry.frontUp(view,anchor,angle,canvas.width,canvas.height);
  }
  renderView=displayView;
  viewLabel(front,usingMap);ctx.save();ctx.transform(...geometry.matrix(displayView,canvas.width,canvas.height));
  if(mapView && mapView.available && canUseMap()){drawOccupancy(mapView);ctx.restore();return;}
  if (scan && scan.available) {
    ui('scan-colour-note').textContent='SCAN ONLY · current beams, /map unavailable. Grey cells: unknown. Pale ray bins: finite-range visibility sketch, NOT guaranteed traversable or measured beam footprints. Point colour = distance from laser: red 0 m → blue 4 m. Not object classes. No saved room map.';
    ctx.fillStyle='#66747e';ctx.fillRect(0,0,canvas.width,canvas.height);
    // Subtle square unknown cells, not radar rings or invented occupancy data.
    const cell=Math.max(8,scale*0.5);
    ctx.fillStyle='#626f79';
    for(let x=0;x<canvas.width;x+=cell)for(let y=0;y<canvas.height;y+=cell)
      if((Math.floor(x/cell)+Math.floor(y/cell))%2===0)ctx.fillRect(x,y,cell,cell);
    ctx.fillStyle='#d5dcdf';
    for(const sector of observedSectors(scan)){
      const a=-Math.PI/2-sector.angle,half=sector.half;
      ctx.beginPath();
      ctx.moveTo(cx+Math.cos(a-half)*sector.inner*scale,cy+Math.sin(a-half)*sector.inner*scale);
      ctx.arc(cx,cy,sector.outer*scale,a-half,a+half);
      ctx.lineTo(cx+Math.cos(a+half)*sector.inner*scale,cy+Math.sin(a+half)*sector.inner*scale);
      if(sector.inner>0)ctx.arc(cx,cy,sector.inner*scale,a+half,a-half,true);
      ctx.closePath();ctx.fill();
    }
    for (let i=0;i<(scan.points || []).length;i++) {
      const [x,y]=scan.points[i];
      if (x*x+y*y > 256) continue;
      ctx.fillStyle=rangeColour(Math.hypot(x,y));
      ctx.beginPath(); ctx.arc(cx-y*scale,cy-x*scale,2.4,0,Math.PI*2); ctx.fill();
    }
    if (scan.valid_samples === 0) {ctx.fillStyle='#a5b6c3';ctx.textAlign='center';ctx.fillText('Receiving scans · no valid ranges',cx,cy+45);ctx.textAlign='start';}
  } else { ui('scan-colour-note').textContent='No current scan or occupancy map. No clear floor inferred.';ctx.fillStyle='#a5b6c3'; ctx.textAlign='center'; ctx.fillText('No recent laser message',cx,cy+45); ctx.textAlign='start'; }
  if(scan && scan.available){
    if(front)drawMarker(ctx,cx-front.y*scale,cy-front.x*scale,-Math.PI/2-front.yaw,front.source!=='TF');
    else {ctx.fillStyle='#d9fff0';ctx.beginPath();ctx.arc(cx,cy,5,0,Math.PI*2);ctx.fill();ctx.fillText('Laser · front unknown',cx+8,cy-12);}
  }
  ctx.restore();
  ctx.fillStyle='#e0e7eb';ctx.font='10px system-ui';ctx.fillText(known?'Car: acquisition-time body TF; icon is not footprint':front?'Illustrative car: '+front.source+' at laser origin; NOT body TF':'Laser origin only; car heading unverified without body TF',12,canvas.height-8);
}
function drawMarker(ctx,x,y,angle,manual=false){
  const canvas=ui('scan'),p=geometry.marker(renderView,[x,y],angle,canvas.width,canvas.height);
  ctx.save();ctx.setTransform(1,0,0,1,0,0);drawVehicle(ctx,p.x,p.y,p.angle,manual);ctx.restore();
}
function drawVehicle(ctx,x,y,angle,manual=false){
  ctx.save();ctx.translate(x,y);ctx.rotate(angle);
  ctx.fillStyle='rgba(255,229,152,.35)';
  for(const sy of [-12,12]){ctx.beginPath();ctx.moveTo(29,sy);ctx.lineTo(46,sy*1.5);ctx.lineTo(46,sy*.6);ctx.closePath();ctx.fill();}
  ctx.fillStyle='#080f15';
  for(const sx of [-23,13])for(const sy of [-24,16])ctx.fillRect(sx,sy,14,8);
  ctx.beginPath();ctx.moveTo(-31,-13);ctx.lineTo(-24,-19);ctx.lineTo(18,-19);ctx.quadraticCurveTo(33,-17,34,0);ctx.quadraticCurveTo(33,17,18,19);ctx.lineTo(-24,19);ctx.lineTo(-31,13);ctx.closePath();
  ctx.fillStyle='#8ad8bd';ctx.fill();ctx.strokeStyle='#173e3b';ctx.lineWidth=2;ctx.stroke();
  ctx.fillStyle='#173e4a';ctx.beginPath();ctx.moveTo(5,-15);ctx.lineTo(15,-12);ctx.lineTo(18,12);ctx.lineTo(5,15);ctx.closePath();ctx.fill();
  ctx.fillStyle='#315c63';ctx.fillRect(-19,-12,9,24);ctx.fillStyle='#b5f0d9';ctx.fillRect(-8,-13,11,26);
  ctx.strokeStyle='#417b69';ctx.beginPath();ctx.moveTo(21,-10);ctx.lineTo(24,10);ctx.stroke();
  ctx.fillStyle='#ffe598';ctx.fillRect(29,-14,5,7);ctx.fillRect(29,7,5,7);
  ctx.fillStyle='#ff496b';ctx.fillRect(-32,-13,4,8);ctx.fillRect(-32,5,4,8);
  if(manual){ctx.strokeStyle='#ffe598';ctx.setLineDash([4,3]);ctx.strokeRect(-35,-26,72,52);}
  ctx.fillStyle='#ffffff';ctx.beginPath();ctx.moveTo(50,0);ctx.lineTo(40,-6);ctx.lineTo(40,6);ctx.closePath();ctx.fill();ctx.restore();
  ctx.save();ctx.translate(x+Math.cos(angle)*64,y+Math.sin(angle)*64);
  ctx.fillStyle='#10272c';ctx.fillRect(-23,-9,46,18);ctx.fillStyle='#ffffff';ctx.font='bold 10px system-ui';ctx.textAlign='center';ctx.fillText('FRONT',0,3);ctx.restore();
}
function mapPixel(map,x,y,canvas){
  const w=map.width,h=map.height,scale=Math.min((canvas.width-28)/w,(canvas.height-26)/h);
  const ox=(canvas.width-w*scale)/2,oy=(canvas.height-h*scale)/2;
  const dx=x-map.origin.x,dy=y-map.origin.y,c=Math.cos(map.origin.yaw),s=Math.sin(map.origin.yaw);
  return [ox+(c*dx+s*dy)/map.resolution*scale,oy+(h-(-s*dx+c*dy)/map.resolution)*scale];
}
function drawOccupancy(map){
  const canvas=ui('scan'),ctx=canvas.getContext('2d'),w=map.width,h=map.height;
  const scale=Math.min((canvas.width-28)/w,(canvas.height-26)/h),ox=(canvas.width-w*scale)/2,oy=(canvas.height-h*scale)/2;
  ctx.clearRect(0,0,canvas.width,canvas.height);ctx.fillStyle='#66747e';ctx.fillRect(ox,oy,w*scale,h*scale);
  // One cached pixel per coarse cell avoids anti-aliased seams and repeated
  // per-cell draw calls. Unknown remains grey, never painted as free floor.
  if(dom && typeof dom.createElement==='function'){
    if(!mapRaster || mapRaster.cells!==map.cells || mapRaster.w!==w || mapRaster.h!==h){
      const surface=dom.createElement('canvas');surface.width=w;surface.height=h;
      const raster=surface.getContext('2d'),pixels=raster.createImageData(w,h);
      for(let i=0;i<map.cells.length;i++){
        const v=map.cells[i],shade=v>=65?18:Math.round(242-v*2.7),j=((h-1-Math.floor(i/w))*w+i%w)*4;
        pixels.data[j]=v<0?102:shade;pixels.data[j+1]=v<0?116:shade;pixels.data[j+2]=v<0?126:shade;pixels.data[j+3]=255;
      }
      raster.putImageData(pixels,0,0);mapRaster={cells:map.cells,w,h,surface};
    }
    ctx.imageSmoothingEnabled=false;ctx.drawImage(mapRaster.surface,ox,oy,w*scale,h*scale);
  }else for(let i=0;i<map.cells.length;i++){
    const v=map.cells[i];if(v<0)continue;const shade=v>=65?18:Math.round(242-v*2.7);
    ctx.fillStyle='rgb('+shade+','+shade+','+shade+')';ctx.fillRect(ox+(i%w)*scale,oy+(h-1-Math.floor(i/w))*scale,scale+.05,scale+.05);
  }
  const origin=map.origin,pixel=(x,y)=>mapPixel(map,x,y,canvas);
  ctx.save();ctx.beginPath();ctx.rect(ox,oy,w*scale,h*scale);ctx.clip();
  const points=map.overlay && map.overlay.scan || [],ranges=map.overlay && map.overlay.scan_ranges_m || [];
  for(let i=0;i<points.length;i++){const [x,y]=points[i],p=pixel(x,y);ctx.fillStyle=rangeColour(ranges.length===points.length?ranges[i]:NaN);ctx.beginPath();ctx.arc(p[0],p[1],2,0,Math.PI*2);ctx.fill();}
  const robot=map.overlay && map.overlay.robot;
  if(robot){const p=pixel(robot.x,robot.y);drawMarker(ctx,p[0],p[1],-(robot.yaw-origin.yaw));}
  ctx.restore();
  ui('scan-colour-note').textContent='MAP '+map.frame+' · white: zero occupancy · grey: unknown · black: high occupancy. Points: laser distance, red 0 m → blue 4+ m; mint if range unavailable. Not object classes. Not guaranteed drivable. '+(robot?'Car: fresh TF pose; icon not to scale.':'Car hidden: no fresh map→base_footprint TF.')+' Snapshot '+seconds(map.age_s)+' old.';
}

  const key=ui('vehicle-key');if(key&&typeof key.getContext==='function')drawVehicle(key.getContext('2d'),40,27,0);
  return {renderScan,drawScan,drawOccupancy,action,viewState:()=>({...view,followFront,fixedMap,markingFront,manualFront:manualFront&&{...manualFront}}),reset:()=>{mapRaster=null;lastScan=null;expiresAt=0;drag=null;manualFront=null;markingFront=false;followFront=true;fixedMap=true;renderView=geometry.initial();}};
}
const api={create,rangeColour,observedSectors};
if(typeof module!=='undefined' && module.exports)module.exports=api;
if(root)root.FahadSensorView=api;
})(typeof window!=='undefined'?window:null);
