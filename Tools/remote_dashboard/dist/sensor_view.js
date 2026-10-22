/* Reusable read-only scan/map renderer. No fetch, timers, ROS or drive access. */
(function(root){
  'use strict';
function rangeColour(distance){
  return Number.isFinite(distance) && distance>=0?'hsl('+Math.round(Math.min(1,distance/4)*240)+',90%,65%)':'#8ad8bd';
}

function create(options){
  const {ui,pill,seconds,getMap,canUseMap,document:dom}=options;
  let mapRaster=null;
function renderScan(scan) {
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
  const mapView=getMap();
  if(mapView && mapView.available && canUseMap()){drawOccupancy(mapView);return;}
  const canvas = ui('scan'), ctx = canvas.getContext('2d'), cx = canvas.width/2, cy = canvas.height/2;
  const scale = (canvas.height/2 - 24)/4;
  ctx.clearRect(0,0,canvas.width,canvas.height);
  if (scan && scan.available) {
    ui('scan-colour-note').textContent='SCAN ONLY · /map unavailable. Point colour = distance from laser: red 0 m → blue 4 m. Blank = unknown, not clear floor. Not object classes.';
    for (let i=0;i<(scan.points || []).length;i++) {
      const [x,y]=scan.points[i];
      if (x*x+y*y > 16) continue;
      ctx.fillStyle=rangeColour(Math.hypot(x,y));
      ctx.beginPath(); ctx.arc(cx-y*scale,cy-x*scale,2.4,0,Math.PI*2); ctx.fill();
    }
    if (scan.valid_samples === 0) {ctx.fillStyle='#a5b6c3';ctx.textAlign='center';ctx.fillText('Receiving scans · no valid ranges',cx,cy+45);ctx.textAlign='start';}
  } else { ui('scan-colour-note').textContent='No current scan or occupancy map. No clear floor inferred.';ctx.fillStyle='#a5b6c3'; ctx.textAlign='center'; ctx.fillText('No recent laser message',cx,cy+45); ctx.textAlign='start'; }
  drawVehicle(ctx,cx,cy,-Math.PI/2);
  ctx.fillStyle='#a5b6c3';ctx.font='10px system-ui';ctx.fillText('Illustrative icon at laser origin · not footprint',12,canvas.height-8);
}
function drawVehicle(ctx,x,y,angle){
  ctx.save();ctx.translate(x,y);ctx.rotate(angle);ctx.fillStyle='#0a1116';
  for(const sx of [-10,7])for(const sy of [-12,8])ctx.fillRect(sx,sy,7,4);
  ctx.fillStyle='#8ad8bd';ctx.fillRect(-14,-8,28,16);ctx.fillStyle='#234f4b';ctx.fillRect(0,-6,8,12);
  ctx.fillStyle='#edf9f4';ctx.fillRect(12,-6,3,4);ctx.fillRect(12,2,3,4);ctx.restore();
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

  return {renderScan,drawScan,drawOccupancy,reset:()=>{mapRaster=null;}};
}
const api={create,rangeColour};
if(typeof module!=='undefined' && module.exports)module.exports=api;
if(root)root.FahadSensorView=api;
})(typeof window!=='undefined'?window:null);
