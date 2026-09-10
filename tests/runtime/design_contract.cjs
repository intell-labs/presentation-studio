#!/usr/bin/env node
// Actual keyboard/menu/save/geometry tests; no visible browser opens.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawnSync } = require('node:child_process');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');
const { inspectDesign, settle } = require('../../plugins/presentation-studio/skills/presentation-studio/scripts/design_qa.cjs');

(async () => {
  const directory=fs.mkdtempSync(path.join(os.tmpdir(),'presentation-studio-regression-'));
  const build=spawnSync('python3',[path.resolve(__dirname,'../structural/test_design_contract.py'),directory],{encoding:'utf8'});
  assert.equal(build.status,0,build.stderr);
  const file=path.join(directory,'presentation.html');
  const project=JSON.parse(fs.readFileSync(path.join(directory,'presentation-project.json'),'utf8'));
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try {
    const page=await browser.newPage({viewport:{width:1440,height:900}});
    await page.addInitScript(() => {
      localStorage.setItem('presentation-studio-theme:'+location.pathname,'custom');
      window.showSaveFilePicker=async()=>({name:'test.html',createWritable:async()=>({write:async value=>{window.savedHTML=value;},close:async()=>{}})});
    });
    await page.goto(pathToFileURL(file).href);
    assert.equal(await page.getAttribute('body','data-theme'),'light','Stale custom should resolve to approved default');
    await page.click('#menu-trigger');
    await settle(page,'#control-menu'); // Normal motion, no timing override.
    assert.deepEqual(await page.locator('[data-theme-choice]').evaluateAll(nodes=>nodes.map(n=>n.dataset.themeChoice)),['light','dark']);
    await page.keyboard.press('Escape');
    for(const expected of ['dark','light','dark','light']) {
      await page.keyboard.press('t');
      assert.equal(await page.getAttribute('body','data-theme'),expected);
    }
    await page.evaluate(()=>{location.hash='#hoja-02';});
    await page.waitForSelector('#hoja-02.is-active');
    await settle(page,'.slide.is-active');
    assert.deepEqual(await inspectDesign(page,project),[]);
    await page.evaluate(()=>{document.querySelector('[data-theme-choice]').parentElement.insertAdjacentHTML('beforeend','<button data-theme-choice="custom">Unexpected</button>');});
    assert((await inspectDesign(page,project)).some(i=>i.code==='design.themes'),'Extra theme must fail');
    await page.evaluate(()=>document.querySelector('[data-theme-choice="custom"]').remove());
    await page.evaluate(()=>document.querySelector('[data-qa-box="logo-0"]').style.width='190px');
    assert((await inspectDesign(page,project)).some(i=>i.code==='design.composition'),'Unequal approved boxes must fail');
    await page.evaluate(()=>document.querySelector('[data-qa-box="logo-0"]').style.removeProperty('width'));
    await page.evaluate(()=>document.querySelector('[data-asset-id="logo-0"]').style.display='none');
    assert((await inspectDesign(page,project)).some(i=>i.code==='assets.not-visible'),'Hidden required logo must fail');
    await page.evaluate(()=>document.querySelector('[data-asset-id="logo-0"]').style.removeProperty('display'));
    await page.click('#menu-trigger');await settle(page,'#control-menu');
    await page.click('#edit-theme');
    await page.locator('#theme-dialog button[value="apply"]').click();
    assert.equal(await page.getAttribute('body','data-theme'),'light','Palette editing must not enable custom');
    await page.click('#menu-trigger');await settle(page,'#control-menu');
    await page.click('#save-as');
    await page.waitForFunction(()=>typeof window.savedHTML==='string');
    const saved=await page.evaluate(()=>window.savedHTML);
    const embedded=JSON.parse(saved.match(/<script\b[^>]*id="presentation-project-data"[^>]*>([\s\S]*?)<\/script>/)[1]);
    assert.deepEqual(embedded.appearance.available_themes,['light','dark']);
    assert(!/<button\b[^>]*data-theme-choice="custom"/.test(saved));
    assert(saved.includes('Approved text stays unchanged.'));
    assert(saved.includes('Unrelated approved closing remains intact.'));
    const exported=path.join(directory,'saved.html');fs.writeFileSync(exported,saved);
    await page.goto(pathToFileURL(exported).href);
    assert.deepEqual(await page.locator('[data-theme-choice]').evaluateAll(nodes=>nodes.map(n=>n.dataset.themeChoice)),['light','dark']);
    assert.equal(await page.locator('.services article').count(),5);
    assert.equal(await page.locator('.services article h3 + p').count(),5);
    assert.equal(await page.locator('[data-asset-id]').count(),6);
    console.log('PASS enabled themes, stale storage, keyboard, real-motion menu, palette, save/reload, composition, hidden logo, service grouping and preserved text.');
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
