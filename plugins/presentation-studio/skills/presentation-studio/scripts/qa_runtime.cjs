#!/usr/bin/env node
/* Rendered geometry, state, chrome, and brand QA for Presentation Studio decks. */

const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

const DEFAULT_VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'laptop', width: 1280, height: 720 },
  { name: 'phone_portrait', width: 390, height: 844 },
  { name: 'phone_landscape', width: 844, height: 390 },
];

function parseArgs(argv) {
  const args = {
    html: null,
    project: null,
    outputDir: null,
    chrome: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    screenshots: true,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--project') args.project = argv[++index];
    else if (value === '--output-dir') args.outputDir = argv[++index];
    else if (value === '--chrome') args.chrome = argv[++index];
    else if (value === '--no-screenshots') args.screenshots = false;
    else if (!args.html) args.html = value;
    else throw new Error(`Unexpected argument: ${value}`);
  }
  if (!args.html) {
    throw new Error('Usage: qa_runtime.cjs presentation.html [--project presentation-project.json] [--output-dir DIR] [--chrome PATH] [--no-screenshots]');
  }
  args.html = path.resolve(args.html);
  args.project = args.project ? path.resolve(args.project) : null;
  args.outputDir = path.resolve(args.outputDir || path.join(path.dirname(args.html), '.visual-qa'));
  return args;
}

function safeName(value) {
  return String(value).replace(/[^a-z0-9_-]+/gi, '-').replace(/^-|-$/g, '').toLowerCase();
}

function htmlEscape(value) {
  return String(value).replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[character]);
}

function readProject(args) {
  if (!args.project) return null;
  return JSON.parse(fs.readFileSync(args.project, 'utf8'));
}

function makeGallery(report, outputDir) {
  const cards = report.screenshots.map(item => `
    <article class="card" data-kind="${htmlEscape(item.kind)}">
      <img loading="lazy" src="${htmlEscape(path.relative(outputDir, item.path))}" alt="${htmlEscape(item.label)}">
      <div><strong>${htmlEscape(item.label)}</strong><span>${htmlEscape(item.kind)}</span></div>
    </article>`).join('');
  return `<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Presentation Studio · Visual QA</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#07111e;color:#eef3f8;font:14px/1.45 system-ui,sans-serif}header{position:sticky;top:0;z-index:2;padding:18px 24px;background:#07111ef2;border-bottom:1px solid #ffffff20;backdrop-filter:blur(18px)}h1{margin:0;font-size:22px}header p{margin:5px 0 0;color:#9eb0c2}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:18px;padding:22px}.card{overflow:hidden;border:1px solid #ffffff1c;border-radius:14px;background:#0d1c2c}.card img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain;background:#02070c}.card div{display:flex;justify-content:space-between;gap:12px;padding:11px 13px}.card span{color:#8fa2b5}
</style></head><body><header><h1>Presentation Studio · Revisión visual completa</h1><p>${report.summary.checks} checks · ${report.summary.failures} fallos · ${report.summary.reviewItems} elementos para revisión</p></header><main class="grid">${cards}</main></body></html>`;
}

async function preparePage(page, url, viewport) {
  await page.setViewportSize({ width: viewport.width, height: viewport.height });
  await page.goto(url, { waitUntil: 'load' });
  await page.evaluate(async () => {
    if (document.fonts?.ready) await document.fonts.ready;
  });
  await page.addStyleTag({ content: '*,*::before,*::after{animation-duration:1ms!important;transition-duration:1ms!important;animation-delay:0ms!important}' });
}

async function deckManifest(page) {
  return page.evaluate(() => ({
    project: (() => { try { return JSON.parse(document.querySelector('#presentation-project-data')?.textContent || '{}'); } catch (_error) { return {}; } })(),
    slides: [...document.querySelectorAll('.slide')].map(slide => ({
      id: slide.id,
      requiredStates: slide.querySelectorAll('[data-present-step="required"]').length,
    })),
  }));
}

async function gotoState(page, slideId, state) {
  await page.evaluate(({ slideId, state }) => {
    location.hash = `#${slideId}${state ? `/estado-${String(state).padStart(2, '0')}` : ''}`;
  }, { slideId, state });
  await page.waitForTimeout(45);
}

async function setTheme(page, theme) {
  await page.evaluate(themeName => {
    const button = document.querySelector(`[data-theme-choice="${themeName}"]`);
    if (button) button.click();
    else document.body.dataset.theme = themeName;
  }, theme);
  await page.waitForTimeout(20);
}

