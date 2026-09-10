const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');
const {evaluate}=require('../../plugins/presentation-studio/skills/presentation-studio/assets/runtime/numeric-model.js');
const {inspectLegibility}=require('../../plugins/presentation-studio/skills/presentation-studio/scripts/legibility_qa.cjs');
const {inspectNumbers}=require('../../plugins/presentation-studio/skills/presentation-studio/scripts/numeric_qa.cjs');
const {inspectDialogs}=require('../../plugins/presentation-studio/skills/presentation-studio/scripts/dialog_qa.cjs');
const runtime=path.resolve(__dirname,'../../plugins/presentation-studio/skills/presentation-studio/assets/runtime/base-deck.html');
const engine=path.join(path.dirname(runtime),'numeric-model.js');
const metric=(id,value,unit,unit_label,meaning)=>({id,value,unit,unit_label,meaning,label:id,period:'Mensual',status:'assumption',source:null});
const model={locale:'en-US',nodes:[
  metric('saving',55000,{USD:1,month:-1},'USD / mes','saving'),
  metric('packages',400000,{package:1,month:-1},'paquetes / mes','volume'),
  metric('people',600,{person:1},'personas','headcount'),
  {...metric('months',12,{month:1},'meses','duration'),period:'12 meses'},
  {...metric('perPackage',null,{USD:1,package:-1},'USD / paquete','saving'),operation:'divide',args:['saving','packages'],decimals:4},
  {...metric('annual',null,{USD:1},'USD','saving'),operation:'multiply',args:['saving','months'],period:'Ritmo de 12 meses',aggregation:'annualized'},
  {...metric('productivity',null,{package:1,month:-1,person:-1},'paquetes / persona / mes','productivity'),operation:'divide',args:['packages','people']},
]};
const values=evaluate(model);
assert.equal(values.perPackage.value,.1375);assert.equal(values.annual.value,660000);
const changed=structuredClone(model);changed.nodes.find(n=>n.id==='people').value=700;
assert.equal(evaluate(changed).productivity.value,400000/700);
for(const mutate of [m=>m.nodes[1].value=0,m=>m.nodes[0].value=NaN,m=>m.nodes.find(n=>n.id==='perPackage').unit={person:1},m=>m.nodes.find(n=>n.id==='annual').args=['annual','months']]){
  const broken=structuredClone(model);mutate(broken);assert.throws(()=>evaluate(broken));
}

