const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const html=fs.readFileSync('index.html','utf8');
const app=fs.readFileSync('app.js','utf8');
const css=fs.readFileSync('styles.css','utf8');
const theme=fs.readFileSync('theme.css','utf8');
new vm.Script(app,{filename:'app.js'});
assert.ok(html.includes('src="./app.js"'),'App bundle must be referenced');
assert.ok(html.includes('href="./styles.css"')&&html.includes('href="./theme.css"'),'Dark stylesheets must be referenced');
for(const id of ['globe','profileLayer','profileModal','unlocatedMarker','unlocatedCount','closeProfile','profileScrim','tabLive','tabInternational','tabHistory','tabAtlas','tabScenario','feed','profile','sector','region','country','effect','window','sortOrder','reviewFilter','reviewProgress','reviewFile','exportReviews','importReviews','countrySwitcher','countryEventSelect','prevCountryEvent','nextCountryEvent','scenarioShortcut','sourceHealth']){
  assert.ok(html.includes('id="'+id+'"'),'Missing required user control '+id);
}
assert.ok(app.includes('this.geoWorld')&&app.includes('Globe.prototype.drawEvent'),'3D globe not configured');
assert.ok(app.includes('Math.sin(12*Math.PI*p.t)')&&app.includes('Globe.prototype.braidArc'),'Braided dual-impact geometry is missing');
assert.ok(app.includes('widthFor'),'Severity-based width is missing');
assert.ok(app.includes('groupEvents:group'),'Full event map grouping is missing');
assert.ok(app.includes('openProfile()')&&app.includes('closeProfile()'),'Event profile modal missing');
assert.ok(app.includes('event.related_sources'),'Linked source collection missing');
assert.ok(app.includes('"events"'),'Event-first dataset is not loaded');
assert.ok(app.includes('candidateSources(event)'),'Event evidence source grouping missing');
assert.ok(css.includes('.panel')&&theme.includes('color-scheme:dark'),'Dark globe theme must render');
assert.ok(app.includes('saveReview(')&&app.includes('loadReviews('),'Human review storage missing');
assert.ok(app.includes('international_watch'),'Global news watch missing');
assert.ok(app.includes('refreshCountrySwitcher('),'Country event carousel missing');
console.log('GeoImpact v0.8 JS syntax, dark globe, woven fibres, country switching and human review controls passed');