async function inspectActiveSlide(page, context) {
  return page.evaluate(({ state, mode, theme }) => {
    const EPSILON = 1.5;
    const slide = document.querySelector('.slide.is-active');
    const stage = document.querySelector('#deck-stage');
    const chrome = document.querySelector('#deck-chrome');
    const project = (() => { try { return JSON.parse(document.querySelector('#presentation-project-data')?.textContent || '{}'); } catch (_error) { return {}; } })();
    const issues = [];
    const review = [];

    function rect(element) {
      if (!element) return null;
      const value = element.getBoundingClientRect();
      return { left: value.left, top: value.top, right: value.right, bottom: value.bottom, width: value.width, height: value.height };
    }
    function visible(element) {
      if (!element) return false;
      for (let current = element; current && current.nodeType === 1; current = current.parentElement) {
        const currentStyle = getComputedStyle(current);
        if (currentStyle.display === 'none' || currentStyle.visibility === 'hidden' || Number(currentStyle.opacity) <= 0.01 || current.hidden) return false;
        if (current === slide) break;
      }
      const style = getComputedStyle(element);
      const value = element.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > 0.01 && value.width > 0.5 && value.height > 0.5 && !element.closest('[hidden]');
    }
    function intersection(a, b) {
      if (!a || !b) return null;
      const left = Math.max(a.left, b.left), top = Math.max(a.top, b.top);
      const right = Math.min(a.right, b.right), bottom = Math.min(a.bottom, b.bottom);
      if (right - left <= EPSILON || bottom - top <= EPSILON) return null;
      return { left, top, right, bottom, width: right - left, height: bottom - top, area: (right - left) * (bottom - top) };
    }
    function inside(inner, outer) {
      return inner.left >= outer.left - EPSILON && inner.top >= outer.top - EPSILON && inner.right <= outer.right + EPSILON && inner.bottom <= outer.bottom + EPSILON;
    }
    function label(element) {
      return element?.dataset.qaBox || element?.dataset.editId || element?.id || element?.className?.toString().split(/\s+/).filter(Boolean).slice(0, 2).join('.') || element?.tagName?.toLowerCase() || 'element';
    }
    function textRects(element) {
      const values = [];
      const visit = node => {
        if (node.nodeType === 3 && node.textContent.trim()) {
          const range = document.createRange();
          range.selectNodeContents(node);
          for (const value of range.getClientRects()) {
            if (value.width > .5 && value.height > .5) values.push({ left: value.left, top: value.top, right: value.right, bottom: value.bottom, width: value.width, height: value.height });
          }
          range.detach();
          return;
        }
        for (const child of node.childNodes || []) visit(child);
      };
      visit(element);
      return values;
    }
    function visualLines(element) {
      const groups = [];
      for (const value of textRects(element).sort((a, b) => a.top - b.top || a.left - b.left)) {
        let group = groups.find(item => Math.abs(item.top - value.top) <= 2.5 || Math.min(item.bottom, value.bottom) - Math.max(item.top, value.top) > Math.min(item.height, value.height) * .6);
        if (!group) {
          group = { ...value };
          groups.push(group);
        } else {
          group.left = Math.min(group.left, value.left); group.top = Math.min(group.top, value.top);
          group.right = Math.max(group.right, value.right); group.bottom = Math.max(group.bottom, value.bottom);
          group.width = group.right - group.left; group.height = group.bottom - group.top;
        }
      }
      return groups.sort((a, b) => a.top - b.top || a.left - b.left);
    }
    function unionRects(values) {
      if (!values.length) return null;
      const left = Math.min(...values.map(value => value.left)), top = Math.min(...values.map(value => value.top));
      const right = Math.max(...values.map(value => value.right)), bottom = Math.max(...values.map(value => value.bottom));
      return { left, top, right, bottom, width: right - left, height: bottom - top };
    }
    function paintedColor(value) {
      if (!value || value === 'transparent') return false;
      const alpha = value.match(/^rgba?\([^/]+(?:\/|,)\s*([\d.]+)\s*\)$/i);
      return !alpha || Number(alpha[1]) > 0.02;
    }
    function surfaceIntersects(element, overlap) {
      if (element.dataset.qaSafeArea === 'strict') return true;
      if (element.dataset.qaSafeArea === 'allow') return false;
      if (/^(IMG|SVG|CANVAS|VIDEO)$/.test(element.tagName)) return true;
      const style = getComputedStyle(element), value = rect(element);
      if (style.backgroundImage !== 'none' || paintedColor(style.backgroundColor)) return true;
      const borders = [
        [Number.parseFloat(style.borderTopWidth), style.borderTopStyle, style.borderTopColor, { left: value.left, top: value.top, right: value.right, bottom: value.top + Number.parseFloat(style.borderTopWidth || 0) }],
        [Number.parseFloat(style.borderRightWidth), style.borderRightStyle, style.borderRightColor, { left: value.right - Number.parseFloat(style.borderRightWidth || 0), top: value.top, right: value.right, bottom: value.bottom }],
        [Number.parseFloat(style.borderBottomWidth), style.borderBottomStyle, style.borderBottomColor, { left: value.left, top: value.bottom - Number.parseFloat(style.borderBottomWidth || 0), right: value.right, bottom: value.bottom }],
        [Number.parseFloat(style.borderLeftWidth), style.borderLeftStyle, style.borderLeftColor, { left: value.left, top: value.top, right: value.left + Number.parseFloat(style.borderLeftWidth || 0), bottom: value.bottom }],
      ];
      return borders.some(([width, borderStyle, color, borderRect]) => width > 0 && borderStyle !== 'none' && paintedColor(color) && intersection(borderRect, overlap));
    }
    function add(code, message, details = {}) {
      issues.push({ code, message, slide: slide?.id || '', state, mode, theme, ...details });
    }
    function resolvedColor(value) {
      const probe = document.createElement('span');
      probe.style.color = value;
      slide.appendChild(probe);
      const result = getComputedStyle(probe).color;
      probe.remove();
      return result;
    }
    function luminance(value) {
      const channels = value.match(/[\d.]+/g)?.slice(0, 3).map(Number);
      if (!channels || channels.length < 3) return null;
      const linear = channels.map(channel => { const normalized = channel / 255; return normalized <= .04045 ? normalized / 12.92 : ((normalized + .055) / 1.055) ** 2.4; });
      return .2126 * linear[0] + .7152 * linear[1] + .0722 * linear[2];
    }

    if (!slide || !stage) {
      add('runtime-active-slide', 'Active slide or stage is missing.');
      return { issues, review, stats: {} };
    }
    const slideRect = rect(slide), stageRect = rect(stage), chromeRect = visible(chrome) ? rect(chrome) : null;
    const renderScale = slideRect.width / 1920;
    const footer = slide.querySelector('[data-qa-role="footer"],.slide-footer');
    const footerRect = visible(footer) ? rect(footer) : null;
    const boxes = [...slide.querySelectorAll('[data-qa-box]')].filter(visible).map(element => ({ element, rect: rect(element), name: label(element), role: element.dataset.qaRole || '' }));
    const editables = [...slide.querySelectorAll('[data-edit-id]')].filter(visible);
    const texts = editables.flatMap(element => textRects(element).map(value => ({ element, rect: value, name: label(element) })));
    function typographyRole(element) {
      if (element.tagName === 'H1') return 'h1';
      if (element.tagName === 'H2') return 'h2';
      if (/^H[3-6]$/.test(element.tagName)) return 'h3';
      if (element.tagName === 'P') return 'body';
      return 'label';
    }
    function typographyBounds(element) {
      const fallback = { label: { min: 14, max: 180 }, body: { min: 18, max: 64 }, h3: { min: 24, max: 96 }, h2: { min: 36, max: 144 }, h1: { min: 48, max: 180 } };
      const role = typographyRole(element), configured = project.appearance?.typography?.bounds?.[role] || {}, defaults = fallback[role];
      const minimum = Number(configured.min), maximum = Number(configured.max);
      return { role, min: Number.isFinite(minimum) ? minimum : defaults.min, max: Number.isFinite(maximum) ? maximum : defaults.max };
    }

    const palette = project.appearance?.brand_palette || {}, strategy = project.appearance?.theme_strategy || {};
    if (palette.locked === true && strategy.preserve_brand_colors === true) {
      const actual = [resolvedColor('var(--accent)'), resolvedColor('var(--accent-2)')];
      const expected = [resolvedColor(palette.primary), resolvedColor(palette.secondary)];
      if (actual.some((value, index) => value !== expected[index])) add('brand-theme-color-shift', 'The active theme mutates the locked brand palette.', { actual, expected, palette: [palette.primary, palette.secondary] });
    }
    if (strategy.inverse_anchor_slides === true && (theme === 'light' || theme === 'dark')) {
      const background = getComputedStyle(slide).backgroundColor, value = luminance(background), anchor = slide.dataset.tone === 'anchor';
      const expectedLight = theme === 'light' ? !anchor : anchor;
      if (value !== null && ((expectedLight && value < .62) || (!expectedLight && value > .38))) add('theme-tone-polarity', `${anchor ? 'Anchor' : 'Content'} slide polarity is inconsistent with the ${theme} theme.`, { background, luminance: value, expectedLight, anchor });
    }

    if (!inside(slideRect, stageRect)) add('slide-stage', 'The active slide leaves the stage.', { slideRect, stageRect });
    for (const item of boxes) {
      if (!inside(item.rect, slideRect)) add('box-outside-slide', `${item.name} leaves the slide.`, { element: item.name, rect: item.rect });
      const element = item.element;
      if (element.scrollWidth > element.clientWidth + 2 || element.scrollHeight > element.clientHeight + 2) {
        const style = getComputedStyle(element);
        const clips = [style.overflow, style.overflowX, style.overflowY].some(value => ['hidden', 'clip', 'auto', 'scroll'].includes(value));
        const spills = [...element.querySelectorAll('[data-edit-id],[data-qa-box],img,svg,canvas,video')]
          .filter(child => child !== element && visible(child) && !inside(rect(child), item.rect)).map(label);
        const textSpills = [...element.querySelectorAll('[data-edit-id]')].filter(visible)
          .flatMap(child => textRects(child)).filter(value => !inside(value, item.rect));
        if (clips || spills.length || textSpills.length) {
          add('intrinsic-overflow', `${item.name} has clipped or overflowing visible content.`, { element: item.name, client: [element.clientWidth, element.clientHeight], scroll: [element.scrollWidth, element.scrollHeight], spills, textSpills: textSpills.length });
        }
      }
    }
    for (const item of texts) {
      if (!inside(item.rect, slideRect)) add('text-outside-slide', `${item.name} leaves the slide.`, { element: item.name, rect: item.rect });
    }

    const reportedTextPairs = new Set();
    for (let leftIndex = 0; leftIndex < texts.length; leftIndex += 1) {
      for (let rightIndex = leftIndex + 1; rightIndex < texts.length; rightIndex += 1) {
        const left = texts[leftIndex], right = texts[rightIndex];
        if (left.element === right.element || left.element.contains(right.element) || right.element.contains(left.element)) continue;
        const overlap = intersection(left.rect, right.rect);
        if (!overlap) continue;
        const pair = [left.name, right.name].sort().join('|');
        if (reportedTextPairs.has(pair)) continue;
        reportedTextPairs.add(pair);
        add('text-overlap', `${left.name} overlaps ${right.name}.`, { elements: [left.name, right.name], overlap });
      }
    }

    for (const element of editables) {
      const style = getComputedStyle(element), fontSize = Number.parseFloat(style.fontSize), bounds = typographyBounds(element);
      if (Number.isFinite(fontSize) && fontSize < bounds.min - .1) add('text-font-size-small', `${label(element)} uses ${fontSize.toFixed(1)} px, below the ${bounds.role} minimum of ${bounds.min} px.`, { element: label(element), fontSize, role: bounds.role, minimum: bounds.min });
      if (Number.isFinite(fontSize) && fontSize > bounds.max + .1) add('text-font-size-large', `${label(element)} uses ${fontSize.toFixed(1)} px, above the ${bounds.role} maximum of ${bounds.max} px.`, { element: label(element), fontSize, role: bounds.role, maximum: bounds.max });
      const linesForElement = visualLines(element);
      if (linesForElement.length < 2) continue;
      const lineHeight = Number.parseFloat(style.lineHeight);
      if (Number.isFinite(fontSize) && Number.isFinite(lineHeight) && fontSize > 0) {
        const ratio = lineHeight / fontSize, heading = /^H[1-6]$/.test(element.tagName);
        const compact = element.dataset.qaLineHeight === 'compact';
        const minimum = compact ? .95 : (heading ? .92 : 1.18), maximum = compact ? 1.35 : (heading ? 1.32 : 1.68);
        if (ratio < minimum) add('text-line-height-tight', `${label(element)} uses line-height ${ratio.toFixed(2)}, below ${minimum.toFixed(2)}.`, { element: label(element), ratio, minimum });
        if (ratio > maximum) add('text-line-height-loose', `${label(element)} uses line-height ${ratio.toFixed(2)}, above ${maximum.toFixed(2)}.`, { element: label(element), ratio, maximum });
        for (let index = 1; index < linesForElement.length; index += 1) {
          // Font ink boxes commonly overlap slightly even when their line boxes are
          // healthy (especially display serifs). Baseline separation below 80% of
          // the computed font size is a reliable signal of actual line collision.
          const separation = linesForElement[index].top - linesForElement[index - 1].top;
          const minimumSeparation = fontSize * renderScale * .8;
          if (separation < minimumSeparation - EPSILON) add('text-line-overlap', `${label(element)} has overlapping rendered lines.`, { element: label(element), line: index + 1, separation, minimumSeparation });
        }
      }
    }

    for (const stack of [...slide.querySelectorAll('[data-qa-text-stack]')].filter(visible)) {
      const stackNodes = editables.filter(element => element.closest('[data-qa-text-stack]') === stack)
        .map(element => ({ element, value: unionRects(visualLines(element)), style: getComputedStyle(element) })).filter(item => item.value);
      stackNodes.sort((a, b) => a.value.top - b.value.top || a.value.left - b.value.left);
      for (let index = 1; index < stackNodes.length; index += 1) {
        const previous = stackNodes[index - 1], currentNode = stackNodes[index];
        const horizontalOverlap = Math.max(0, Math.min(previous.value.right, currentNode.value.right) - Math.max(previous.value.left, currentNode.value.left));
        if (horizontalOverlap / Math.min(previous.value.width, currentNode.value.width) < .25 || currentNode.value.top < previous.value.top) continue;
        const gap = currentNode.value.top - previous.value.bottom;
        const previousFont = Number.parseFloat(previous.style.fontSize) * renderScale, currentFont = Number.parseFloat(currentNode.style.fontSize) * renderScale;
        const minimum = Math.max(2, Math.min(previousFont, currentFont) * .14);
        const maximum = Math.max(24 * renderScale, Math.max(previousFont, currentFont) * 2.4);
        if (gap >= 0 && gap < minimum) add('text-spacing-tight', `${label(previous.element)} and ${label(currentNode.element)} are too tightly spaced.`, { stack: label(stack), elements: [label(previous.element), label(currentNode.element)], gap, minimum });
        if (gap > maximum && stack.dataset.qaTextStack !== 'loose') review.push({ code: 'text-spacing-loose', message: `${label(previous.element)} and ${label(currentNode.element)} may be too far apart.`, slide: slide.id, state, stack: label(stack), elements: [label(previous.element), label(currentNode.element)], gap, maximum });
      }
    }

    for (let leftIndex = 0; leftIndex < boxes.length; leftIndex += 1) {
      for (let rightIndex = leftIndex + 1; rightIndex < boxes.length; rightIndex += 1) {
        const left = boxes[leftIndex], right = boxes[rightIndex];
        if (left.element.contains(right.element) || right.element.contains(left.element)) continue;
        if (left.element.dataset.qaOverlap === 'allow' || right.element.dataset.qaOverlap === 'allow') continue;
        const overlap = intersection(left.rect, right.rect);
        if (!overlap) continue;
        const ratio = overlap.area / Math.min(left.rect.width * left.rect.height, right.rect.width * right.rect.height);
        if (ratio > .008) add('box-overlap', `${left.name} overlaps ${right.name}.`, { elements: [left.name, right.name], overlap, ratio });
      }
    }

    for (const box of boxes) {
      for (const item of texts) {
        if (box.element === item.element || box.element.contains(item.element) || item.element.contains(box.element)) continue;
        const overlap = intersection(box.rect, item.rect);
        if (overlap && surfaceIntersects(box.element, overlap)) add('surface-text-overlap', `${box.name} visually overlaps ${item.name}.`, { surface: box.name, text: item.name, overlap });
      }
    }

    for (const protectedRegion of [{ name: 'footer', rect: footerRect }, { name: 'chrome', rect: chromeRect }]) {
      if (!protectedRegion.rect) continue;
      for (const item of boxes) {
        if (protectedRegion.name === 'footer' && (item.element === footer || footer?.contains(item.element))) continue;
        if (item.role === 'decoration' && item.element.dataset.qaOverlap === 'allow') continue;
        const overlap = intersection(item.rect, protectedRegion.rect);
        if (overlap && surfaceIntersects(item.element, overlap)) add('safe-area-overlap', `${item.name} paints into the ${protectedRegion.name} safe area.`, { element: item.name, region: protectedRegion.name, overlap });
      }
      for (const item of texts) {
        if (protectedRegion.name === 'footer' && footer?.contains(item.element)) continue;
        const overlap = intersection(item.rect, protectedRegion.rect);
        if (overlap) add('text-safe-area-overlap', `${item.name} is covered by the ${protectedRegion.name}.`, { element: item.name, region: protectedRegion.name, overlap });
      }
    }

    const lines = [...slide.querySelectorAll('[data-qa-line]')].filter(visible);
    for (const line of lines) {
      if (line.dataset.qaOverlap === 'allow') continue;
      const lineRect = rect(line);
      const clearance = Math.max(2, 4 * renderScale);
      const horizontal = lineRect.width >= lineRect.height;
      const lineProbe = horizontal
        ? { left: lineRect.left, right: lineRect.right, top: lineRect.top - clearance, bottom: lineRect.bottom + clearance, width: lineRect.width, height: lineRect.height + clearance * 2 }
        : { left: lineRect.left - clearance, right: lineRect.right + clearance, top: lineRect.top, bottom: lineRect.bottom, width: lineRect.width + clearance * 2, height: lineRect.height };
      for (const item of texts) {
        if (line.contains(item.element)) continue;
        const overlap = intersection(lineProbe, item.rect);
        if (overlap) add('line-through-text', `${label(line)} crosses ${item.name}.`, { line: label(line), text: item.name, overlap });
      }
    }

    const anchors = new Map([...slide.querySelectorAll('[data-qa-anchor]')].map(element => [element.dataset.qaAnchor, element]));
    for (const connector of [...slide.querySelectorAll('[data-qa-connector-for]')].filter(visible)) {
      const endpoints = connector.dataset.qaConnectorFor.split(/\s+/).filter(Boolean);
      const missing = endpoints.filter(name => !visible(anchors.get(name)));
      if (endpoints.length < 2 || missing.length) add('orphan-connector', `${label(connector)} is visible without all endpoints.`, { connector: label(connector), endpoints, missing });
      if (!missing.length && endpoints.length === 2 && connector.dataset.qaConnectorGeometry === 'strict') {
        const connectorRect = rect(connector), endpointRects = endpoints.map(name => rect(anchors.get(name)));
        const horizontal = connectorRect.width >= connectorRect.height, tolerance = Math.max(3, 8 * renderScale);
        if (horizontal) {
          endpointRects.sort((a, b) => a.left - b.left);
          const gaps = [Math.abs(connectorRect.left - endpointRects[0].right), Math.abs(connectorRect.right - endpointRects[1].left)];
          const centerY = connectorRect.top + connectorRect.height / 2;
          if (gaps.some(gap => gap > tolerance)) add('connector-endpoint-gap', `${label(connector)} does not terminate proportionally at its endpoints.`, { connector: label(connector), gaps, tolerance });
          if (endpointRects.some(value => centerY < value.top - tolerance || centerY > value.bottom + tolerance)) add('connector-axis-misalignment', `${label(connector)} is not aligned with its endpoint centers.`, { connector: label(connector), centerY, endpoints: endpointRects });
        } else {
          endpointRects.sort((a, b) => a.top - b.top);
          const gaps = [Math.abs(connectorRect.top - endpointRects[0].bottom), Math.abs(connectorRect.bottom - endpointRects[1].top)];
          const centerX = connectorRect.left + connectorRect.width / 2;
          if (gaps.some(gap => gap > tolerance)) add('connector-endpoint-gap', `${label(connector)} does not terminate proportionally at its endpoints.`, { connector: label(connector), gaps, tolerance });
          if (endpointRects.some(value => centerX < value.left - tolerance || centerX > value.right + tolerance)) add('connector-axis-misalignment', `${label(connector)} is not aligned with its endpoint centers.`, { connector: label(connector), centerX, endpoints: endpointRects });
        }
      }
    }

    const connectorGroups = new Map();
    for (const connector of [...slide.querySelectorAll('[data-qa-connector-group]')].filter(visible)) {
      const name = connector.dataset.qaConnectorGroup;
      if (!connectorGroups.has(name)) connectorGroups.set(name, []);
      connectorGroups.get(name).push(rect(connector));
    }
    for (const [name, values] of connectorGroups) {
      if (values.length < 2) continue;
      const horizontal = values.every(value => value.width >= value.height), lengths = values.map(value => horizontal ? value.width : value.height);
      const thicknesses = values.map(value => horizontal ? value.height : value.width), axes = values.map(value => horizontal ? value.top + value.height / 2 : value.left + value.width / 2);
      const lengthRatio = Math.max(...lengths) / Math.max(1, Math.min(...lengths));
      if (lengthRatio > 1.06 || Math.max(...thicknesses) - Math.min(...thicknesses) > 1.5 || Math.max(...axes) - Math.min(...axes) > Math.max(2, 3 * renderScale)) {
        add('connector-proportion', `Connector group ${name} is not visually proportional.`, { group: name, lengths, thicknesses, axes, lengthRatio });
      }
    }

    for (const sequence of [...slide.querySelectorAll('[data-qa-sequence]')].filter(visible)) {
      const items = [...sequence.querySelectorAll('[data-qa-item]')].filter(visible);
      if (sequence.dataset.qaComplete !== 'true') add('unfinished-sequence', `${label(sequence)} is not marked visually complete.`, { sequence: label(sequence) });
      if (items.length > 1 && !items.some(item => item.hasAttribute('data-qa-terminal'))) add('missing-terminal-treatment', `${label(sequence)} has no terminal item treatment.`, { sequence: label(sequence) });
    }

    const grid = slide.querySelector('.slide-grid');
    if (grid) {
      for (const child of [...grid.children].filter(visible)) {
        if (child.matches('.notes,[data-qa-box],[data-qa-role],[data-qa-overlap="allow"]')) continue;
        add('unannotated-major-block', `${label(child)} is a visible top-level block without QA semantics.`, { element: label(child) });
      }
    }

    const policy = project.brand?.usage_policy || {};
    const exception = (policy.exceptions || []).find(item => item.slide === slide.id) || {};
    const maxMarks = Number.isInteger(exception.max_visible_marks_per_slide) ? exception.max_visible_marks_per_slide : (Number.isInteger(policy.max_visible_marks_per_slide) ? policy.max_visible_marks_per_slide : 1);
    const maxTextWithMark = Number.isInteger(exception.max_text_mentions_when_mark_present) ? exception.max_text_mentions_when_mark_present : (Number.isInteger(policy.max_text_mentions_when_mark_present) ? policy.max_text_mentions_when_mark_present : 0);
    const marks = [...slide.querySelectorAll('[data-brand-mark]')].filter(visible);
    if (marks.length > maxMarks) add('brand-mark-density', `The slide has ${marks.length} visible brand marks; policy allows ${maxMarks}.`, { count: marks.length, maximum: maxMarks });
    const names = (policy.names || []).map(value => String(value).trim().toLocaleLowerCase()).filter(Boolean);
    const mentionNodes = editables.filter(element => !element.closest('[data-brand-mark]')).filter(element => names.some(name => element.textContent.toLocaleLowerCase().includes(name)));
    if (marks.length && mentionNodes.length > maxTextWithMark) add('brand-name-repetition', `A visible brand mark is repeated in ${mentionNodes.length} text element(s); policy allows ${maxTextWithMark}.`, { marks: marks.length, mentions: mentionNodes.map(label), maximum: maxTextWithMark });
    if (policy.footer !== 'branded-approved' && footer && names.some(name => footer.textContent.toLocaleLowerCase().includes(name))) add('branded-footer', 'The footer repeats the brand without an approved branded-footer policy.');
    if (policy.text_mentions_use_neutral_color !== false) {
      const rootStyle = getComputedStyle(slide);
      const accentColors = [rootStyle.getPropertyValue('--accent'), rootStyle.getPropertyValue('--accent-2')].map(value => value.trim()).filter(Boolean);
      for (const element of mentionNodes) {
        const color = getComputedStyle(element).color;
        const probe = document.createElement('span');
        probe.style.color = color;
        slide.appendChild(probe);
        const normalized = getComputedStyle(probe).color;
        probe.remove();
        const accentNormalized = accentColors.map(value => { const node = document.createElement('span'); node.style.color = value; slide.appendChild(node); const result = getComputedStyle(node).color; node.remove(); return result; });
        if (accentNormalized.includes(normalized) && element.dataset.brandMention !== 'allow-accent') add('brand-mention-accent', `${label(element)} styles a brand-name mention as an accent.`, { element: label(element), color: normalized });
      }
    }

    if (state === 0 && slide.querySelectorAll('[data-present-step="required"]').length) {
      const requiredSteps = [...slide.querySelectorAll('[data-present-step="required"]')];
      const visibleRequiredSteps = requiredSteps.filter(visible);
      const contentArea = boxes.filter(item => item.role !== 'header' && item.role !== 'footer' && item.role !== 'decoration').reduce((sum, item) => sum + item.rect.width * item.rect.height, 0);
      const ratio = contentArea / (slideRect.width * slideRect.height);
      if (!visibleRequiredSteps.length && slide.dataset.qaStateZero !== 'intentional') {
        add('sparse-state-zero', 'State zero hides every required progressive element and appears unfinished.', { requiredSteps: requiredSteps.length, visibleRequiredSteps: 0, ratio });
      } else if (ratio < .07) {
        review.push({ code: 'sparse-state-zero', message: 'State zero is visually sparse and requires completion review.', slide: slide.id, state, ratio, requiredSteps: requiredSteps.length, visibleRequiredSteps: visibleRequiredSteps.length });
      }
    }

    return {
      issues,
      review,
      stats: { boxes: boxes.length, textRects: texts.length, marks: marks.length, mentions: mentionNodes.length },
    };
  }, context);
}

