const {evaluate,context}=require('../assets/runtime/numeric-model.js');
async function inspectNumbers(page){
  let model;
  try{model=await page.evaluate(()=>{const n=document.querySelector('#presentation-numeric-data');return n?JSON.parse(n.textContent):null;});}
  catch(error){return {issues:[{code:'numeric.model',message:'Invalid numeric JSON: '+error.message,slide:'numeric-model',state:0}],coverage:{metrics:0,status:'failed'}};}
  if(!model)return {issues:[],coverage:{metrics:0,status:'not-applicable'}};
  let values;
  try{values=evaluate(model);}catch(error){return {issues:[{code:'numeric.model',message:error.message,slide:'numeric-model',state:0}],coverage:{metrics:0,status:'failed'}};}
  const expected=Object.fromEntries(model.nodes.map(n=>[n.id,{value:new Intl.NumberFormat(model.locale||'es-SV',{maximumFractionDigits:n.decimals??2,minimumFractionDigits:n.decimals??0}).format(values[n.id].value),label:n.label,context:context(n)}]));
  const issues=await page.evaluate(expected=>{
    const issues=[];
    const visible=n=>{if(!n)return false;for(let p=n;p;p=p.parentElement){const s=getComputedStyle(p);if(p.hidden||s.display==='none'||s.visibility==='hidden'||Number(s.opacity)===0)return false;}return n.getBoundingClientRect().width>0;};
    for(const output of document.querySelectorAll('[data-metric-value]')){
      const id=output.dataset.metricValue,metric=expected[id],container=output.closest('[data-metric]');
      const add=message=>issues.push({code:'numeric.binding',message,slide:output.closest('.slide')?.id||'numeric-model',state:0});
      if(!metric||output.textContent.trim()!==metric.value){add(`Stale or unbound metric ${id}.`);continue;}
      if(!container||container.querySelector('[data-metric-label]')?.textContent!==metric.label||container.querySelector('[data-metric-context]')?.textContent!==metric.context)add(`Metric ${id} lacks its local meaning/unit/period/estimate context.`);
      if(visible(output)&&(!visible(container?.querySelector('[data-metric-label]'))||!visible(container?.querySelector('[data-metric-context]'))))add(`Metric ${id} hides its meaning or context while showing the number.`);
    }
    for(const n of document.querySelectorAll('[data-metric-input]'))if(!expected[n.dataset.metricInput])issues.push({code:'numeric.input',message:'Unbound assumption input',slide:'numeric-model',state:0});
    return issues;
  },expected);
  return {issues,coverage:{metrics:Object.keys(values).length,status:issues.length?'failed':'passed'}};
}
module.exports={inspectNumbers};
