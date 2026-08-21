#!/usr/bin/env node
/* Rendered loading, responsive-layout, and embedded-slide QA for Presentation Studio comparison galleries. */
'use strict';

const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'laptop', width: 1280, height: 720 },
  { name: 'phone_portrait', width: 390, height: 844 },
  { name: 'phone_landscape', width: 844, height: 390 },
];

function parseArgs(argv) {
  const args = { html: '', outputDir: '', chrome: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', screenshots: true };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (!args.html && !value.startsWith('--')) args.html = path.resolve(value);
    else if (value === '--output-dir') args.outputDir = path.resolve(argv[++index]);
    else if (value === '--chrome') args.chrome = argv[++index];
    else if (value === '--no-screenshots') args.screenshots = false;
    else throw new Error(`Unknown argument: ${value}`);
  }
  if (!args.html) throw new Error('Usage: qa_gallery.cjs visual-options.html [--output-dir DIR] [--chrome PATH] [--no-screenshots]');
  if (!args.outputDir) args.outputDir = path.join(path.dirname(args.html), 'gallery-qa');
  return args;
}

function safeName(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

async function inspectGallery(page, viewport, optionIndex) {
  const outer = await page.evaluate(({ viewportName, optionIndex: selectedOption }) => {
    const failures = [];
    const add = (code, message, details = {}) => failures.push({ code, message, viewport: viewportName, option: selectedOption, ...details });
    const panel = document.querySelector(`.option-panel:not([hidden])`);
    if (!panel) return [{ code: 'active-panel', message: 'No gallery option is visible.', viewport: viewportName, option: selectedOption }];
    const cards = [...panel.querySelectorAll('.preview-card')], labels = cards.map(card => card.querySelector('.preview-name')?.textContent.trim() || '');
    if (cards.length < 2 || cards.length > 3) add('preview-count', `The active option contains ${cards.length} previews; expected two or three.`);
    if (new Set(labels).size !== labels.length || labels.some(label => !/^Opción [A-C]-\d+$/.test(label))) add('preview-labels', 'Preview labels must be unique and use “Opción A-1” notation.', { labels });
    if (document.documentElement.scrollWidth > innerWidth + 2) add('horizontal-overflow', 'The gallery causes horizontal viewport overflow.', { scrollWidth: document.documentElement.scrollWidth, innerWidth });
    for (const [index, card] of cards.entries()) {
      const cardRect = card.getBoundingClientRect(), frame = card.querySelector('.frame'), frameRect = frame.getBoundingClientRect(), iframe = card.querySelector('iframe');
      if (cardRect.left < -1 || cardRect.right > innerWidth + 1) add('card-outside-viewport', `Preview ${index + 1} leaves the viewport.`, { rect: { left: cardRect.left, right: cardRect.right, width: cardRect.width } });
      if (Math.abs(frameRect.width / frameRect.height - 16 / 9) > .025) add('preview-aspect', `Preview ${index + 1} does not preserve 16:9.`, { width: frameRect.width, height: frameRect.height });
      if (iframe.dataset.loaded !== 'true' || card.classList.contains('is-loading') || card.classList.contains('load-error')) add('preview-load', `Preview ${index + 1} did not finish loading.`, { loaded: iframe.dataset.loaded || '', classes: card.className });
    }
    for (const [index, button] of [...document.querySelectorAll('[role="tab"]')].entries()) {
      const value = button.getBoundingClientRect();
      if (value.height < 44 || value.width < 44) add('tab-target', `Option tab ${index + 1} is smaller than 44px.`, { width: value.width, height: value.height });
    }
    if (innerWidth <= 900 && cards.length > 1) {
      const values = cards.map(card => card.getBoundingClientRect());
      if (values.slice(1).some((value, index) => value.top < values[index].bottom - 1)) add('responsive-columns', 'Compact gallery previews do not form a single readable column.');
    }
    return failures;
  }, { viewportName: viewport.name, optionIndex });

  const embedded = [];
  const frames = page.locator('.option-panel:not([hidden]) iframe[data-ppt-preview="true"]');
  for (let index = 0; index < await frames.count(); index += 1) {
    const handle = await frames.nth(index).elementHandle();
    const frame = await handle.contentFrame();
    if (!frame) {
      embedded.push({ code: 'preview-frame', message: `Preview ${index + 1} has no document frame.`, viewport: viewport.name, option: optionIndex });
      continue;
    }
    const result = await frame.evaluate(({ viewportName, selectedOption, previewIndex }) => {
      const visible = element => {
        const style = getComputedStyle(element), value = element.getBoundingClientRect();
        return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > .01 && value.width > .5 && value.height > .5;
      };
      const slides = [...document.querySelectorAll('.slide')].filter(visible), stage = document.querySelector('#deck-stage'), chrome = document.querySelector('#deck-chrome');
      const failures = [], add = (code, message, details = {}) => failures.push({ code, message, viewport: viewportName, option: selectedOption, preview: previewIndex, ...details });
      if (slides.length !== 1) add('embedded-visible-slide', `Preview ${previewIndex} has ${slides.length} visible slides; expected one.`);
      if (!slides[0]?.textContent.trim()) add('embedded-empty-slide', `Preview ${previewIndex} has no visible slide text.`);
      const required = [...(slides[0]?.querySelectorAll('[data-present-step="required"]') || [])];
      const subdued = required.filter(element => { const style = getComputedStyle(element); return style.visibility === 'hidden' || Number(style.opacity) < .95 || element.classList.contains('step-hidden'); });
      if (subdued.length) add('embedded-required-state-not-final', `Preview ${previewIndex} leaves ${subdued.length} required element(s) hidden or visually subdued.`, { required: required.length, subdued: subdued.length });
      if (!stage) add('embedded-stage', `Preview ${previewIndex} is missing the protected stage.`);
      else {
        const value = stage.getBoundingClientRect();
        const widthUse = value.width / innerWidth, heightUse = value.height / innerHeight;
        const centeredX = Math.abs(value.left - (innerWidth - value.width) / 2) <= 2;
        const centeredY = Math.abs(value.top - (innerHeight - value.height) / 2) <= 2;
        if (widthUse < .96 || heightUse < .96 || !centeredX || !centeredY) {
          add('embedded-scale', `Preview ${previewIndex} does not fill and center within its 16:9 frame.`, { stage: { left: value.left, top: value.top, width: value.width, height: value.height }, frameViewport: { width: innerWidth, height: innerHeight }, widthUse, heightUse, centeredX, centeredY });
        }
      }
      if (chrome && visible(chrome)) add('embedded-chrome', `Preview ${previewIndex} exposes presentation controls inside the gallery.`);
      return failures;
    }, { viewportName: viewport.name, selectedOption: optionIndex, previewIndex: index + 1 });
    embedded.push(...result);
  }
  return [...outer, ...embedded];
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!fs.existsSync(args.html)) throw new Error(`Gallery not found: ${args.html}`);
  fs.mkdirSync(args.outputDir, { recursive: true });
  const browser = await chromium.launch({ headless: true, executablePath: args.chrome });
  const report = { html: args.html, generatedAt: new Date().toISOString(), runs: [], failures: [], screenshots: [] };
  try {
    for (const viewport of VIEWPORTS) {
      const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height }, reducedMotion: 'reduce' });
      const consoleErrors = [];
      page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
      page.on('pageerror', error => consoleErrors.push(error.message));
      await page.goto(pathToFileURL(args.html).href, { waitUntil: 'load' });
      await page.waitForSelector('[role="tab"]');
      const optionCount = await page.locator('[role="tab"]').count();
      for (let optionIndex = 0; optionIndex < optionCount; optionIndex += 1) {
        await page.locator('[role="tab"]').nth(optionIndex).click();
        await page.waitForFunction(() => {
          const frames = [...document.querySelectorAll('.option-panel:not([hidden]) iframe[data-ppt-preview="true"]')];
          return frames.length >= 2 && frames.every(frame => frame.dataset.loaded === 'true');
        }, null, { timeout: 12000 });
        await page.waitForTimeout(80);
        const failures = await inspectGallery(page, viewport, optionIndex + 1);
        report.failures.push(...failures);
        const label = `${viewport.name}-option-${optionIndex + 1}`;
        report.runs.push({ label, viewport, option: optionIndex + 1, failures: failures.length });
        if (args.screenshots) {
          const file = path.join(args.outputDir, `${safeName(label)}.png`);
          await page.screenshot({ path: file, fullPage: true });
          report.screenshots.push(file);
        }
      }
      report.failures.push(...consoleErrors.map(message => ({ code: 'console-error', message, viewport: viewport.name })));
      await page.close();
    }
  } finally {
    await browser.close();
  }
  const reportFile = path.join(args.outputDir, 'report.json');
  fs.writeFileSync(reportFile, `${JSON.stringify(report, null, 2)}\n`);
  console.log(`Rendered gallery QA: ${report.runs.length} option/view runs, ${report.failures.length} failure(s), ${report.screenshots.length} screenshot(s)`);
  console.log(reportFile);
  if (report.failures.length) {
    for (const failure of report.failures.slice(0, 40)) console.error(`FAIL [${failure.viewport || 'unknown'}/option-${failure.option || '?'}] ${failure.code}: ${failure.message}`);
    if (report.failures.length > 40) console.error(`... ${report.failures.length - 40} additional failure(s) in report.json`);
    process.exitCode = 1;
  }
}

main().catch(error => { console.error(error.stack || error.message); process.exitCode = 1; });