async function inspectRuntimeMenu(page, mode) {
  await page.evaluate(requestedMode => {
    document.body.dataset.viewMode = requestedMode;
    const trigger = document.querySelector('#menu-trigger');
    const menu = document.querySelector('#control-menu');
    if (menu?.hidden) trigger?.click();
  }, mode);
  await page.waitForTimeout(35);
  return page.evaluate(requestedMode => {
    const failures = [], add = (code, message, details = {}) => failures.push({ code, message, slide: 'runtime-menu', state: 0, mode: requestedMode, theme: document.body.dataset.theme, ...details });
    const visible = element => { if (!element) return false; const style = getComputedStyle(element), value = element.getBoundingClientRect(); return !element.hidden && style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > .01 && value.width > .5 && value.height > .5; };
    const menu = document.querySelector('#control-menu'), menuRect = menu?.getBoundingClientRect();
    if (!visible(menu)) add('runtime-menu-hidden', `The control menu is not visible in ${requestedMode} mode.`);
    if (menuRect && (menuRect.left < -1 || menuRect.top < -1 || menuRect.right > innerWidth + 1 || menuRect.bottom > innerHeight + 1)) add('runtime-menu-overflow', 'The control menu leaves the desktop viewport.', { rect: { left: menuRect.left, top: menuRect.top, right: menuRect.right, bottom: menuRect.bottom }, viewport: { width: innerWidth, height: innerHeight } });
    const authorHeading = [...document.querySelectorAll('#control-menu h2')].find(element => element.textContent.trim() === 'Autor');
    if (!visible(authorHeading)) add('author-menu-discoverability', `The Author section is hidden in ${requestedMode} mode.`);
    for (const id of ['toggle-edit', 'edit-typography', 'save', 'save-as', 'toggle-author-view']) if (!visible(document.getElementById(id))) add('author-menu-discoverability', `${id} is hidden in ${requestedMode} mode.`, { element: id });
    for (const button of [...document.querySelectorAll('#control-menu button[data-shortcut]')].filter(visible)) {
      const shortcut = button.querySelector('.menu-shortcut');
      if (!shortcut || shortcut.textContent.trim() !== button.dataset.shortcut) add('menu-shortcut-label', `${button.id || button.textContent.trim()} does not show its implemented shortcut.`, { element: button.id || '', expected: button.dataset.shortcut, actual: shortcut?.textContent.trim() || '' });
    }
    return failures;
  }, mode);
}

