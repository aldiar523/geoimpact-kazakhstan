const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const html=fs.readFileSync('index.html','utf8');
const app=fs.readFileSync('app.js','utf8');
const css=fs.readFileSync('styles.css','utf8');
new vm.Script(app,{filename:'app.js'});
assert.ok(html.includes('src="./app.js"'),'App bundle must be referenced');
assert.ok(html.includes('href="./styles.css"'),'Light stylesheet must be referenced');
for(const id of ['globe','profileLayer','profileModal','unlocatedMarker','unlocatedCount','closeProfile','profileScrim','tabLive','tabHistory','tabAtlas','tabScenario','feed','profile','sector','region','country','effect','window','scenarioShortcut','sourceHealth']){
  assert.ok(html.includes('id="'+id+'"'),'Missing required user control '+id);
}
assert.ok(app.includes('this.geoWorld')&&app.includes('Globe.prototype.drawEvent'),'3D globe not configured');
assert.ok(app.includes('Math.sin(10*Math.PI*p.t)'),'Braided dual-impact geometry is missing');
assert.ok(app.includes('widthFor'),'Severity-based width is missing');
assert.ok(app.includes('groupEvents:group'),'Full event map grouping is missing');
assert.ok(app.includes('openProfile()')&&app.includes('closeProfile()'),'Event profile modal missing');
assert.ok(app.includes('candidateSources(event)'),'Event evidence source grouping missing');
assert.ok(css.includes('.panel')&&css.includes('.globe-panel')&&!css.includes('color-scheme:dark'),'Light UI must render');
console.log('GeoImpact v0.5 JS syntax, layout, braided arc and evidence-profile assertions passed');