(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try{
    const page=await browser.newPage({viewport:{width:1440,height:900}});
    await page.setContent('<style>.slide{position:relative;width:1920px;height:1080px;background:white;color:black}.shape{position:absolute;left:40px;top:80px;width:200px;height:200px;border-radius:50%;background:#eee}.shape p{position:absolute;left:2px;top:0;font-size:24px}.low{color:#bbffdd}.region{position:absolute;top:500px;width:200px;height:30px}</style><section class="slide" id="hoja-01"><div class="shape" data-qa-shape="ellipse"><p data-edit-id="circle">Wide label</p></div><p class="low" data-edit-id="contrast">A readable number</p><div class="region" data-qa-box="brand" style="left:20px"></div><div class="region" data-qa-box="footer" style="left:225px"></div></section>');
    const project={design_contract:{composition:{clearances:[{a:'brand',b:'footer',min_px:24}]}}};
    let result=await inspectLegibility(page,project,'.slide');
    for(const code of ['geometry.shape-containment','geometry.contrast','geometry.clearance'])assert(result.issues.some(i=>i.code===code),code);
    await page.evaluate(()=>{document.querySelector('.shape p').style.cssText='left:36px;top:65px;font-size:24px';document.querySelector('.low').style.color='#222';document.querySelector('[data-qa-box="footer"]').style.left='260px';});
    result=await inspectLegibility(page,project,'.slide');assert.deepEqual(result.issues,[]);
    await page.evaluate(()=>document.querySelector('.low').style.backgroundImage='linear-gradient(white,gray)');
    assert((await inspectLegibility(page,project,'.slide')).coverage.unmeasured.some(n=>n.criterion==='contrast'));
    await page.evaluate(()=>{document.querySelector('.slide').style.opacity='.5';document.querySelector('.low').style.cssText='color:black;background:white';});
    assert((await inspectLegibility(page,project,'.slide')).coverage.unmeasured.some(n=>n.element==='contrast'),'Opaque child cannot cancel ancestor group opacity');

    const folder=fs.mkdtempSync(path.join(os.tmpdir(),'presentation-clarity-')),file=path.join(folder,'deck.html');
    const widget='<div data-metric="productivity"><output data-metric-value="productivity"></output><span data-metric-label="productivity"></span><small data-metric-context="productivity"></small></div>';
    const modal='<button id="open-calculation" data-dialog-open="calculation" style="position:fixed;top:4px;left:4px">Calculation</button><dialog class="ps-dialog" id="calculation" aria-label="Calculation"><button data-dialog-close>Close</button><section data-dialog-summary>'+widget+'</section><button data-dialog-edit>Edit assumptions</button><section data-dialog-editor hidden><label>People <input data-metric-input="people" type="number"></label></section></dialog>';
    let source=fs.readFileSync(runtime,'utf8').replace('</body>',modal+'<script type="application/json" id="presentation-numeric-data">'+JSON.stringify(model)+'</script><script>'+fs.readFileSync(engine,'utf8')+'</script></body>');
    fs.writeFileSync(file,source);
    await page.addInitScript(()=>{window.showSaveFilePicker=async()=>({createWritable:async()=>({write:async value=>window.saved=value,close:async()=>{}})});});
    await page.goto(pathToFileURL(file).href);
    await page.click('#open-calculation');
    await page.waitForSelector('#calculation[open]');
    assert.equal(await page.locator('[data-dialog-editor]').isVisible(),false);
    const hash=await page.evaluate(()=>location.hash);
    for(const key of ['ArrowRight','ArrowLeft','PageDown','Home','End','t','e'])await page.keyboard.press(key);
    assert.equal(await page.evaluate(()=>location.hash),hash);
    assert.equal(await page.locator('body').evaluate(n=>n.classList.contains('edit-mode')),false);
    await page.click('[data-dialog-edit]');await page.locator('[data-metric-input]').fill('700');await page.locator('[data-metric-input]').dispatchEvent('change');
    assert.deepEqual((await inspectNumbers(page)).issues,[]);
    assert.equal(await page.locator('[data-metric-value]').textContent(),'571.43');
    await page.locator('[data-metric-context]').evaluate(n=>n.hidden=true);
    assert((await inspectNumbers(page)).issues.some(i=>i.code==='numeric.binding'),'Visible value must not hide its context');
    await page.locator('[data-metric-context]').evaluate(n=>n.hidden=false);
    await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('#calculation').open);
    assert.equal(await page.evaluate(()=>document.activeElement.id),'open-calculation');
    await page.click('#open-calculation');assert.equal(await page.locator('[data-dialog-editor]').isVisible(),false);
    await page.keyboard.press('Meta+s');await page.waitForFunction(()=>typeof window.saved==='string');
    const saved=await page.evaluate(()=>window.saved);const exported=path.join(folder,'saved.html');fs.writeFileSync(exported,saved);
    await page.goto(pathToFileURL(exported).href);await page.click('#open-calculation');
    assert.equal(await page.locator('[data-metric-value]').textContent(),'571.43');
    assert.deepEqual((await inspectNumbers(page)).issues,[]);
    await page.keyboard.press('Escape');
    await page.evaluate(()=>document.querySelector('.slide.is-active').append(document.querySelector('#open-calculation')));
    for(const viewport of [{width:1440,height:900},{width:390,height:844}]){
      await page.setViewportSize(viewport);
      const checks=await inspectDialogs(page,{},async result=>{
        if(result.state==='summary')assert((await page.locator('#calculation').boundingBox()).height<500,'Summary must fit its content, not stretch to viewport height');
        const screenshot=path.join(folder,`dialog-${viewport.width}-${result.state}.png`);
        await page.screenshot({path:screenshot});
      });
      assert(checks.some(r=>r.state==='summary'));assert(checks.some(r=>r.state==='editor'));
      assert.deepEqual(checks.flatMap(r=>r.issues),[]);
    }
    console.log('Dialog screenshots: '+folder);
    console.log('PASS numeric dependencies, units, invalid inputs, annualization, shape/contrast/clearance, modal keyboard/focus, progressive editing and save/reopen.');
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
