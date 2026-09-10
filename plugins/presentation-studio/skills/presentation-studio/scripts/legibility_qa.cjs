/* Measured legibility checks; complex paint is reported as unmeasured, not passed. */
async function inspectLegibility(page, project, rootSelector = '.slide.is-active') {
  return page.evaluate(({project, rootSelector}) => {
    const root=document.querySelector(rootSelector), issues=[], unmeasured=[];
    const coverage={contrast:0, textRuns:0, shapes:0, clearances:0, sharedRegions:0, critical:0, unmeasured};
    const slide=root?.id||'unknown';
    const add=(code,message,detail={})=>issues.push({code,message,slide,state:0,...detail});
    if(!root)return {issues:[{code:'geometry.root',message:'QA root missing',slide,state:0}],coverage};
    const name=n=>n.dataset.editId||n.dataset.qaBox||n.id||[n.closest('[data-edit-id]')?.dataset.editId,n.tagName].filter(Boolean).join('/');
    const visible=n=>{if(!n)return false;for(let p=n;p;p=p.parentElement){const s=getComputedStyle(p);if(p.hidden||s.display==='none'||s.visibility==='hidden'||Number(s.opacity)===0)return false;}return n.getBoundingClientRect().width>0;};
    // Measure actual text runs: an editable parent can contain differently colored spans.
    const texts=[],walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
    for(let node=walker.nextNode();node;node=walker.nextNode()){
      const text=node.parentElement;
      if(node.textContent.trim()&&visible(text)&&!text.closest('script,style,noscript,title,desc,.sr-only,.notes,[data-brand-mark]'))texts.push({text,node});
    }
    coverage.textRuns=texts.length;
    const scale=root.classList.contains('slide')?root.getBoundingClientRect().width/1920:1;
    const rgb=value=>{const m=value.match(/^rgba?\(([^)]+)\)$/);if(!m)return null;const a=m[1].split(/[ ,/]+/).map(Number);return a.length>=3&&a.every(Number.isFinite)?[a[0],a[1],a[2],a[3]??1]:null;};
    const over=(front,back)=>{const alpha=front[3]+back[3]*(1-front[3]);return [0,1,2].map(i=>(front[i]*front[3]+back[i]*back[3]*(1-front[3]))/(alpha||1)).concat(alpha);};
    const lum=c=>c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
    const boxes=[...root.querySelectorAll('[data-qa-box]')];
    for(const {text,node} of texts){
      const chain=[];for(let n=text;n;n=n.parentElement)chain.push(n);
      let bg=[255,255,255,1],complex=false,unsupportedEffect=false;
      for(const n of chain.reverse()){
        const style=getComputedStyle(n),color=rgb(style.backgroundColor);
        if(color?.[3]===1)complex=false; // An opaque local surface shields the paint below it.
        const pseudos=['::before','::after'].some(p=>{const s=getComputedStyle(n,p);return s.content!=='none'&&s.content!=='normal'&&s.display!=='none'&&s.visibility!=='hidden'&&Number(s.opacity)>0;});
        if(style.backgroundImage!=='none')complex=true;
        if(style.filter!=='none'||style.backdropFilter!=='none'||Number(style.opacity)!==1||style.mixBlendMode!=='normal'||pseudos)unsupportedEffect=true;
        if(color)bg=over(color,bg);else complex=true;
      }
      const style=getComputedStyle(text),svg=text.namespaceURI==='http://www.w3.org/2000/svg';
      const ink=svg?style.fill:(style.webkitTextFillColor||style.color),fg=rgb(ink);
      if(svg&&(style.stroke!=='none'||Number(style.fillOpacity)!==1))unsupportedEffect=true;
      const textRange=document.createRange();textRange.selectNodeContents(node);
      const textBounds=textRange.getBoundingClientRect();
      if([...root.querySelectorAll('img,svg,canvas,video,svg rect,svg path,svg circle,svg ellipse,svg polygon,svg image,svg use')].some(n=>{
        if(n.contains(text)||text.contains(n)||!visible(n))return false;
        const b=n.getBoundingClientRect();return b.left<textBounds.right&&b.right>textBounds.left&&b.top<textBounds.bottom&&b.bottom>textBounds.top;
      }))complex=true; // Sibling paint/photographs cannot be inferred from ancestral colors.
      if(complex||unsupportedEffect||!fg){unmeasured.push({element:name(text),criterion:'contrast',reason:'Complex image/gradient/overlay/filter paint needs visual inspection.'});}
      else{
        const front=over(fg,bg),a=lum(front),b=lum(bg),ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
        const size=parseFloat(style.fontSize)*scale,large=size>=24||(size>=18.66&&parseFloat(style.fontWeight)>=700);
        const min=large?3:4.5;coverage.contrast++;
        if(ratio<min)add('geometry.contrast',`${name(text)} contrast ${ratio.toFixed(2)}:1 is below ${min}:1 on its effective background.`,{element:name(text),text:node.textContent.trim().slice(0,100),foreground:ink,background:bg,ratio,minimum:min});
      }
      const shape=text.closest('[data-qa-shape="ellipse"]');
      if(shape){
        coverage.shapes++;
        const b=shape.getBoundingClientRect(),cx=b.left+b.width/2,cy=b.top+b.height/2;
        for(const r of textRange.getClientRects()){
          if(!r.width||!r.height)continue;
          if([[r.left,r.top],[r.right,r.top],[r.left,r.bottom],[r.right,r.bottom]].some(([x,y])=>((x-cx)/(b.width/2))**2+((y-cy)/(b.height/2))**2>1.015)){
            add('geometry.shape-containment',`${name(text)} fits the bounding box but leaves the visible ellipse ${name(shape)}.`);break;
          }
        }
      }
    }
    for(const check of project.design_contract?.composition?.clearances||[]){
      if(check.slide&&check.slide!==slide)continue;
      const a=boxes.find(n=>n.dataset.qaBox===check.a),b=boxes.find(n=>n.dataset.qaBox===check.b);
      if(!visible(a)||!visible(b)){add('geometry.clearance-coverage',`Missing visible region for ${check.a}/${check.b}.`);continue;}
      coverage.clearances++;
      const x=a.getBoundingClientRect(),y=b.getBoundingClientRect();
      const gap=Math.hypot(Math.max(0,x.left-y.right,y.left-x.right),Math.max(0,x.top-y.bottom,y.top-x.bottom))/scale;
      if(!Number.isFinite(check.min_px)||gap<check.min_px)add('geometry.clearance',`${check.a}/${check.b} have ${gap.toFixed(1)}px clearance; need ${check.min_px}px.`);
    }
    for(const check of project.design_contract?.composition?.shared_regions||[]){
      const slides=[...document.querySelectorAll('.slide')].filter(s=>!check.slides||check.slides.includes(s.id));
      const regions=slides.map(s=>s.querySelector(`[data-qa-box="${CSS.escape(check.box)}"]`));
      if(regions.some(n=>!n||!n.getBoundingClientRect().width)){add('geometry.shared-region-coverage',`Shared region ${check.box} missing/unmeasurable on a declared slide.`);continue;}
      for(const prop of check.properties||['width','height']){
        coverage.sharedRegions++;
        const values=regions.map(n=>{const r=n.getBoundingClientRect(),s=n.closest('.slide').getBoundingClientRect(),k=s.width/1920;return (r[prop]-(prop==='left'||prop==='right'?s.left:prop==='top'||prop==='bottom'?s.top:0))/k;});
        if(values.some(v=>!Number.isFinite(v))||Math.max(...values)-Math.min(...values)>(check.tolerance_px??2))add('geometry.shared-region',`Shared ${check.box} has inconsistent ${prop}.`);
      }
    }
    for(const n of root.querySelectorAll('[data-critical="true"]')){coverage.critical++;if(!visible(n))add('editorial.hidden-critical',`${name(n)} is indispensable but hidden from the audience.`);}
    if(document.body.dataset.viewMode==='audience')for(const n of root.querySelectorAll('[data-audience="internal"]'))if(visible(n))add('editorial.internal-content',`${name(n)} exposes internal instructions in the client view.`);
    for(const n of boxes.filter(visible)){
      if(!n.dataset.qaRole)unmeasured.push({element:name(n),criterion:'semantic-region',reason:'Missing role annotation.'});
      const s=getComputedStyle(n);
      if(!n.dataset.qaShape&&s.borderTopLeftRadius==='50%')unmeasured.push({element:name(n),criterion:'shape',reason:'Rounded shape lacks explicit containment annotation.'});
    }
    return {issues,coverage};
  }, {project,rootSelector});
}
module.exports={inspectLegibility};