async function inspectTypographyEditor(page) {
  await page.evaluate(() => {
    document.body.dataset.viewMode = 'author';
    if (!document.body.classList.contains('edit-mode')) document.querySelector('#toggle-edit')?.click();
    document.querySelector('#edit-typography')?.click();
    const target = document.querySelector('.slide.is-active h1[data-edit-id]') || document.querySelector('.slide.is-active h2[data-edit-id]') || document.querySelector('.slide.is-active p[data-edit-id]') || document.querySelector('.slide.is-active [data-edit-id]');
    target?.click();
  });
  await page.waitForTimeout(45);
  return page.evaluate(() => {
    const failures = [], add = (code, message, details = {}) => failures.push({ code, message, slide: 'typography-editor', state: 0, mode: 'author', theme: document.body.dataset.theme, ...details });
    const visible = element => { if (!element) return false; const style = getComputedStyle(element), value = element.getBoundingClientRect(); return !element.hidden && style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > .01 && value.width > .5 && value.height > .5; };
    const dialog = document.querySelector('#typography-dialog'), target = document.querySelector('.slide.is-active .typography-target');
    if (!visible(dialog) || !dialog.open) add('typography-editor-hidden', 'The typography editor does not open for a selected editable text.');
    if (!target) add('typography-target-missing', 'The typography editor does not preserve a visible selected target.');
    const required = ['type-family', 'type-weight', 'type-size', 'type-size-number', 'type-leading', 'type-leading-number', 'type-tracking', 'type-tracking-number', 'type-color', 'type-color-auto', 'type-italic', 'reset-typography'];
    for (const id of required) if (!visible(document.getElementById(id))) add('typography-control-missing', `${id} is not visible in the typography editor.`, { element: id });
    if (document.querySelectorAll('.align-button').length !== 3) add('typography-alignment-controls', 'The typography editor must expose left, center, and right alignment.');
    const size = document.querySelector('#type-size-number'), minimum = Number(size?.min), maximum = Number(size?.max), value = Number(size?.value);
    if (!(Number.isFinite(minimum) && Number.isFinite(maximum) && minimum < maximum && value >= minimum && value <= maximum)) add('typography-size-bounds', 'The selected text does not expose a valid semantic font-size range.', { minimum, maximum, value });
    const families = [...document.querySelectorAll('#type-family option')];
    if (!families.length || families.some(option => !option.value || !option.textContent.trim())) add('typography-family-options', 'Approved typography families are missing or incomplete.');
    return failures;
  });
}

