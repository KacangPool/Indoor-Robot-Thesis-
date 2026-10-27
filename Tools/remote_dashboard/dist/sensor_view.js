/* Reusable read-only scan/map renderer. No fetch, timers, ROS or drive access. */
(function(root){
  'use strict';
const geometry=typeof module!=='undefined'&&module.exports?require('./scene_geometry.js'):root.FahadSceneGeometry;
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
  const zoomLabel=ui('scene-zoom');
  function repaint(){drawScan(now()<expiresAt?lastScan:{available:false});}
  function action(name,x,y){view=geometry.update(view,name,x,y);repaint();}
  function listen(id,event,handler,opts){const node=ui(id);if(node&&typeof node.addEventListener==='function')node.addEventListener(event,handler,opts);}
  for(const [id,operation,x] of [['scene-zoom-in','zoom',1.25],['scene-zoom-out','zoom',0.8],['scene-reset','reset',0],['scene-orbit','oblique',0]])
    listen(id,'click',()=>action(operation,x,0));
  listen('scene-pan','click',()=>action('tool',view.tool==='pan'?0:1,0));
  listen('scan','wheel',event=>{if(!Number.isFinite(event.deltaY))return;event.preventDefault();action('zoom',Math.exp(-Math.max(-500,Math.min(500,event.deltaY))*0.002),0);},{passive:false});
  listen('scan','pointerdown',event=>{
    if(drag||event.isPrimary===false||(event.button!==undefined&&event.button!==0)||![event.clientX,event.clientY].every(Number.isFinite))return;
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
  function viewLabel(){
    if(zoomLabel)zoomLabel.textContent=view.zoom.toFixed(2)+'× · '+(view.pitch?'3D view / flat data':'Top view')+' · '+view.tool;
    const pan=ui('scene-pan');if(pan&&typeof pan.setAttribute==='function')pan.setAttribute('aria-pressed',String(view.tool==='pan'));
  }
function renderScan(scan) {
  lastScan=scan;expiresAt=scan&&scan.available?now()+Math.max(0,2-(scan.age_s||0))*1000:0;
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
  viewLabel();ctx.save();ctx.transform(...geometry.matrix(view,canvas.width,canvas.height));
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
    ctx.fillStyle='#123e38';ctx.fillRect(cx-5,cy-5,10,10);
    ctx.fillStyle='#d9fff0';ctx.font='11px system-ui';ctx.fillText('+X laser',cx+8,cy-12);
    ctx.fillText('+Y',cx-37,cy+16);
    const robot=scan.robot_pose;
    if(robot&&[robot.x,robot.y,robot.yaw].every(Number.isFinite))drawVehicle(ctx,cx-robot.y*scale,cy-robot.x*scale,-Math.PI/2-robot.yaw);
  }
  ctx.restore();
  const pose=scan&&scan.available&&scan.robot_pose;
  const known=pose&&[pose.x,pose.y,pose.yaw].every(Number.isFinite);
  ctx.fillStyle='#e0e7eb';ctx.font='10px system-ui';ctx.fillText(known?'Car: acquisition-time body TF; icon is not footprint':'Laser origin only; car heading unverified without body TF',12,canvas.height-8);
}
function drawVehicle(ctx,x,y,angle){
  ctx.save();ctx.translate(x,y);ctx.rotate(angle);ctx.fillStyle='#0a1116';
  for(const sx of [-17,10])for(const sy of [-18,12])ctx.fillRect(sx,sy,12,6);
  ctx.fillStyle='#8ad8bd';ctx.fillRect(-22,-12,44,24);ctx.fillStyle='#234f4b';ctx.fillRect(1,-10,12,20);
  ctx.fillStyle='#ffe598';ctx.fillRect(20,-10,4,6);ctx.fillRect(20,4,4,6);ctx.restore();
  // Front is explicitly local +X, transformed by the supplied body pose.
  ctx.save();ctx.translate(x,y);ctx.rotate(angle);ctx.fillStyle='#ffffff';
  ctx.beginPath();ctx.moveTo(34,0);ctx.lineTo(27,-5);ctx.lineTo(27,5);ctx.closePath();ctx.fill();ctx.restore();
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
  const origin=map.origin,c=Math.cos(origin.yaw),s=Math.sin(origin.yaw);
  const pixel=(x,y)=>{const dx=x-origin.x,dy=y-origin.y;return [ox+(c*dx+s*dy)/map.resolution*scale,oy+(h-(-s*dx+c*dy)/map.resolution)*scale];};
  ctx.save();ctx.beginPath();ctx.rect(ox,oy,w*scale,h*scale);ctx.clip();
  const points=map.overlay && map.overlay.scan || [],ranges=map.overlay && map.overlay.scan_ranges_m || [];
  for(let i=0;i<points.length;i++){const [x,y]=points[i],p=pixel(x,y);ctx.fillStyle=rangeColour(ranges.length===points.length?ranges[i]:NaN);ctx.beginPath();ctx.arc(p[0],p[1],2,0,Math.PI*2);ctx.fill();}
  const robot=map.overlay && map.overlay.robot;
  if(robot){const p=pixel(robot.x,robot.y);drawVehicle(ctx,p[0],p[1],-(robot.yaw-origin.yaw));}
  ctx.restore();
  ui('scan-colour-note').textContent='MAP '+map.frame+' · white: zero occupancy · grey: unknown · black: high occupancy. Points: laser distance, red 0 m → blue 4+ m; mint if range unavailable. Not object classes. Not guaranteed drivable. '+(robot?'Car: fresh TF pose; icon not to scale.':'Car hidden: no fresh map→base_footprint TF.')+' Snapshot '+seconds(map.age_s)+' old.';
}

  const key=ui('vehicle-key');if(key&&typeof key.getContext==='function')drawVehicle(key.getContext('2d'),32,27,0);
  return {renderScan,drawScan,drawOccupancy,action,viewState:()=>({...view}),reset:()=>{mapRaster=null;lastScan=null;expiresAt=0;drag=null;}};
}
const api={create,rangeColour,observedSectors};
if(typeof module!=='undefined' && module.exports)module.exports=api;
if(root)root.FahadSensorView=api;
})(typeof window!=='undefined'?window:null);
