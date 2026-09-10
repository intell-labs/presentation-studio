/* Decision-fidelity checks shared by rendered QA and regression tests. */
const crypto = require('crypto');
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
function contractHash(project) {
  const ordered = value => Array.isArray(value) ? value.map(ordered) : value && typeof value === 'object'
    ? Object.fromEntries(Object.keys(value).sort().map(key => [key, ordered(value[key])])) : value;
  const { visual_qa, ...decisions } = project;
  return sha256(JSON.stringify(ordered(decisions)));
}

async function settle(page, selector) {
  await page.waitForFunction(selector => {
    const node = document.querySelector(selector);
    return node && !node.hidden && getComputedStyle(node).display !== 'none' && node.getBoundingClientRect().width > 0;
  }, selector);
  await page.evaluate(async selector => {
    const node = document.querySelector(selector);
    await Promise.all(node.getAnimations({ subtree: true }).filter(a => a.effect?.getTiming().iterations !== Infinity)
      .map(a => a.finished.catch(() => {})));
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  }, selector);
}

async function inspectDesign(page, project) {
  return page.evaluate(project => {
    const issues = [], slide = document.querySelector('.slide.is-active');
    const add = (code, message) => issues.push({code, message, slide: slide.id, state: 0});
    const expected = project.slides?.find(s => s.id === slide.id);
    if (!expected || expected.role !== slide.dataset.slideRole || expected.tone !== (slide.dataset.tone || 'content'))
      add('design.role-tone', 'Rendered role/tone does not match the approved slide contract.');
    const themes = [...document.querySelectorAll('[data-theme-choice]')].map(b => b.dataset.themeChoice);
    if (JSON.stringify(themes) !== JSON.stringify(project.appearance?.available_themes))
      add('design.themes', 'Theme menu differs from available_themes.');
    const visible = node => node && !node.closest('[hidden]') && node.getBoundingClientRect().width > 0 &&
      ![node, ...ancestors(node)].some(n => { const s = getComputedStyle(n); return s.display === 'none' || s.visibility === 'hidden' || +s.opacity === 0; });
    function ancestors(node) { const values=[]; while(node.parentElement){node=node.parentElement;values.push(node);} return values; }
    for (const asset of project.design_contract?.assets || []) {
      if (asset.decision === 'remove' || !asset.slides?.includes(slide.id) || (asset.themes && !asset.themes.includes(document.body.dataset.theme))) continue;
      const node = [...slide.querySelectorAll('[data-asset-id]')].find(n => n.dataset.assetId === asset.id);
      if (!visible(node) || (node.tagName === 'IMG' && (!node.complete || !node.naturalWidth)))
        add('assets.not-visible', `Required asset ${asset.id} is missing, hidden or cannot load.`);
      if (node?.tagName === 'IMG' && asset.kind === 'logo' && getComputedStyle(node).objectFit !== 'contain')
        add('assets.logo-fit', `Logo ${asset.id} must preserve its proportions with object-fit: contain.`);
    }
    const scale = slide.getBoundingClientRect().width / 1920;
    for (const check of project.design_contract?.composition?.checks || []) {
      if (check.slide !== slide.id) continue;
      const nodes = (check.boxes || []).map(id => [...slide.querySelectorAll('[data-qa-box]')].find(n => n.dataset.qaBox === id));
      if (nodes.length < 2 || nodes.some(n => !visible(n))) { add('design.composition', `Missing comparison boxes for ${check.property}.`); continue; }
      const rects = nodes.map(n => n.getBoundingClientRect());
      const prop = check.property;
      const values = prop === 'gap-x' ? rects.slice(1).map((r,i) => r.left - rects[i].right)
        : prop === 'gap-y' ? rects.slice(1).map((r,i) => r.top - rects[i].bottom) : rects.map(r => r[prop]);
      const tolerance = Number(check.tolerance_px);
      if (!Number.isFinite(tolerance) || tolerance < 0 || tolerance > 24 || values.some(v => !Number.isFinite(v)) ||
          (Math.max(...values) - Math.min(...values)) / scale > tolerance ||
          (Number.isFinite(check.value_px) && values.some(v => Math.abs(v / scale - check.value_px) > tolerance)))
        add('design.composition', `Approved ${prop} alignment/spacing is not met for ${check.boxes.join(', ')}.`);
    }
    const profile = project.design_contract?.readability || {};
    const exception = {...(profile.by_role?.[expected?.role] || {}), ...((profile.exceptions || []).find(e => e.slide === slide.id && e.reason) || {})};
    const texts = [...slide.querySelectorAll('[data-edit-id]')].filter(visible);
    const words = texts.filter(n => !n.parentElement.closest('[data-edit-id]')).reduce((n,e) => n + e.textContent.trim().split(/\s+/).filter(Boolean).length, 0);
    if (words > (exception.max_words_per_slide || profile.max_words_per_slide || Infinity))
      add('design.readability-density', `${words} visible words exceed the approved ${profile.mode} profile; simplify before shrinking.`);
    const minimum = exception.supporting_text_min_px || profile.supporting_text_min_px;
    for (const text of texts.filter(n => n.matches('p,li,[data-typography-role="body"]') && !n.closest('footer,[data-qa-role="footer"]'))) {
      if (minimum && parseFloat(getComputedStyle(text).fontSize) < minimum)
        add('design.readability-size', `${text.dataset.editId} is below the approved supporting-text size (${minimum}px on stage).`);
    }
    return issues;
  }, project);
}

module.exports = { sha256, contractHash, settle, inspectDesign };