async function inspectContextualTextToolbar(page, viewport) {
  await page.evaluate(() => {
    document.body.dataset.viewMode = 'author';
    if (!document.body.classList.contains('edit-mode')) document.querySelector('#toggle-edit')?.click();
    const target = document.querySelector('.slide.is-active h1[data-edit-id]') || document.querySelector('.slide.is-active h2[data-edit-id]') || document.querySelector('.slide.is-active p[data-edit-id]') || document.querySelector('.slide.is-active [data-edit-id]');
    target?.click();
  });
  await page.waitForTimeout(55);
  return page.evaluate(({ viewportName }) => {
    const failures = [], add = (code, message, details = {}) => failures.push({ code, message, slide: 'contextual-text-toolbar', state: 0, mode: 'author', theme: document.body.dataset.theme, ...details });
    const visible = element => { if (!element) return false; const style = getComputedStyle(element), value = element.getBoundingClientRect(); return !element.hidden && style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > .01 && value.width > .5 && value.height > .5; };
    const toolbar = document.querySelector('#element-toolbar'), target = document.querySelector('.slide.is-active .typography-target');
    const toolbarRect = toolbar?.getBoundingClientRect(), targetRect = target?.getBoundingClientRect();
    if (!visible(toolbar) || toolbar?.dataset.mode !== 'text') add('contextual-text-toolbar-hidden', 'Clicking editable text does not open the contextual text toolbar.');
    if (!target) add('contextual-text-target-missing', 'Clicking editable text does not preserve the selected component.');
    if (toolbarRect && (toolbarRect.left < -1 || toolbarRect.top < -1 || toolbarRect.right > innerWidth + 1 || toolbarRect.bottom > innerHeight + 1)) add('contextual-toolbar-overflow', 'The contextual text toolbar leaves the viewport.', { viewportName, rect: { left: toolbarRect.left, top: toolbarRect.top, right: toolbarRect.right, bottom: toolbarRect.bottom } });
    if (viewportName === 'desktop' && toolbar && toolbar.scrollWidth > toolbar.clientWidth + 2) add('contextual-toolbar-clipped-controls', 'The contextual text toolbar requires horizontal scrolling on desktop.', { scrollWidth: toolbar.scrollWidth, clientWidth: toolbar.clientWidth });
    if (viewportName === 'desktop' && toolbarRect && targetRect) {
      const gap = Math.min(Math.abs(toolbarRect.top - targetRect.bottom), Math.abs(targetRect.top - toolbarRect.bottom));
      if (gap > 80) add('contextual-toolbar-distance', 'The contextual text toolbar is not positioned close to the selected text.', { gap });
    }
    const required = ['context-type-family', 'context-type-size', 'context-type-color', 'context-color-auto', 'context-bold', 'context-italic', 'context-align', 'context-more-type', 'context-reset-type'];
    for (const id of required) if (!visible(document.getElementById(id))) add('contextual-text-control-missing', `${id} is not visible in the contextual text toolbar.`, { element: id });
    const preview = document.querySelector('#element-toolbar-preview')?.textContent.trim() || '';
    if (!preview || (target?.textContent.trim() && !preview.includes(target.textContent.trim().slice(0, Math.min(18, target.textContent.trim().length))))) add('contextual-text-preview', 'The toolbar does not identify the selected text.', { preview });
    const size = document.querySelector('#context-type-size'), minimum = Number(size?.min), maximum = Number(size?.max);
    if (!(Number.isFinite(minimum) && Number.isFinite(maximum) && minimum < maximum)) add('contextual-size-bounds', 'Contextual font size has no valid semantic bounds.', { minimum, maximum });
    if (target && size) {
      size.value = String(maximum + 40); size.dispatchEvent(new Event('change', { bubbles: true }));
      if (Math.round(parseFloat(target.style.fontSize)) !== maximum) add('contextual-size-clamp', 'Contextual font size is not clamped to the semantic maximum.', { expected: maximum, actual: target.style.fontSize });
      const color = document.querySelector('#context-type-color'); color.value = '#b53148'; color.dispatchEvent(new Event('input', { bubbles: true }));
      if (!target.style.color) add('contextual-text-color', 'Contextual text color does not apply to the selected component.');
      const family = document.querySelector('#context-type-family'); if (family.options.length > 1) family.selectedIndex = 1; family.dispatchEvent(new Event('change', { bubbles: true }));
      if (!target.dataset.typographyFamily) add('contextual-text-family', 'Contextual font family does not apply to the selected component.');
      document.querySelector('#context-reset-type')?.click();
      if (target.style.fontSize || target.style.color) add('contextual-text-reset', 'Contextual text reset does not restore the element baseline.', { style: target.getAttribute('style') || '' });
    }
    return failures;
  }, { viewportName: viewport.name });
}

