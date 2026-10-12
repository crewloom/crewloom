import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

test('worker persists activation, rejects foreign senders, and gates capture', () => {
  let handler: (message: any, sender: any, reply: (value: any) => void) => unknown;
  const state: Record<string, unknown> = {};
  let captures = 0;
  const chrome = {
    runtime: { id: 'owned', getURL: (p: string) => `chrome-extension://owned/${p}`, getManifest: () => ({version:'2.2.0'}), onInstalled: {addListener() {}}, onMessage: {addListener(fn: typeof handler) {handler=fn;}} },
    sidePanel: {setPanelBehavior: () => Promise.resolve()},
    contextMenus: {onClicked: {addListener() {}}},
    storage: {local: {get: (defaults: object, cb: any) => cb({...defaults,...state}), set: (value: object, cb: any) => {Object.assign(state,value);cb();}}},
    tabs: {captureVisibleTab: (_: unknown, __: unknown, cb: any) => {captures++;cb('png');}}
  };
  const context = vm.createContext({chrome,console,URL,AbortSignal});
  vm.runInContext(readFileSync('../extensions/chrome/background.js','utf8'),context);
  const panel={id:'owned',url:'chrome-extension://owned/sidepanel.html'};
  const call=(type: string, sender=panel, extra={}) => {let reply: any; handler!({type,...extra},sender,r=>reply=r);return reply;};
  assert.equal(call('CAPTURE_TAB').ok,false); assert.equal(captures,0);
  assert.equal(call('SET_CONTROL',{id:'owned',url:'https://foreign.example'},{enabled:true}).ok,false);
  assert.equal(call('SET_CONTROL',panel,{enabled:true}).enabled,true);
  assert.equal(call('CAPTURE_TAB').ok,true); assert.equal(captures,1);
  vm.runInContext(readFileSync('../extensions/chrome/background.js','utf8'),context);
  assert.equal(call('GET_CONTROL').enabled,true);
  call('SET_CONTROL',panel,{enabled:false}); assert.equal(call('CAPTURE_TAB').ok,false); assert.equal(captures,1);
});
