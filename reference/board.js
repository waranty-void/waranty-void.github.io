const get = id => document.getElementById(id);
const canvas = get('board');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;
const params = new URLSearchParams(location.hash.slice(1));
const room = params.get('room') || '';
const discordRoom = /^\d{17,20}$/.test(room) ? room : '';
const draftKey = discordRoom || 'personal';
const validImage = /^data:image\/(?:png|jpeg|webp);base64,/;
const inkColor = /^#[0-9a-f]{6}$/i;
let board = {version:1, title:'', note:'', objects:[]};
let selected = -1, tool = 'move', gesture, notePoint, db, saving;
const history = [], future = [], bitmap = new Map();
const back = get('back');
if (discordRoom) {
  back.href = 'https://discord.com/channels/1575145811912826910/' + discordRoom;
  back.hidden = false;
}
function status(text) { get('status').textContent = text; clearTimeout(status.timer); status.timer = setTimeout(() => get('status').textContent = '', 3400); }
function undoPoint() {
  history.push(structuredClone(board));
  if (history.length > 20) history.shift();
  future.length = 0;
}
function store() {
  clearTimeout(saving);
  saving = setTimeout(() => {
    if (!db) return;
    try {
      const tx = db.transaction('drafts','readwrite');
      tx.objectStore('drafts').put(board,draftKey);
      tx.oncomplete = () => get('saved').textContent = 'Saved on this device';
      tx.onerror = () => get('saved').textContent = 'Use Save editable board';
    } catch { get('saved').textContent = 'Use Save editable board'; }
  }, 250);
}
function selectTool(name) {
  tool = name;
  for (const el of document.querySelectorAll('[data-tool]')) el.setAttribute('aria-pressed',String(el.dataset.tool === name));
  get('tool-hint').textContent = {move:'Drag a pin to move it. Select it to resize or remove it.',arrow:'Drag from the tail toward the detail you want to point out.',pen:'Draw a line with your mouse, pen or finger.',note:'Tap the board where the note should go.'}[tool];
}
function paper() {
  ctx.fillStyle='#c7a575'; ctx.fillRect(0,0,W,H);
  ctx.fillStyle='#a98b60'; for (let y=12;y<H;y+=24) for(let x=12;x<W;x+=24) ctx.fillRect(x,y,2,2);
}
function line(points,color,width) {
  if(!points.length) return;
  ctx.beginPath();ctx.moveTo(...points[0]);for(const p of points.slice(1))ctx.lineTo(...p);
  ctx.strokeStyle=color;ctx.lineWidth=width;ctx.lineCap='round';ctx.lineJoin='round';ctx.stroke();
}
function pinHead(x,y) {
  ctx.beginPath();ctx.arc(x,y+2,6,0,Math.PI*2);ctx.fillStyle='#70402f';ctx.fill();
  ctx.beginPath();ctx.arc(x,y,5.5,0,Math.PI*2);ctx.fillStyle='#e56543';ctx.fill();
}
function decoded(src) {
  if (bitmap.has(src)) return bitmap.get(src);
  const entry = {image:null, ready:null};
  bitmap.set(src,entry);
  entry.ready = (async () => {
    const comma = src.indexOf(','), binary = atob(src.slice(comma+1));
    const bytes = Uint8Array.from(binary, c => c.charCodeAt(0));
    const blob = new Blob([bytes], {type:src.slice(5,src.indexOf(';'))});
    entry.image = await createImageBitmap(blob);
  })().catch(() => { status('One photo could not be decoded. Replace it before exporting.'); })
    .finally(() => draw());
  return entry;
}
function paint(o) {
  if(o.type==='photo'||o.type==='note'){
    ctx.save(); ctx.shadowColor='#3f301d66';ctx.shadowBlur=11;ctx.shadowOffsetY=5;
    ctx.fillStyle=o.type==='photo'?'#fffdf4':'#fff0ac';ctx.fillRect(o.x-5,o.y-5,o.w+10,o.h+10);ctx.restore();
    if(o.type==='photo'){
      const im=decoded(o.src).image;
      if(im)ctx.drawImage(im,o.x,o.y,o.w,o.h);
    } else {
      const font=Math.min(40,Math.max(18,o.w/12));ctx.fillStyle='#332f23';ctx.font='600 '+font+'px system-ui';
      const words=o.text.split(/\s+/);let s='',y=o.y+font+14;
      for(const word of words){
        if(s&&ctx.measureText(s+' '+word).width>o.w-24){ctx.fillText(s,o.x+12,y,o.w-24);y+=font*1.3;s='';}
        s+=(s?' ':'')+word;
      }
      if(s)ctx.fillText(s,o.x+12,y,o.w-24);
    }
    pinHead(o.x+o.w/2,o.y+5);
  }else{
    const pts=o.points;line(pts,'#fff8e7',11);line(pts,o.ink,6);
    if(o.type==='arrow'&&pts.length>=2){
      const [a,b]=[pts[0],pts.at(-1)],ang=Math.atan2(b[1]-a[1],b[0]-a[0]);
      const head=[-.48,.48].map(v=>[b[0]-26*Math.cos(ang+v),b[1]-26*Math.sin(ang+v)]);
      line([head[0],b,head[1]],'#fff8e7',11);line([head[0],b,head[1]],o.ink,6);
    }
  }
}
function bounds(o) {
  if(o.type==='photo'||o.type==='note')return [o.x,o.y,o.x+o.w,o.y+o.h];
  const xs=o.points.map(p=>p[0]),ys=o.points.map(p=>p[1]);
  return [Math.min(...xs)-10,Math.min(...ys)-10,Math.max(...xs)+10,Math.max(...ys)+10];
}
function draw(showSelection=true) {
  paper();board.objects.forEach(paint);
  const o=board.objects[selected];
  if(showSelection&&o&&tool==='move'){
    const [x,y,x2,y2]=bounds(o);ctx.save();ctx.strokeStyle='#1e5949';ctx.lineWidth=3;ctx.setLineDash([8,5]);ctx.strokeRect(x-8,y-8,x2-x+16,y2-y+16);ctx.restore();
  }
  get('count').textContent=board.objects.length+' '+(board.objects.length===1?'item':'items');
  get('empty').hidden=!!board.objects.length;
  get('undo').disabled=!history.length;get('redo').disabled=!future.length;get('remove').disabled=!o;
  for(const id of ['bigger','smaller'])get(id).disabled=!o||!['photo','note'].includes(o.type);
  get('download').disabled=!board.objects.length||board.objects.some(o=>o.type==='photo'&&!decoded(o.src).image);get('copy').disabled=!board.note.trim()&&!board.title.trim();
  get('board-title').textContent=board.title.trim()||'Untitled board';
}
function syncFields(){get('title').value=board.title;get('note').value=board.note;selected=-1;gesture=null;draw();}
function point(e){const r=canvas.getBoundingClientRect();return [Math.max(0,Math.min(W,(e.clientX-r.left)*W/r.width)),Math.max(0,Math.min(H,(e.clientY-r.top)*H/r.height))];}
function hit(p){
  return board.objects.findLastIndex(o=>{
    const [x,y,r,b]=bounds(o);
    if(p[0]<x-5||p[0]>r+5||p[1]<y-5||p[1]>b+5)return false;
    if(!o.points)return true;
    return o.points.some((v,i)=>{const a=o.points[Math.max(0,i-1)],dx=v[0]-a[0],dy=v[1]-a[1];const t=Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy||1)));return Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)<19;});
  });
}
function move(o,dx,dy){if(o.points)o.points=o.points.map(([x,y])=>[x+dx,y+dy]);else{o.x+=dx;o.y+=dy;}}
canvas.onpointerdown=e=>{
  if(e.button!==0||gesture)return;
  const p=point(e);
  if(tool==='note'){notePoint=p;get('sticky').value='';get('sticky-dialog').showModal();get('sticky').focus();return;}
  if(tool==='move'){selected=hit(p);if(selected<0){draw();return;}undoPoint();}
  else{if(board.objects.length>=64){status('This board holds up to 64 pins and marks.');return;}undoPoint();board.objects.push({type:tool,ink:get('ink').value,points:[p,p]});selected=board.objects.length-1;}
  gesture={pointer:e.pointerId,prev:p};canvas.setPointerCapture(e.pointerId);draw();
};
canvas.onpointermove=e=>{
  if(!gesture||gesture.pointer!==e.pointerId)return;
  const p=point(e),o=board.objects[selected];
  if(tool==='move')move(o,p[0]-gesture.prev[0],p[1]-gesture.prev[1]);
  else if(tool==='arrow')o.points[1]=p;else if(o.points.length<5000)o.points.push(p);
  gesture.prev=p;draw();
};
function finish(e){if(gesture?.pointer===e.pointerId){gesture=null;store();draw();}}
canvas.onpointerup=finish;canvas.onpointercancel=finish;
get('sticky-dialog').onclose=()=>{
  const text=get('sticky').value.trim();
  if(get('sticky-dialog').returnValue!=='default'||!text||!notePoint)return;
  if(board.objects.length>=64){status('This board holds up to 64 pins and marks.');return;}
  undoPoint();board.objects.push({type:'note',text,x:Math.min(notePoint[0],W-290),y:Math.min(notePoint[1],H-162),w:275,h:150});
  selected=board.objects.length-1;selectTool('move');draw();store();
};
for(const el of document.querySelectorAll('[data-tool]'))el.onclick=()=>{selectTool(el.dataset.tool);draw();};
for(const id of ['title','note']) {get(id).onfocus=()=>undoPoint();get(id).oninput=e=>{board[id]=e.target.value;draw();store();};}
async function addFiles(files){
  const ok=[...files].filter(f=>['image/png','image/jpeg','image/webp'].includes(f.type));
  if(!ok.length){status('Choose PNG, JPEG or WebP images.');return;}
  if(ok.length+board.objects.filter(o=>o.type==='photo').length>10||ok.length+board.objects.length>64){status('Use up to ten photos per board.');return;}
  undoPoint();
  for(const file of ok){
    if(file.size>20*1024*1024){status('Choose an image smaller than 20 MB.');continue;}
    let bmp;
    try{bmp=await createImageBitmap(file);}catch{status('This image could not be opened.');continue;}
    const scale=Math.min(1,1440/Math.max(bmp.width,bmp.height)),im=document.createElement('canvas');
    im.width=Math.max(1,Math.round(bmp.width*scale));im.height=Math.max(1,Math.round(bmp.height*scale));const ic=im.getContext('2d');ic.fillStyle='#fff';ic.fillRect(0,0,im.width,im.height);ic.drawImage(bmp,0,0,im.width,im.height);bmp.close();
    const fit=Math.min(970/im.width,740/im.height,1.6),w=im.width*fit,h=im.height*fit,offset=board.objects.filter(o=>o.type==='photo').length*38;
    board.objects.push({type:'photo',src:im.toDataURL('image/webp',.91),x:Math.min(W-w-15,(W-w)/2+offset),y:Math.min(H-h-15,(H-h)/2+offset),w,h});
    selected=board.objects.length-1;
  }
  selectTool('move');draw();store();
}
for(const k of ['add','add-empty'])get(k).onclick=()=>get('files').click();
get('files').onchange=e=>{void addFiles(e.target.files);e.target.value='';};
canvas.parentElement.ondragover=e=>e.preventDefault();canvas.parentElement.ondrop=e=>{e.preventDefault();void addFiles(e.dataTransfer.files);};
document.addEventListener('paste',e=>{if(e.clipboardData.files.length){e.preventDefault();void addFiles(e.clipboardData.files);}});
function undoRedo(from,to){if(!from.length)return;to.push(board);board=from.pop();syncFields();store();}
get('undo').onclick=()=>undoRedo(history,future);get('redo').onclick=()=>undoRedo(future,history);
get('remove').onclick=()=>{if(selected<0)return;undoPoint();board.objects.splice(selected,1);selected=-1;draw();store();};
for(const [id,k] of [['bigger',1.14],['smaller',1/1.14]])get(id).onclick=()=>{
  const o=board.objects[selected];if(!o||!('w' in o))return;undoPoint();
  const f=Math.max(45/o.w,Math.min(k,W/o.w,H/o.h));o.w*=f;o.h*=f;draw();store();
};
document.addEventListener('keydown',e=>{if(e.target.matches('input,textarea')||get('sticky-dialog').open)return;
  if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'){e.preventDefault();(e.shiftKey?get('redo'):get('undo')).click();}
  if(e.key==='Delete'||e.key==='Backspace'){e.preventDefault();get('remove').click();}
});
function download(blob,suffix){const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download=(board.title.trim().replace(/[^a-z0-9-]+/gi,'-').slice(0,60)||'reference-board')+suffix;a.click();setTimeout(()=>URL.revokeObjectURL(url),15000);}
get('download').onclick=()=>{draw(false);canvas.toBlob(blob=>{draw();if(blob){download(blob,'.png');status('Board image saved. Attach it with Write a pin in Discord.');}},'image/png');};
get('copy').onclick=async()=>{try{await navigator.clipboard.writeText('**'+(board.title.trim()||'Project reference')+'**\n'+board.note.trim());status('Copied. Paste into Discord to post from your profile.');}catch{get('note').select();status('Select and copy your note.');}};
get('save-edit').onclick=()=>download(new Blob([JSON.stringify(board)],{type:'application/json'}),'.wvboard');
get('load-edit').onclick=()=>get('load-json').click();
function checked(data){
  const finite=n=>Number.isFinite(n)&&Math.abs(n)<=20000;
  const coord=p=>Array.isArray(p)&&p.length===2&&p.every(finite);
  if(data?.version!==1||typeof data.title!=='string'||typeof data.note!=='string'||!Array.isArray(data.objects)||data.objects.length>64)throw Error();
  const objects=data.objects.map(o=>{
    if(o.type==='photo'||o.type==='note'){
      if(![o.x,o.y,o.w,o.h].every(finite)||o.w<=0||o.h<=0)throw Error();
      if(o.type==='photo'&&(typeof o.src!=='string'||!validImage.test(o.src)||o.src.length>6e6))throw Error();
      if(o.type==='note'&&(typeof o.text!=='string'||o.text.length>130))throw Error();
      return {type:o.type,x:o.x,y:o.y,w:o.w,h:o.h,...(o.type==='note'?{text:o.text}:{src:o.src})};
    }
    if(!['arrow','pen'].includes(o.type)||!inkColor.test(o.ink)||!Array.isArray(o.points)||!o.points.length||o.points.length>5000||!o.points.every(coord))throw Error();
    return {type:o.type,ink:o.ink,points:o.points};
  });
  return {version:1,title:data.title.slice(0,70),note:data.note.slice(0,900),objects};
}
get('load-json').onchange=async e=>{try{const f=e.target.files[0];if(!f||f.size>25e6)throw Error();const next=checked(JSON.parse(await f.text()));undoPoint();board=next;syncFields();store();}catch{status('Choose a supported editable board under 25 MB.');}e.target.value='';};
draw();
try{
  const req=indexedDB.open('warranty-void-reference',1);req.onupgradeneeded=()=>req.result.createObjectStore('drafts');
  req.onsuccess=()=>{db=req.result;const q=db.transaction('drafts').objectStore('drafts').get(draftKey);q.onsuccess=()=>{if(q.result&&!history.length){try{board=checked(q.result);syncFields();get('saved').textContent='Saved on this device';}catch{status('Your saved board could not be read.');}}};};
}catch{get('saved').textContent='Use Save editable board';}