async function inspectContextualVisualToolbar(page, viewport) {
  await page.evaluate(() => {
    document.body.dataset.viewMode = 'author';
    if (!document.body.classList.contains('edit-mode')) document.querySelector('#toggle-edit')?.click();
    const target = document.querySelector('.slide.is-active [data-style-id]');
    target?.click();
  });
  await page.waitForTimeout(55);
  return page.evaluate(({ viewportName }) => {
    const failures = [], add = (code, message, details = {}) => failures.push({ code, message, slide: 'contextual-visual-toolbar', state: 0, mode: 'author', theme: document.body.dataset.theme, ...details });
    const visible = element => { if (!element) return false; const style = getComputedStyle(element), value = element.getBoundingClientRect(); return !element.hidden && style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > .01 && value.width > .5 && value.height > .5; };
    const toolbar = document.querySelector('#element-toolbar'), target = document.querySelector('.slide.is-active .element-style-target'), toolbarRect = toolbar?.getBoundingClientRect();
    if (!visible(toolbar) || toolbar?.dataset.mode !== 'visual') add('contextual-visual-toolbar-hidden', 'Clicking a styleable component does not open the visual toolbar.');
    if (!target) add('contextual-visual-target-missing', 'The visual component is not visibly selected.');
    if (toolbarRect && (toolbarRect.left < -1 || toolbarRect.top < -1 || toolbarRect.right > innerWidth + 1 || toolbarRect.bottom > innerHeight + 1)) add('contextual-toolbar-overflow', 'The contextual visual toolbar leaves the viewport.', { viewportName, rect: { left: toolbarRect.left, top: toolbarRect.top, right: toolbarRect.right, bottom: toolbarRect.bottom } });
    if (viewportName === 'desktop' && toolbar && toolbar.scrollWidth > toolbar.clientWidth + 2) add('contextual-toolbar-clipped-controls', 'The contextual visual toolbar requires horizontal scrolling on desktop.', { scrollWidth: toolbar.scrollWidth, clientWidth: toolbar.clientWidth });
    const required = ['context-fill-color', 'context-fill-none', 'context-border-color', 'context-border-width', 'context-border-style', 'context-radius', 'context-shadow', 'context-opacity', 'context-reset-visual'];
    for (const id of required) if (!visible(document.getElementById(id))) add('contextual-visual-control-missing', `${id} is not visible in the contextual visual toolbar.`, { element: id });
    if (target) {
      const fill = document.querySelector('#context-fill-color'); fill.value = '#17304a'; fill.dispatchEvent(new Event('input', { bubbles: true }));
      const border = document.querySelector('#context-border-color'); border.value = '#39d4c7'; border.dispatchEvent(new Event('input', { bubbles: true }));
      const width = document.querySelector('#context-border-width'); width.value = '3'; width.dispatchEvent(new Event('change', { bubbles: true }));
      const radius = document.querySelector('#context-radius'); radius.value = '24'; radius.dispatchEvent(new Event('change', { bubbles: true }));
      const shadow = document.querySelector('#context-shadow'); shadow.value = 'medium'; shadow.dispatchEvent(new Event('change', { bubbles: true }));
      const opacity = document.querySelector('#context-opacity'); opacity.value = '80'; opacity.dispatchEvent(new Event('input', { bubbles: true }));
      if (!target.style.backgroundColor || target.style.borderWidth !== '3px' || target.style.borderRadius !== '24px' || !target.style.boxShadow || target.style.opacity !== '0.8') add('contextual-visual-apply', 'One or more visual style controls do not apply to the selected component.', { style: target.getAttribute('style') || '' });
      document.querySelector('#context-reset-visual')?.click();
      if (target.style.backgroundColor || target.style.borderWidth || target.style.borderRadius || target.style.boxShadow || target.style.opacity) add('contextual-visual-reset', 'Visual style reset does not restore the component baseline.', { style: target.getAttribute('style') || '' });
    }
    return failures;
  }, { viewportName: viewport.name });
}

