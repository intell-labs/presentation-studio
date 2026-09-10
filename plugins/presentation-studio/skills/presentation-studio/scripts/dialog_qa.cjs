const {settle}=require('./design_qa.cjs');
const {inspectLegibility}=require('./legibility_qa.cjs');
const {inspectNumbers}=require('./numeric_qa.cjs');

// Content dialogs are optional. Do not add fake controls or content to pass QA.
async function inspectDialogs(page,project,onState=async()=>{}){
  const results=[];
  const triggers=page.locator('.slide.is-active [data-dialog-open]');
  for(let index=0;index<await triggers.count();index++){
    const trigger=triggers.nth(index);
    if(!await trigger.isVisible())continue;
    const id=await trigger.getAttribute('data-dialog-open'),selector=`dialog[id=${JSON.stringify(id)}]`;
    const dialog=page.locator(selector),issues=[];
    const add=(code,message)=>issues.push({code:'runtime.dialog-'+code,message,slide:id,state:0});
    const before=await page.evaluate(()=>({hash:location.hash,edit:document.body.classList.contains('edit-mode')}));
    try{
      await trigger.click({timeout:2500});
      await page.waitForFunction(id=>document.getElementById(id)?.open,id,{timeout:1500});
      await settle(page,selector);
      const initial=await dialog.evaluate(n=>({summary:!!n.querySelector('[data-dialog-summary]'),editorOpen:[...n.querySelectorAll('[data-dialog-editor]')].some(e=>!e.hidden),label:!!(n.getAttribute('aria-label')||n.getAttribute('aria-labelledby'))}));
      if(!initial.summary||initial.editorOpen)add('summary','Open on a useful summary with assumption editing collapsed.');
      if(!initial.label)add('name','Content dialog needs an accessible name.');
      for(const key of ['ArrowRight','PageDown','Home','End','t','e'])await page.keyboard.press(key);
      const after=await page.evaluate(()=>({hash:location.hash,edit:document.body.classList.contains('edit-mode')}));
      if(JSON.stringify(before)!==JSON.stringify(after))add('shortcuts','Dialog leaked a presentation shortcut.');
      for(const mode of ['summary','editor']){
        if(mode==='editor'){
          const edit=dialog.locator('[data-dialog-edit]');
          if(!await edit.count())continue;
          await edit.first().click();await settle(page,selector);
          if(!await dialog.locator('[data-dialog-editor]').first().isVisible())add('editor','Assumption editor did not expand.');
        }
        const geometry=await dialog.evaluate(n=>{const r=n.getBoundingClientRect();return {fits:r.left>=0&&r.top>=0&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1,horizontal:n.scrollWidth>n.clientWidth+1,focus:n.contains(document.activeElement)};});
        if(!geometry.fits||geometry.horizontal)add('geometry','Dialog exceeds viewport or clips horizontally.');
        if(!geometry.focus)add('focus','Focus is outside the open dialog.');
        const legibility=await inspectLegibility(page,project,selector),numeric=await inspectNumbers(page);
        const result={dialog:id,state:mode,issues:[...issues,...legibility.issues,...numeric.issues],coverage:{...legibility.coverage,numeric:numeric.coverage}};
        results.push(result);await onState(result);
      }
      // Tab must remain within native modal, then Escape must restore its opener.
      for(let i=0;i<3;i++){await page.keyboard.press('Tab');if(!await dialog.evaluate(n=>n.contains(document.activeElement)))add('focus-trap','Tab escaped the modal.');}
      await page.keyboard.press('Escape');
      await page.waitForFunction(id=>!document.getElementById(id)?.open,id,{timeout:1500});
      if(!await trigger.evaluate(n=>document.activeElement===n))add('focus-return','Closing did not return focus to its trigger.');
    }catch(error){add('interaction',error.message);await page.evaluate(()=>document.querySelectorAll('dialog[open]').forEach(n=>n.close()));}
    results.push({dialog:id,state:'interaction',issues,coverage:{interaction:true}});
  }
  return results;
}
module.exports={inspectDialogs};
