'use strict';
// No real annotations/results are read or written: fs is injected in a VM.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'analyse_pilot_annotations.js'),'utf8');
const core=require('./annotation_review_core.js');
let reads=0,writes=0,printed='';
const labels={schema_version:1,dataset_id:'fixture',annotations:{},policy:{},exported_at:'fixture-time'};
const manifest={schema_version:1,dataset_id:'fixture',frames:[]};
const fakeFs={readFileSync:p=>{reads++;return Buffer.from(JSON.stringify(p.endsWith('pilot_annotations.json')?labels:manifest));},
  writeFileSync:()=>{writes++;}};
const requireFake=name=>name==='fs'?fakeFs:name==='./annotation_review_core.js'?core:require(name);
requireFake.main={};
const context=vm.createContext({require:requireFake,module:{exports:{}},__dirname,
  Buffer,process:{stdout:{write:value=>{printed+=value;}},exitCode:0}});
vm.runInContext(source,context);
assert.equal(reads,0);assert.equal(writes,0);assert.equal(printed,'');
const first=context.module.exports.buildPilotEvaluation(__dirname);
assert.equal(first.exitCode,0);assert.equal(first.report.dataset_id,'fixture');assert.equal(first.report.settings.length,6);
assert.equal(writes,0);assert.equal(printed,'');
labels.dataset_id='mismatch';
const bad=context.module.exports.buildPilotEvaluation(__dirname);
assert.equal(bad.exitCode,1);assert.equal(bad.report,null);assert(bad.summary.errors.includes('Dataset identity mismatch.'));
assert.equal(writes,0);
labels.dataset_id='fixture';context.module.exports.main();
assert.equal(writes,1);assert.equal(JSON.parse(printed).counts.frames,0);assert.equal(context.process.exitCode,0);
console.log('4 annotation-module checks passed: import safety, reusable evaluation, failure result, explicit CLI writes.');