async function capture(page, outputDir, label, kind, screenshots, enabled) {
  if (!enabled) return;
  const file = path.join(outputDir, `${safeName(label)}.png`);
  await page.screenshot({ path: file, fullPage: false });
  screenshots.push({ path: file, label, kind });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!fs.existsSync(args.html)) throw new Error(`HTML not found: ${args.html}`);
  fs.mkdirSync(args.outputDir, { recursive: true });
  const projectFile = readProject(args);
  const browser = await chromium.launch({ headless: true, executablePath: args.chrome });
  const context = await browser.newContext({ reducedMotion: 'reduce' });
  const baseUrl = pathToFileURL(args.html).href;
  const report = { html: args.html, project: args.project, generatedAt: new Date().toISOString(), runs: [], failures: [], review: [], screenshots: [] };
  try {
    const manifestPage = await context.newPage();
    await preparePage(manifestPage, baseUrl, DEFAULT_VIEWPORTS[0]);
    const manifest = await deckManifest(manifestPage);
    await manifestPage.close();
    const project = projectFile || manifest.project;
    const configured = project.visual_qa?.required_viewports || DEFAULT_VIEWPORTS;
    const viewports = DEFAULT_VIEWPORTS.map(fallback => configured.find(item => item.name === fallback.name) || fallback);

    for (const viewport of viewports) {
      const page = await context.newPage();
      await preparePage(page, baseUrl, viewport);
      for (const slide of manifest.slides) {
        for (let state = 0; state <= slide.requiredStates; state += 1) {
          await gotoState(page, slide.id, state);
          const result = await inspectActiveSlide(page, { state, mode: 'audience', theme: await page.$eval('body', body => body.dataset.theme) });
          const label = `${viewport.name}-audience-${slide.id}-estado-${String(state).padStart(2, '0')}`;
          report.runs.push({ label, viewport, slide: slide.id, state, mode: 'audience', theme: await page.$eval('body', body => body.dataset.theme), ...result.stats });
          report.failures.push(...result.issues.map(issue => ({ viewport: viewport.name, ...issue })));
          report.review.push(...result.review.map(issue => ({ viewport: viewport.name, ...issue })));
          await capture(page, args.outputDir, label, 'all-states', report.screenshots, args.screenshots);
        }
      }
      await page.close();
    }

    for (const mode of ['audience', 'author']) {
      const menuPage = await context.newPage();
      await preparePage(menuPage, mode === 'author' ? `${baseUrl}?author=1` : baseUrl, DEFAULT_VIEWPORTS[0]);
      const failures = await inspectRuntimeMenu(menuPage, mode);
      const label = `desktop-${mode}-runtime-menu`;
      report.runs.push({ label, viewport: DEFAULT_VIEWPORTS[0], slide: 'runtime-menu', state: 0, mode, theme: await menuPage.$eval('body', body => body.dataset.theme), menuChecks: true });
      report.failures.push(...failures.map(issue => ({ viewport: 'desktop', ...issue })));
      await capture(menuPage, args.outputDir, label, 'runtime-menu', report.screenshots, args.screenshots);
      await menuPage.close();
    }

    const typographyPage = await context.newPage();
    await preparePage(typographyPage, `${baseUrl}?author=1`, DEFAULT_VIEWPORTS[0]);
    const typographyFailures = await inspectTypographyEditor(typographyPage);
    const typographyLabel = 'desktop-author-typography-editor';
    report.runs.push({ label: typographyLabel, viewport: DEFAULT_VIEWPORTS[0], slide: 'typography-editor', state: 0, mode: 'author', theme: await typographyPage.$eval('body', body => body.dataset.theme), typographyChecks: true });
    report.failures.push(...typographyFailures.map(issue => ({ viewport: 'desktop', ...issue })));
    await capture(typographyPage, args.outputDir, typographyLabel, 'typography-editor', report.screenshots, args.screenshots);
    await typographyPage.close();

    for (const viewport of [DEFAULT_VIEWPORTS[0], DEFAULT_VIEWPORTS[2]]) {
      const textToolbarPage = await context.newPage();
      await preparePage(textToolbarPage, `${baseUrl}?author=1`, viewport);
      const failures = await inspectContextualTextToolbar(textToolbarPage, viewport);
      const label = `${viewport.name}-author-contextual-text-toolbar`;
      report.runs.push({ label, viewport, slide: 'contextual-text-toolbar', state: 0, mode: 'author', theme: await textToolbarPage.$eval('body', body => body.dataset.theme), contextualTextChecks: true });
      report.failures.push(...failures.map(issue => ({ viewport: viewport.name, ...issue })));
      await capture(textToolbarPage, args.outputDir, label, 'contextual-text-toolbar', report.screenshots, args.screenshots);
      await textToolbarPage.close();

      const visualToolbarPage = await context.newPage();
      await preparePage(visualToolbarPage, `${baseUrl}?author=1`, viewport);
      const visualFailures = await inspectContextualVisualToolbar(visualToolbarPage, viewport);
      const visualLabel = `${viewport.name}-author-contextual-visual-toolbar`;
      report.runs.push({ label: visualLabel, viewport, slide: 'contextual-visual-toolbar', state: 0, mode: 'author', theme: await visualToolbarPage.$eval('body', body => body.dataset.theme), contextualVisualChecks: true });
      report.failures.push(...visualFailures.map(issue => ({ viewport: viewport.name, ...issue })));
      await capture(visualToolbarPage, args.outputDir, visualLabel, 'contextual-visual-toolbar', report.screenshots, args.screenshots);
      await visualToolbarPage.close();
    }

    const authorPage = await context.newPage();
    await preparePage(authorPage, `${baseUrl}?author=1`, DEFAULT_VIEWPORTS[0]);
    for (const slide of manifest.slides) {
      await gotoState(authorPage, slide.id, slide.requiredStates);
      const result = await inspectActiveSlide(authorPage, { state: slide.requiredStates, mode: 'author', theme: await authorPage.$eval('body', body => body.dataset.theme) });
      const label = `desktop-author-${slide.id}-final`;
      report.runs.push({ label, viewport: DEFAULT_VIEWPORTS[0], slide: slide.id, state: slide.requiredStates, mode: 'author', theme: await authorPage.$eval('body', body => body.dataset.theme), ...result.stats });
      report.failures.push(...result.issues.map(issue => ({ viewport: 'desktop', ...issue })));
      report.review.push(...result.review.map(issue => ({ viewport: 'desktop', ...issue })));
      await capture(authorPage, args.outputDir, label, 'author-final', report.screenshots, args.screenshots);
    }
    await authorPage.close();

    const themePage = await context.newPage();
    await preparePage(themePage, baseUrl, DEFAULT_VIEWPORTS[0]);
    for (const theme of ['light', 'dark', 'custom']) {
      await setTheme(themePage, theme);
      for (const slide of manifest.slides) {
        await gotoState(themePage, slide.id, slide.requiredStates);
        const result = await inspectActiveSlide(themePage, { state: slide.requiredStates, mode: 'audience', theme });
        const label = `desktop-theme-${theme}-${slide.id}-final`;
        report.runs.push({ label, viewport: DEFAULT_VIEWPORTS[0], slide: slide.id, state: slide.requiredStates, mode: 'audience', theme, ...result.stats });
        report.failures.push(...result.issues.map(issue => ({ viewport: 'desktop', ...issue })));
        report.review.push(...result.review.map(issue => ({ viewport: 'desktop', ...issue })));
        await capture(themePage, args.outputDir, label, 'theme-final', report.screenshots, args.screenshots);
      }
    }
    await themePage.close();
  } finally {
    await browser.close();
  }

  const uniqueFailures = [...new Map(report.failures.map(item => [JSON.stringify(item), item])).values()];
  const uniqueReview = [...new Map(report.review.map(item => [JSON.stringify(item), item])).values()];
  report.failures = uniqueFailures;
  report.review = uniqueReview;
  report.summary = {
    checks: report.runs.length,
    failures: report.failures.length,
    reviewItems: report.review.length,
    screenshots: report.screenshots.length,
  };
  fs.writeFileSync(path.join(args.outputDir, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  fs.writeFileSync(path.join(args.outputDir, 'review.html'), makeGallery(report, args.outputDir));
  console.log(`Rendered visual QA: ${report.summary.checks} states, ${report.summary.failures} failure(s), ${report.summary.reviewItems} review item(s), ${report.summary.screenshots} screenshot(s)`);
  console.log(path.join(args.outputDir, 'report.json'));
  if (report.failures.length) {
    for (const failure of report.failures.slice(0, 40)) console.error(`FAIL [${failure.viewport}/${failure.slide}/state-${failure.state}] ${failure.code}: ${failure.message}`);
    if (report.failures.length > 40) console.error(`... ${report.failures.length - 40} additional failure(s) in report.json`);
    process.exitCode = 1;
  }
}

main().catch(error => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
