/* GeoImpact KZ v0.5: interactive orthographic 3D globe, channel-aware impact dossiers.
   Globe uses locally hosted Natural Earth polygons. No map tiles or API key. */
(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const tone = {positive:{color:"#189968",klass:"green",label:"Positive"},negative:{color:"#d64c53",klass:"red",label:"Negative"},critical:{color:"#26303c",klass:"dark",label:"Critical"},neutral:{color:"#407fdc",klass:"blue",label:"Neutral"},unknown:{color:"#8291a4",klass:"grey",label:"Unknown"},mixed:{color:"#9b7c70",klass:"mixed",label:"Mixed"}};
  const KZ = [48,67];
  const memory = {mode:"live",events:[],history:[],scenario:[],atlas:{assets:[],links:[],owners:[]},reports:{},world:[],status:null,selection:null,worldError:false};
  const defaultContext=[
    {label:"EIA — world oil transit chokepoints",url:"https://www.eia.gov/international/content/analysis/special_topics/World_Oil_Transit_Chokepoints/",role:"Structural background, not verification of a news article"},
    {label:"IMF — Kazakhstan economic outlook (2026)",url:"https://www.imf.org/en/news/articles/2026/06/15/pr26207-kazakhstan-imf-staff-concludes-visit",role:"Economic transmission background; not event-specific evidence"}
  ];
  const demo={
    id:"scenario-hormuz",title:"Illustrative scenario: Hormuz disruption and Kazakhstan's oil-price exposure",
    summary:"A shipping or supply disruption near the Strait of Hormuz could affect global crude prices and maritime insurance. Effects on Kazakhstan depend on observed price movements, export volumes, fiscal rules, exchange-rate responses and cost pass-through. This is a demonstration of the two-channel logic, not a claim that an actual disruption caused these outcomes.",
    published:null,source:"Analytical scenario · EIA / IMF background",url:defaultContext[0].url,region:"MENA",country:"Strait of Hormuz",
    lat:26.6,lon:56.3,sector:"Oil",direction:"Mixed",overall_effect:"mixed",scenario:true,verification:"Illustrative scenario · not an observed event",event_type:"Systemic market channel",tier:"Scenario",
    reason:"Oil-price mechanism between a globally important maritime chokepoint and Kazakhstan's commodity-export exposure",
    matches:[],market_evidence:defaultContext,impact_summary:"No net positive or negative assessment is justified without information about the price move, Kazakhstan's realized oil price, inflation pass-through and policy response.",
    impact_channels:[
      {id:"rev",direction:"positive",label:"Oil export earnings",severity:null,condition:"If global and Kazakhstan realized export prices rise and export volumes are maintained",mechanism:"Higher export prices may increase producer receipts and oil-linked government revenue, although tax rules and contracts determine the amount.",affected:["Oil producers","Fiscal receipts / National Fund"],evidence_status:"conditional pathway",source_links:[defaultContext[1]]},
      {id:"cost",direction:"negative",label:"Imported costs and inflation",severity:null,condition:"If global energy or freight prices rise and are transmitted to Kazakhstan",mechanism:"Higher global prices can increase costs for imports, transport and firms; household effects depend on fuel regulation, exchange rates and pricing.",affected:["Importers","Transport services","Households"],evidence_status:"conditional pathway",source_links:[defaultContext[0]]}
    ]
  };
  memory.scenario=[demo];
  memory.history=[
    {id:"history-grid",title:"January 2022 cross-border grid disruption",summary:"A power-system fault in Uzbekistan propagated through interconnected networks; KEGOC reported load shedding in southern Kazakhstan. Recorded electricity interruptions do not establish a monetary estimate of economic losses.",country:"Uzbekistan",lat:41,lon:64,sector:"Electricity",region:"Central Asia",source:"KEGOC",published:"2022-01-25T06:00:00Z",direction:"Negative",reason:"Synchronous regional electricity network and North–South transmission constraints",verification:"Historical operator documentation",url:"https://www.kegoc.kz/",matches:[{asset:"KEGOC national power grid",asset_id:"CA-023",source_url:"https://www.kegoc.kz/"}],impact_channels:[{id:"grid",label:"Electrical continuity",direction:"negative",severity:null,evidence_status:"Observed domestic interruption; precise impacts unresolved",mechanism:"A regional disturbance can produce overloads and emergency load shedding within connected grids.",affected:["Southern Kazakhstan electricity users"],source_links:[{label:"KEGOC — system operator",url:"https://www.kegoc.kz/",role:"Operator documentation"}]}]},
    {id:"history-cpc",title:"February 2025 CPC Kropotkinskaya station attack",summary:"The CPC operator reported a pumping-station outage and bypass. The incident affected infrastructure serving Kazakhstan-origin oil, but an incident-specific national export or fiscal loss was not established.",country:"Russia",lat:45.5,lon:40.6,sector:"Oil",region:"Russia/Eurasia",source:"CPC operator",published:"2025-02-17T08:00:00Z",direction:"Unknown",reason:"Kazakhstan crude uses CPC transport infrastructure located in Russia",verification:"Historical operator documentation",url:"https://www.cpc.ru/en/",matches:[{asset:"Caspian Pipeline Consortium",asset_id:"CA-001",source_url:"https://www.cpc.ru/en/"}],impact_channels:[{id:"transport",label:"Oil export transport",direction:"negative",severity:null,evidence_status:"Technical disruption observed; export loss not established",mechanism:"Reduced operating capability may limit exports if bypass and spare transport capacity cannot maintain shipments.",affected:["Oil producers","Export logistics"],source_links:[{label:"CPC operator disclosures",url:"https://www.cpc.ru/en/",role:"Operator background"}]}]}
  ];

  function normalizeDirection(raw) {
    let v=String(raw||"unknown").toLowerCase().trim();
    if(v.includes("mix"))return "mixed";
    if(v.includes("critical")||v.includes("awful"))return "critical";
    if(v.includes("negative"))return "negative";
    if(v.includes("positive"))return "positive";
    if(v.includes("neutral"))return "neutral";
    return "unknown";
  }
  function direction(event){return normalizeDirection(event.overall_effect && event.overall_effect!=="unknown" ? event.overall_effect:event.direction);}
  function daysOld(event){return event.published?Math.max(0,(Date.now()-Date.parse(event.published))/864e5):999;}
  function isFresh(event){return daysOld(event)<=2;}
  function candidateSources(event){
    let out=[],set=new Set();
    const add=(label,url,role)=>{
      if(!url||!/^https?:\/\//.test(url)||set.has(url))return;
      set.add(url);out.push({label,url,role});
    };
    if(event.url)add(event.source||"Article / event reporting",event.url,"News or official reporting; inspect original");
    const report=memory.reports[event.id];
    for(let s of report?.independent_reporting_leads||[])add(s.publisher||s.title,s.url,"Similar reporting lead; may be syndicated");
    for(let s of report?.original_source_leads||[])add(s.title,s.url,"Possible official-domain search result; not yet verified");
    for(let s of (event.matches||[]).slice(0,4))add(s.asset_id+" — "+s.asset,s.source_url,"Atlas background for asset relationship");
    for(let s of event.other_sources||[])add(s.label,s.url,s.role||"Inspected background or original reporting");
    for(let s of event.market_evidence||[])add(s.label,s.url,s.role||"Economic background — not proof of the event");
    for(let c of event.impact_channels||[])for(let s of c.source_links||[])add(s.label,s.url,s.role||"Background mechanism");
    return out;
  }
  function shortText(x,n=145){x=String(x||"");return x.length>n?x.slice(0,n-1)+"…":x;}
  const make=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
  function clear(e){e.replaceChildren();}
  function sourceLink(parent,s){
    const a=make("a","",s.label+" ↗");a.href=s.url;a.target="_blank";a.rel="noopener noreferrer";
    const note=make("small","",s.role||"Source link");
    a.append(note);parent.append(a);
  }
  function statusPill(state){const dir=normalizeDirection(state);return make("span","pill "+tone[dir].klass,tone[dir].label);}
  function currentItems(){return memory.mode==="live"?memory.events:memory.mode==="historical"?memory.history:memory.mode==="scenario"?memory.scenario:memory.atlas.assets;}
  function allSectors(){return [...new Set(memory.events.concat(memory.history,memory.scenario).map(e=>e.sector).filter(Boolean))].sort();}
  function allRegions(){return [...new Set(memory.events.concat(memory.history,memory.scenario).map(e=>e.region).filter(Boolean))].sort();}
  function allCountries(){return [...new Set(memory.events.concat(memory.history,memory.scenario).map(e=>e.country).filter(Boolean))].sort();}
  function fillOptions(id,options){
    const e=$(id),existing=e.value;
    while(e.options.length>1)e.remove(1);
    for(const o of options){const opt=document.createElement("option");opt.value=o;opt.textContent=o;e.add(opt);}
    e.value=[...e.options].some(x=>x.value===existing)?existing:"";
  }
  function fillFilters(){fillOptions("sector",allSectors());fillOptions("region",allRegions());fillOptions("country",allCountries());}
  function filterEvents(){
    const q=$("search").value.trim().toLowerCase(),sec=$("sector").value,region=$("region").value,country=$("country").value,eff=$("effect").value,days=Number($("window").value),item=currentItems();
    return item.filter(e=>{
      if(memory.mode==="atlas")return (!sec||e.sector===sec)&&(!q||[e.name,e.external_counterpart,e.id,e.sector].join(" ").toLowerCase().includes(q));
      if(memory.mode==="live"&&daysOld(e)>days)return false;
      return (!sec||e.sector===sec)&&(!region||e.region===region)&&(!country||e.country===country)&&(!eff||direction(e)===eff)&&(!q||[e.title,e.summary,e.sector,e.region,e.country,(e.matches||[]).map(x=>x.asset).join(" ")].join(" ").toLowerCase().includes(q));
    });
  }
  function setMode(m){
    memory.mode=m;for(const [id,key] of [["tabLive","live"],["tabHistory","historical"],["tabAtlas","atlas"],["tabScenario","scenario"]])$(id).classList.toggle("active",key===m);
    $("feedHeading").textContent=m==="live"?"News monitoring":m==="historical"?"Historical cases":m==="atlas"?"Dependency Atlas":"Scenario lab";
    $("feedSubtitle").textContent=m==="live"?"Screened Kazakhstan exposure candidates":m==="historical"?"Documented reference incidents":m==="atlas"?"Named assets and external relationships":"Illustrative conditional effects";
    $("effect").value="";$("sector").value="";$("region").value="";$("country").value="";$("search").value="";
    closeProfile();
    if(m==="scenario")pick(demo,{showProfile:false});
    else if(m==="historical")pick(memory.history[0],{showProfile:false});
    else if(m==="live"&&memory.events.length)pick(memory.events.find(e=>direction(e)==="mixed"&&Number.isFinite(e.lat))||memory.events.find(e=>Number.isFinite(e.lat))||memory.events[0],{showProfile:false});
    else {memory.selection=null;drawProfile(null);}
    renderFeed();
  }
  function renderFeed(){
    const filtered=filterEvents(),feed=$("feed");clear(feed);
    $("feedTotal").textContent=filtered.length+" "+(memory.mode==="atlas"?"assets":"items");
    if(!filtered.length){feed.append(make("div","empty",memory.mode==="live"?"No matching current reports. Check the collector health; this does not mean no relevant event occurred.":"No matches for the current filters."));globe.setEvents([]);return;}
    const fragment=document.createDocumentFragment();
    for(const e of filtered){
      const atlasMode=memory.mode==="atlas",card=make("article","event"+((memory.selection?.id===(atlasMode?e.id:e.id))?" chosen":""));
      const row=make("div","event-head");row.append(make("span","",atlasMode?e.id+" · "+e.sector:(e.source||"Source")+" · "+(e.published?new Date(e.published).toLocaleDateString("en-GB"):"Scenario")));
      if(!atlasMode)row.append(statusPill(direction(e)));card.append(row);
      card.append(make("h3","event-title",atlasMode?e.name:e.title));
      if(atlasMode)card.append(make("p","event-reason",shortText(e.external_counterpart,100)));
      else {
        card.append(make("div","event-meta",(e.country||"Geography unresolved")+" · "+e.sector+" · "+(e.tier||"Screened candidate")));
        if((e.impact_channels||[]).length>0){card.append(make("p","event-reason",(e.impact_channels||[]).length+" pathway(s) to inspect · "+(e.scenario?"conditional":"event-based")));}
      }
      card.onclick=()=>atlasMode?pickAsset(e):pick(e);fragment.append(card);
    }
    feed.append(fragment);
    const plotted=filtered.filter(e=>Number.isFinite(e.lat)&&Number.isFinite(e.lon));
    globe.setEvents(plotted);
    if(memory.mode==="live"){
      $("mapNotice").textContent=plotted.length+" of "+filtered.length+" screened reports geolocated · overlapping origins grouped · click a marker for all related stories";
    }
  }
  function pair(label,value){const p=make("div","info-row");p.append(make("span","",label),make("strong","",value));return p;}
  function sectionTitle(p,text){p.append(make("div","sectionhead",text));}
  function pickAsset(a){
    memory.selection=a;openProfile();globe.focusCountry(a.external_counterpart);
    renderFeed();
    const pane=$("profile");clear(pane);
    const heading=make("div","profilehead");heading.append(make("span","pill blue",a.id+" · "+a.sector),make("h3","",a.name));pane.append(heading);
    pane.append(pair("External counterpart",a.external_counterpart),pair("Evidence status","Dated Atlas research"));
    sectionTitle(pane,"Recorded relationship");
    pane.append(make("p","profile-text","This is a named dependency in the research inventory, not evidence that a disruption has occurred or that it caused a quantified impact."));
    const links=memory.atlas.links.filter(l=>l.sector===a.sector).slice(0,6);
    if(links.length){sectionTitle(pane,"Potential sector transmission");for(const l of links){let card=make("div","channel grey");card.append(make("div","channel-title",l.from+" → "+l.to),make("p","",l.relationship));pane.append(card);}}
    sectionTitle(pane,"Original research link");const sources=make("div","sources");sourceLink(sources,{label:a.name,url:a.source_url,role:"Source used in original Atlas; current status must be rechecked"});pane.append(sources);
  }
  function drawProfile(event){
    const pane=$("profile");clear(pane);
    if(!event){pane.append(make("div","empty","Select a news event or asset to inspect the evidence, sources and potential channels to Kazakhstan."));return;}
    const d=direction(event),heading=make("div","profilehead");heading.append(statusPill(d));
    heading.append(make("h3","",event.title));
    heading.append(make("div","meta",(event.source||"")+(event.published?" · "+(event.publication_precision==="date"?new Date(event.published).toLocaleDateString("en-GB"):new Date(event.published).toLocaleString("en-GB")):" · Hypothetical scenario")));
    pane.append(heading);
    pane.append(pair("Origin",event.country||"Not established"),pair("Sector",event.sector||"Not classified"),
      pair("Impact severity",Number.isInteger(event.severity)&&event.severity>=1&&event.severity<=5?event.severity+"/5 — assessed":"Unassessed"),
      pair("Probability","Unassessed · specify outcome & horizon"));
    const explanation=event.scenario?"Two opposing effects are mapped as conditional scenarios, not observed net benefits or losses.":"The article is screened for possible Kazakhstan relevance; further independent verification is required.";
    pane.append(make("div","insight warning",explanation));
    sectionTitle(pane,"Event overview");
    pane.append(make("p","profile-text",event.summary||"No article synopsis is available. Open the linked source."));
    sectionTitle(pane,"Why Kazakhstan may be exposed");
    pane.append(make("p","profile-text",event.reason||"Further investigation is needed to establish a specific relationship."));
    if(event.impact_summary)pane.append(make("p","profile-text",event.impact_summary));
    const channels=event.impact_channels||[];
    sectionTitle(pane,"Impact channels"+(channels.length?" · "+channels.length:""));
    if(!channels.length)pane.append(make("div","insight","Specific socioeconomic transmission and direction remain unresolved. A headline/asset match is insufficient to infer an effect."));
    for(const channel of channels){
      const dir=normalizeDirection(channel.direction),box=make("div","channel "+tone[dir].klass),head=make("div","channel-title");
      head.append(make("span","",channel.label||"Impact channel"),make("span","pill "+tone[dir].klass,tone[dir].label));box.append(head);
      box.append(make("p","",channel.mechanism||"No assessed mechanism."));if(channel.condition)box.append(make("p","", "Condition: "+channel.condition));
      if(channel.affected?.length)box.append(make("p","", "Who may be affected: "+channel.affected.join(", ")));
      box.append(make("p","", "Severity: "+(Number.isInteger(channel.severity)?channel.severity+"/5":"unassessed")+
        " · Evidence: "+(channel.evidence_status||"not verified")));
      pane.append(box);
    }
    sectionTitle(pane,"Verification & source provenance");
    const report=memory.reports[event.id];
    const stage=event.investigation_stage||report?.investigation_stage||event.verification||"Unverified reporting";
    pane.append(make("div","insight","Stage: "+stage+". Repeated or syndicated reporting does not establish independent corroboration. Background sources explain mechanisms, not article-specific impact."));
    const sources=make("div","sources"),all=candidateSources(event);
    if(!all.length)sources.append(make("div","empty","No accessible source link is supplied for this entry."));
    else for(const s of all.slice(0,15))sourceLink(sources,s);
    pane.append(sources);
    const related=event.groupEvents||[];
    if(related.length>1){
      sectionTitle(pane,"Other reports from this map location · "+related.length+" total");
      const others=make("div","grouped-reports");
      for(const r of related.filter(v=>v.id!==event.id).slice(0,60)){
        const button=make("button","grouped-event",shortText(r.title,100));
        button.type="button";button.onclick=()=>pick(r);others.append(button);
      }
      pane.append(others);
    }
    sectionTitle(pane,"Remaining analytical questions");
    pane.append(make("p","profile-text",event.scenario?
      "Did world oil prices actually change? What happened to Kazakhstan's realized export prices and shipments? Were domestic fuel and freight prices transmitted to households? What is the timeframe and baseline?":
      "Did the reported event occur? Which named dependency was affected? What domestic outcome was observed? What alternative explanations and counterfactuals apply?"));
  }
  function pick(e,{showProfile=true}={}){memory.selection=e;drawProfile(e);globe.selectEvent(e);if(showProfile)openProfile();renderFeed();}
  function openProfile(){const layer=$("profileLayer");layer.hidden=false;$("closeProfile").focus({preventScroll:true});}
  function closeProfile(){const layer=$("profileLayer");layer.hidden=true;}
  $("closeProfile").addEventListener("click",closeProfile);
  $("profileScrim").addEventListener("click",closeProfile);
  document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!$("profileLayer").hidden)closeProfile();});
  function safeFetch(file){return fetch("data/"+file+".json?"+Date.now()).then(r=>{if(!r.ok)throw Error(file+" HTTP "+r.status);return r.json()});}
  async function start(){
    globe.resize();renderFeed();drawProfile(null);
    const settled=await Promise.allSettled(["world","feed","status","atlas","investigations"].map(safeFetch));
    const take=i=>settled[i].status==="fulfilled"?settled[i].value:null;
    if(take(0)){memory.world=take(0).features||[];globe.setWorld(memory.world);}else{memory.worldError=true;$("mapNotice").textContent="Map coastlines unavailable; displaying a globe with grid lines.";}
    if(take(1))memory.events=take(1).events||[];
    if(take(2))memory.status=take(2);
    if(take(3))memory.atlas=take(3);
    if(take(4))memory.reports=Object.fromEntries((take(4).cases||[]).map(x=>[x.event_id,x]));
    fillFilters();
    const st=memory.status, time=st?.last_poll?new Date(st.last_poll).toLocaleString("en-GB"):"not collected";
    $("lastUpdated").textContent=time;
    $("sourceHealth").textContent=st?st.sources_successful+"/"+st.sources_configured:"Unavailable";
    $("sourceStatus").textContent=st?st.sources_successful+"/"+st.sources_configured+" sources reached · "+(st.error||"Scheduled every 12 hours (best effort)."):"Monitoring status cannot be loaded.";
    $("mainCount").textContent=memory.events.length+" screened reports · 30 days";
    $("atlasCount").textContent=(memory.atlas.assets?.length||0)+" assets";
    if(memory.events.length){const preferred=memory.events.find(e=>direction(e)==="mixed"&&Number.isFinite(e.lat))||
      memory.events.find(e=>(e.matches||[]).length&&Number.isFinite(e.lat))||
      memory.events.find(e=>Number.isFinite(e.lat))||memory.events[0];pick(preferred,{showProfile:false});}else drawProfile(null);
    renderFeed();
  }

  /* Genuine spherical projection. Countries and arcs are rendered directly on a 3D globe
     (orthographic sphere), with no API-key tiles, third-party map server or external library. */
  function Globe(canvas){
    this.canvas=canvas;this.ctx=canvas.getContext("2d",{alpha:false});this.w=0;this.h=0;
    this.lon=66;this.lat=28;this.zoom=1.0;this.drag=null;this.spin=false;this.sel=null;this.events=[];this.features=[];this.pins=[];this.frameTime=0;this.frame=0;
    this.onPick=null;
    this.resize=()=>{
      const rect=canvas.getBoundingClientRect();this.w=Math.max(1,rect.width);this.h=Math.max(1,rect.height);
      const dpr=Math.min(window.devicePixelRatio||1,2);
      canvas.width=Math.round(this.w*dpr);canvas.height=Math.round(this.h*dpr);
      this.ctx.setTransform(dpr,0,0,dpr,0,0);
    };
    if(window.ResizeObserver)new ResizeObserver(()=>this.resize()).observe(canvas);
    window.addEventListener("resize",this.resize);
    canvas.addEventListener("pointerdown",e=>{this.drag={x:e.clientX,y:e.clientY,oldX:e.clientX,oldY:e.clientY,moved:false};canvas.setPointerCapture(e.pointerId);canvas.classList.add("dragging");});
    canvas.addEventListener("pointermove",e=>{
      if(!this.drag)return;const dx=e.clientX-this.drag.oldX,dy=e.clientY-this.drag.oldY;
      if(Math.abs(e.clientX-this.drag.x)+Math.abs(e.clientY-this.drag.y)>5)this.drag.moved=true;
      this.lon=((this.lon-dx*.24+540)%360)-180;this.lat=Math.max(-75,Math.min(75,this.lat+dy*.18));
      this.drag.oldX=e.clientX;this.drag.oldY=e.clientY;
    });
    canvas.addEventListener("pointerup",e=>{
      const d=this.drag;this.drag=null;canvas.classList.remove("dragging");if(!d||d.moved)return;
      const rect=canvas.getBoundingClientRect(),x=e.clientX-rect.left,y=e.clientY-rect.top;
      let pin=this.pins.slice().reverse().find(p=>Math.hypot(p.x-x,p.y-y)<17);if(pin&&this.onPick)this.onPick(pin.event);
    });
    canvas.addEventListener("wheel",e=>{e.preventDefault();this.zoom=Math.max(.7,Math.min(1.55,this.zoom*(e.deltaY>0?.93:1.07)));},{passive:false});
    this.project=(lat,lon,rFactor=1)=>{
      const deg=Math.PI/180,a=lat*deg,b=(lon-this.lon)*deg,c=this.lat*deg;
      const ca=Math.cos(a),sa=Math.sin(a),cb=Math.cos(b),sb=Math.sin(b),cc=Math.cos(c),sc=Math.sin(c);
      const x=ca*sb,y=sa*cc-ca*cb*sc,z=sa*sc+ca*cb*cc;
      return {x:this.cx+this.rad*rFactor*x,y:this.cy-this.rad*rFactor*y,z};
    };
    this.geoWorld=(features)=>{
      return features.flatMap(f=>{
        const g=f.geometry||{};let rings=g.type==="Polygon"?g.coordinates:g.type==="MultiPolygon"?g.coordinates.flat(1):[];
        return rings.filter(r=>r.length>=3).map(r=>({name:f.name,ring:r.map(p=>[p[1],p[0]])}));
      });
    };
    this.setWorld=features=>{this.features=this.geoWorld(features);};
    this.setEvents=items=>{this.events=items||[];};
    this.selectEvent=event=>{this.sel=event; if(event&&Number.isFinite(event.lat)&&Number.isFinite(event.lon)){let lon=event.lon,dl=((lon-67+540)%360)-180;this.lon=((67+dl*.43+540)%360)-180;this.lat=Math.min(66,Math.max(-30,(event.lat+48)/2-3));}};
    this.focusCountry=()=>{};
    this.resize();
    const paint=(ts)=>{if(ts-this.frameTime>33){this.frameTime=ts;if(this.spin&&!this.drag)this.lon=((this.lon+.17+540)%360)-180;this.render(ts);};requestAnimationFrame(paint);};
    requestAnimationFrame(paint);
  }
  Globe.prototype.render=function(ts){
    const ctx=this.ctx,w=this.w,h=this.h;if(w<8||h<8)return;
    ctx.clearRect(0,0,w,h);ctx.fillStyle="#f6faff";ctx.fillRect(0,0,w,h);
    this.cx=w*.5;this.cy=h*.515;this.rad=Math.min(w*.43,h*.37)*this.zoom;
    const cx=this.cx,cy=this.cy,r=this.rad;
    // soft outer halo
    const halo=ctx.createRadialGradient(cx,cy,r*.71,cx,cy,r*1.25);halo.addColorStop(0,"rgba(180,211,239,0)");halo.addColorStop(.75,"rgba(123,167,214,.10)");halo.addColorStop(1,"rgba(123,167,214,0)");
    ctx.fillStyle=halo;ctx.beginPath();ctx.arc(cx,cy,r*1.28,0,Math.PI*2);ctx.fill();
    const sea=ctx.createRadialGradient(cx-r*.26,cy-r*.42,r*.06,cx+r*.14,cy+r*.13,r*1.24);
    sea.addColorStop(0,"#ecf7ff");sea.addColorStop(.58,"#bfdcec");sea.addColorStop(1,"#79a8c7");
    ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.fillStyle=sea;ctx.fill();
    ctx.save();ctx.beginPath();ctx.arc(cx,cy,r-.25,0,Math.PI*2);ctx.clip();
    ctx.strokeStyle="rgba(100,141,169,.19)";ctx.lineWidth=.8;
    const graticule=(points)=>{ctx.beginPath();let active=false;for(const [lat,lon] of points){const p=this.project(lat,lon);if(p.z>0){if(!active)ctx.moveTo(p.x,p.y);else ctx.lineTo(p.x,p.y);active=true}else active=false;}ctx.stroke();};
    for(let lat=-60;lat<=60;lat+=30){const pts=[];for(let lon=-180;lon<=180;lon+=3)pts.push([lat,lon]);graticule(pts);}
    for(let lon=-180;lon<180;lon+=30){const pts=[];for(let lat=-90;lat<=90;lat+=3)pts.push([lat,lon]);graticule(pts);}
    for(const feature of this.features){
      const ring=feature.ring,ka=feature.name==="Kazakhstan";
      ctx.beginPath();let visible=false,has=false;
      for(let i=0;i<ring.length;i++){const p=this.project(ring[i][0],ring[i][1]);if(p.z>0){if(!visible)ctx.moveTo(p.x,p.y);else ctx.lineTo(p.x,p.y);visible=true;has=true;}else visible=false;}
      if(!has)continue;ctx.closePath();ctx.fillStyle=ka?"#f2d8a5":"#d3e4d9";ctx.fill();
      ctx.strokeStyle=ka?"#c29c5f":"#aac9c1";ctx.lineWidth=ka?1.25:.55;ctx.stroke();
    }
    // transparent depth overlay to show sphere curvature
    const shade=ctx.createRadialGradient(cx-r*.38,cy-r*.5,r*.1,cx+r*.19,cy+r*.1,r*1.33);
    shade.addColorStop(0,"rgba(255,255,255,.10)");shade.addColorStop(.55,"rgba(14,56,83,0)");shade.addColorStop(1,"rgba(13,55,101,.20)");
    ctx.fillStyle=shade;ctx.fillRect(cx-r,cy-r,r*2,r*2);ctx.restore();
    ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.lineWidth=1.5;ctx.strokeStyle="#85aecb";ctx.stroke();
    this.pins=[];
    const candidates=this.events.slice().filter(e=>Number.isFinite(e.lat)&&Number.isFinite(e.lon));
    const selected=this.sel;
    // Group shared map origins by direction. Every report is represented by its
    // origin group; clicking the marker opens a dossier listing all reports.
    const groups=new Map();
    for(const e of candidates){
      const key=e.lat.toFixed(2)+"|"+e.lon.toFixed(2)+"|"+direction(e);
      if(!groups.has(key))groups.set(key,[]);
      groups.get(key).push(e);
    }
    for(const group of groups.values()){
      const representative=group.find(e=>e.id===selected?.id)||group[0];
      if(group.some(e=>e.id===selected?.id))continue;
      this.drawEvent(ctx,{...representative,groupEvents:group},ts,false);
    }
    if(selected&&candidates.some(e=>e.id===selected.id))
      this.drawEvent(ctx,{...selected,groupEvents:groups.get(selected.lat.toFixed(2)+"|"+selected.lon.toFixed(2)+"|"+direction(selected))||[selected]},ts,true);
    const kz=this.project(KZ[0],KZ[1]);if(kz.z>=0){
      ctx.beginPath();ctx.arc(kz.x,kz.y,8,0,Math.PI*2);ctx.fillStyle="#2066cb";ctx.fill();ctx.lineWidth=3;ctx.strokeStyle="#fff";ctx.stroke();
      ctx.fillStyle="#195095";ctx.font="700 10px DM Sans, sans-serif";ctx.fillText("KAZAKHSTAN",kz.x+13,kz.y-10);
    }
  };
  const vec=(lat,lon)=>{const la=lat*Math.PI/180,lo=lon*Math.PI/180;return [Math.cos(la)*Math.cos(lo),Math.cos(la)*Math.sin(lo),Math.sin(la)]};
  const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
  const norm=a=>{const l=Math.hypot(...a)||1;return a.map(x=>x/l)};
  const interp=(a,b,t)=>{let dot=Math.min(1,Math.max(-1,a.reduce((v,x,i)=>v+x*b[i],0)));const th=Math.acos(dot),sin=Math.sin(th);return sin<.0001?norm(a.map((x,i)=>x*(1-t)+b[i]*t)):a.map((x,i)=>(x*Math.sin((1-t)*th)+b[i]*Math.sin(t*th))/sin)};
  const geo=v=>[Math.atan2(v[2],Math.hypot(v[0],v[1]))*180/Math.PI,Math.atan2(v[1],v[0])*180/Math.PI];
  Globe.prototype.pointsFor=function(e,side){
    const A=vec(e.lat,e.lon),B=vec(KZ[0],KZ[1]),base=[];
    for(let i=0;i<=90;i++){
      const t=i/90,xyz=interp(A,B,t),ll=geo(xyz),lift=1+.11*Math.sin(Math.PI*t);
      base.push({...this.project(ll[0],ll[1],lift),t});
    }
    // Braid in *screen pixels*, not geographic degrees: two hairline fibres
    // touch or slightly overlap rather than diverging to country-size curves.
    if(!side)return base;
    return base.map((p,i)=>{
      const a=base[Math.max(0,i-1)],b=base[Math.min(base.length-1,i+1)];
      const dx=b.x-a.x,dy=b.y-a.y,len=Math.hypot(dx,dy)||1;
      const amplitude=0.72*side*Math.sin(10*Math.PI*p.t);
      return {...p,x:p.x-dy/len*amplitude,y:p.y+dx/len*amplitude};
    });
  };
  Globe.prototype.strokeArc=function(ctx,pts,color,width,dashed,ts,selected){
    ctx.save();ctx.lineWidth=width;ctx.lineCap="round";ctx.lineJoin="round";ctx.strokeStyle=color;ctx.globalAlpha=selected?.96:.48;
    if(dashed)ctx.setLineDash([5,6]);
    ctx.beginPath();let active=false;
    for(const p of pts){if(p.z>-.035){if(!active)ctx.moveTo(p.x,p.y);else ctx.lineTo(p.x,p.y);active=true;}else active=false;}ctx.stroke();
    if(selected&&!dashed&&pts.length){const p=pts[Math.floor((ts*.00022%1)*(pts.length-1))];if(p.z>0){ctx.setLineDash([]);ctx.globalAlpha=1;ctx.beginPath();ctx.arc(p.x,p.y,Math.max(2,width*.75),0,Math.PI*2);ctx.fillStyle=color;ctx.fill();}}
    const end=pts[pts.length-1],prev=pts[pts.length-5];
    if(end?.z>0&&prev?.z>0){ctx.setLineDash([]);ctx.globalAlpha=selected?1:.75;const a=Math.atan2(end.y-prev.y,end.x-prev.x);ctx.beginPath();ctx.moveTo(end.x,end.y);ctx.lineTo(end.x-4*Math.cos(a-.5),end.y-4*Math.sin(a-.5));ctx.lineTo(end.x-4*Math.cos(a+.5),end.y-4*Math.sin(a+.5));ctx.closePath();ctx.fillStyle=color;ctx.fill();}
    ctx.restore();
  };
  function widthFor(severity,selected){
    const sev=Number(severity);
    // All fibres stay thin on the globe. Severity controls relative weight
    // but does not create ribbons spanning regions or countries.
    return Number.isInteger(sev)&&sev>=1&&sev<=5?(1.05+sev*.34+(selected?.2:0)):(selected?1.65:1.35);
  }
  Globe.prototype.drawEvent=function(ctx,e,ts,selected){
    const p=this.project(e.lat,e.lon);if(p.z<-.15&&!selected)return;
    const dir=direction(e),channels=e.impact_channels||[],hasMixed=dir==="mixed"&&channels.some(x=>normalizeDirection(x.direction)==="positive")&&channels.some(x=>normalizeDirection(x.direction)==="negative");
    if(hasMixed){
      const pos=channels.find(x=>normalizeDirection(x.direction)==="positive"),neg=channels.find(x=>normalizeDirection(x.direction)==="negative");
      this.strokeArc(ctx,this.pointsFor(e,+1),tone.positive.color,widthFor(pos?.severity,selected),!e.human_reviewed,ts,selected);
      this.strokeArc(ctx,this.pointsFor(e,-1),tone.negative.color,widthFor(neg?.severity,selected),!e.human_reviewed,ts,selected);
    }else{
      const effective=dir==="mixed"?"unknown":dir;
      this.strokeArc(ctx,this.pointsFor(e,0),tone[effective].color,widthFor(e.severity,selected),!e.human_reviewed,ts,selected);
    }
    if(p.z>=0){
      ctx.save();ctx.beginPath();ctx.arc(p.x,p.y,selected?5:3.2,0,2*Math.PI);
      ctx.fillStyle=hasMixed?"#b17d75":tone[dir].color;ctx.fill();
      ctx.lineWidth=selected?3:2;ctx.strokeStyle="#fff";ctx.stroke();ctx.restore();
      this.pins.push({x:p.x,y:p.y,event:e});
      if((e.groupEvents||[]).length>1){
        const n=e.groupEvents.length;
        ctx.save();ctx.font="700 9px DM Sans, sans-serif";ctx.fillStyle="#213c5b";
        ctx.fillText(n>99?"99+":String(n),p.x+7,p.y-7);ctx.restore();
      }
      if(selected){ctx.fillStyle="#314964";ctx.font="700 10px DM Sans, sans-serif";ctx.fillText(e.country,p.x+12,p.y+3);}
    }
  };

  const globe=new Globe($("globe"));
  globe.onPick=e=>pick(e);
  $("tabLive").onclick=()=>setMode("live");
  $("tabHistory").onclick=()=>setMode("historical");
  $("tabAtlas").onclick=()=>setMode("atlas");
  $("tabScenario").onclick=()=>setMode("scenario");
  $("scenarioShortcut").onclick=()=>setMode("scenario");
  for(const id of ["search","sector","region","country","effect","window"])$(id).addEventListener("input",renderFeed);
  $("zoomIn").onclick=()=>globe.zoom=Math.min(1.55,globe.zoom*1.12);
  $("zoomOut").onclick=()=>globe.zoom=Math.max(.7,globe.zoom/1.12);
  $("resetView").onclick=()=>{globe.lon=66;globe.lat=28;globe.zoom=1;};
  $("spin").onclick=()=>{globe.spin=!globe.spin;$("spin").classList.toggle("active",globe.spin);};
  start();
})();
