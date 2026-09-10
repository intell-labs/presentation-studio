const assert=require('node:assert/strict');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');
const {inspectLegibility}=require('../../plugins/presentation-studio/skills/presentation-studio/scripts/legibility_qa.cjs');
const {settle}=require('../../plugins/presentation-studio/skills/presentation-studio/scripts/design_qa.cjs');
const runtime=path.resolve(__dirname,'../../plugins/presentation-studio/skills/presentation-studio/assets/runtime/base-deck.html');

(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try{
    const page=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'});
    await page.setContent(`<style>.slide{width:1920px;background:white;color:#111;font:16px Arial}.card{padding:16px}.dark{background:#101820;color:white}.light{background:white;color:#111}</style>
      <section class="slide" id="test">
        <div class="card dark"><p id="dark-on-dark" style="color:#18212d">Dark text</p><p id="light-on-dark">Clear text</p></div>
        <div class="card light"><p id="light-on-white" style="color:#e4e8ed">Light text</p><p id="dark-on-white">Clear text</p></div>
        <p data-edit-id="copy">Readable parent <span id="nested-bad" style="color:#ededed">Unreadable child</span></p>
        <small id="unannotated-bad" style="color:#eee">Footnote without editable ID</small>
        <p id="small-gray" style="color:#888">Small gray</p><p id="large-gray" style="color:#888;font-size:32px">Large gray</p>
        <div class="dark"><p id="alpha-bad" style="color:rgba(255,255,255,.1)">Transparent text</p></div>
        <div style="background:white"><div style="background:rgba(0,0,0,.95);padding:10px"><span id="alpha-good" style="color:white">Alpha surface</span></div></div>
        <svg width="300" height="50"><text id="svg-bad" x="0" y="30" fill="white" style="color:black">SVG chart label</text></svg>
        <p id="fill-bad" style="color:black;-webkit-text-fill-color:white">Different painted text fill</p>
      </section>`);
    let result=await inspectLegibility(page,{},'.slide');
    const failures=result.issues.filter(i=>i.code==='geometry.contrast');
    assert.deepEqual(new Set(failures.map(i=>i.element)),new Set(['dark-on-dark','light-on-white','nested-bad','unannotated-bad','small-gray','alpha-bad','svg-bad','fill-bad']));
    assert(failures.every(i=>i.ratio<i.minimum&&i.text&&i.foreground&&i.background));
    assert.equal(result.coverage.contrast,result.coverage.textRuns);
    await page.evaluate(()=>{
      for(const id of ['dark-on-dark','alpha-bad'])document.getElementById(id).style.color='white';
      for(const id of ['light-on-white','nested-bad','unannotated-bad','small-gray'])document.getElementById(id).style.color='#111';
      document.getElementById('svg-bad').style.fill='#111';document.getElementById('fill-bad').style.webkitTextFillColor='#111';
    });
    assert.deepEqual((await inspectLegibility(page,{},'.slide')).issues,[]);
    await page.evaluate(()=>document.getElementById('dark-on-white').style.backgroundImage='linear-gradient(white,#111)');
    assert((await inspectLegibility(page,{},'.slide')).coverage.unmeasured.some(i=>i.element==='dark-on-white'&&i.criterion==='contrast'));
    await page.evaluate(()=>{
      const svg=document.querySelector('svg'),rect=document.createElementNS(svg.namespaceURI,'rect');
      for(const [name,value] of Object.entries({width:300,height:50,fill:'#111'}))rect.setAttribute(name,value);
      svg.prepend(rect);
    });
    assert((await inspectLegibility(page,{},'.slide')).coverage.unmeasured.some(i=>i.element==='svg-bad'),'Painted chart background must not be mistaken for the white page');
    await page.setContent('<style>section{background:white;font:16px Arial}button{background:#111;color:white;padding:16px}button:hover,button:focus{color:#222}</style><section id="hover"><button id="action">Action</button></section>');
    await page.hover('#action');
    assert((await inspectLegibility(page,{},'#hover')).issues.some(i=>i.element==='action'&&i.code==='geometry.contrast'));
    await page.mouse.move(0,0);await page.locator('#action').focus();
    assert((await inspectLegibility(page,{},'#hover')).issues.some(i=>i.element==='action'&&i.code==='geometry.contrast'));

    await page.goto(pathToFileURL(runtime).href);
    for(const theme of ['light','dark','custom']){
      await page.evaluate(theme=>document.querySelector(`[data-theme-choice="${theme}"]`).click(),theme);
      for(const hash of ['#hoja-01/estado-01','#hoja-02']){
        await page.evaluate(hash=>location.hash=hash,hash);await settle(page,'.slide.is-active');
        await page.mouse.move(0,0);await settle(page,'.slide.is-active');
        result=await inspectLegibility(page,{});
        assert.deepEqual(result.issues.filter(i=>i.code==='geometry.contrast'),[],`${theme} ${hash}`);
      }
    }
    // A label accidentally using the global light-theme accent on an inverse slide must fail.
    await page.evaluate(()=>{document.querySelector('[data-theme-choice="light"]').click();location.hash='#hoja-01/estado-01';});
    await settle(page,'.slide.is-active');
    await page.locator('#hoja-01 .kicker').evaluate(n=>n.style.color='var(--accent-readable)');
    assert((await inspectLegibility(page,{})).issues.some(i=>i.code==='geometry.contrast'&&i.element==='s01-kicker'));
    console.log('PASS contrast: dark/light surfaces, nested and unannotated copy, SVG/fill, alpha, text size, inverse anchors and all 3 starter themes.');
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
