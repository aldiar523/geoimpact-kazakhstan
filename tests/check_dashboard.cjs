const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const html=fs.readFileSync('index.html','utf8');
const scripts=[...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)];
assert.ok(scripts.length>0,'Expected inline dashboard script');
for (const [i,m] of scripts.entries())new vm.Script(m[1],{filename:'index-inline-'+i+'.js'});
for(const id of ['tablive','tabhist','tabatlas','map','feed','detail']){
 assert.ok(html.includes('id="'+id+'"'),'Missing UI control '+id);
}
assert.ok(html.includes("data/"),'Static dashboard must load monitored JSON');
console.log('Dashboard script syntax and controls verified');
