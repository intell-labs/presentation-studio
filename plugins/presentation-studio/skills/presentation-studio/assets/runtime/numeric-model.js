/* Optional self-contained model. Inline only for decks with linked metrics/calculators. */
(function(scope){
  'use strict';
  const unitKey=u=>JSON.stringify(Object.entries(u||{}).filter(([,v])=>v!==0).sort(([a],[b])=>a.localeCompare(b)));
  function evaluate(model){
    const nodes=new Map(),values={},visiting=new Set();
    for(const n of model.nodes||[]){
      if(!n.id||nodes.has(n.id))throw Error('Duplicate/missing metric ID');
      if(!n.label||!n.meaning||!n.unit_label||!n.period||!['observed','assumption','estimate'].includes(n.status))throw Error(`Incomplete metric meaning/unit/period/status: ${n.id}`);
      if(n.status==='observed'&&!n.source)throw Error(`Observed metric lacks source: ${n.id}`);
      if(!n.unit||Object.values(n.unit).some(v=>!Number.isInteger(v)))throw Error(`Invalid dimensions: ${n.id}`);
      if(n.decimals!==undefined&&(!Number.isInteger(n.decimals)||n.decimals<0||n.decimals>20))throw Error(`Invalid precision: ${n.id}`);
      nodes.set(n.id,n);
    }
    const visit=id=>{
      if(Object.hasOwn(values,id))return values[id];
      const n=nodes.get(id);if(!n)throw Error(`Unknown dependency: ${id}`);
      if(visiting.has(id))throw Error(`Circular dependency: ${id}`);visiting.add(id);
      let value=n.value,unit=n.unit;
      if(n.operation){
        if(!Array.isArray(n.args)||n.args.length!==2)throw Error(`Operation needs two dependencies: ${id}`);
        const [a,b]=n.args.map(visit);unit={...a.unit};
        if(n.operation==='add'||n.operation==='subtract'){
          if(unitKey(a.unit)!==unitKey(b.unit))throw Error(`Incompatible units: ${id}`);
          value=n.operation==='add'?a.value+b.value:a.value-b.value;
        }else if(n.operation==='multiply'||n.operation==='divide'){
          if(n.operation==='divide'&&b.value===0)throw Error(`Zero denominator: ${id}`);
          value=n.operation==='multiply'?a.value*b.value:a.value/b.value;
          for(const [key,power] of Object.entries(b.unit))unit[key]=(unit[key]||0)+(n.operation==='multiply'?power:-power);
        }else throw Error(`Unsupported operation: ${id}`);
        if(unitKey(unit)!==unitKey(n.unit))throw Error(`Result unit mismatch: ${id}`);
        if((a.status!=='observed'||b.status!=='observed')&&n.status==='observed')throw Error(`Derived assumption labelled observed: ${id}`);
      }
      if(typeof value!=='number'||!Number.isFinite(value)||(Number.isFinite(n.min)&&value<n.min)||(Number.isFinite(n.max)&&value>n.max))throw Error(`Invalid/out-of-range value: ${id}`);
      visiting.delete(id);return values[id]={value,unit,status:n.status};
    };
    for(const id of nodes.keys())visit(id);
    return values;
  }
  function context(n){return [n.unit_label,n.period,n.aggregation==='annualized'?'Anualizado; no es acumulado real del primer año':null,n.status==='assumption'?'Supuesto':n.status==='estimate'?'Estimado':null,n.source?'Fuente: '+n.source:'Sin fuente medida'].filter(Boolean).join(' · ');}
  function render(root,model){
    const values=evaluate(model);
    const map=new Map(model.nodes.map(n=>[n.id,n]));
    for(const el of root.querySelectorAll('[data-metric-value],[data-metric-label],[data-metric-context]')){
      const id=el.dataset.metricValue||el.dataset.metricLabel||el.dataset.metricContext,n=map.get(id);
      if(!n)throw Error(`Unbound metric: ${id}`);
      el.textContent=el.hasAttribute('data-metric-value')?new Intl.NumberFormat(model.locale||'es-SV',{maximumFractionDigits:n.decimals??2,minimumFractionDigits:n.decimals??0}).format(values[id].value):el.hasAttribute('data-metric-label')?n.label:context(n);
      el.setAttribute('contenteditable','false');
    }
    return values;
  }
  function attach(root=document){
    const source=root.querySelector('#presentation-numeric-data');if(!source)return null;
    let model=JSON.parse(source.textContent);render(root,model);
    root.querySelectorAll('[data-metric-input]').forEach(input=>{
      const node=model.nodes.find(n=>n.id===input.dataset.metricInput);
      if(!node||node.operation||node.status!=='assumption')throw Error('Only input assumptions may be edited');
      input.value=node.value;
      input.addEventListener('change',()=>{
        const candidate=JSON.parse(JSON.stringify(model)),n=candidate.nodes.find(n=>n.id===input.dataset.metricInput);
        n.value=input.value.trim()===''?NaN:Number(input.value);
        try{evaluate(candidate);input.setCustomValidity('');model=candidate;source.textContent=JSON.stringify(model);render(root,model);root.dispatchEvent(new CustomEvent('presentation:data-change',{bubbles:true}));}
        catch(error){input.setCustomValidity(error.message);input.reportValidity();}
      });
    });
    return {get model(){return model;}};
  }
  const api={evaluate,render,attach,context};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  else{scope.PresentationNumbers=api;if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>attach());else attach();}
})(typeof globalThis!=='undefined'?globalThis:this);
