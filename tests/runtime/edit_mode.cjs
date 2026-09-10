#!/usr/bin/env node
// Run with Node and Playwright available through NODE_PATH; no visible browser opens.
const assert = require('node:assert/strict');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');
const { settle } = require('../../plugins/presentation-studio/skills/presentation-studio/scripts/design_qa.cjs');

const runtime = path.resolve(__dirname, '../../plugins/presentation-studio/skills/presentation-studio/assets/runtime/base-deck.html');
const viewports = [
  { width: 1440, height: 900 },
  { width: 1280, height: 720 },
  { width: 390, height: 844 },
  { width: 844, height: 390 },
];

async function assertEditing(page, expected) {
  const state = await page.evaluate(() => ({
    editing: document.body.classList.contains('edit-mode'),
    editable: !!document.querySelector('[contenteditable="true"]'),
    selected: !!document.querySelector('.typography-target,.element-style-target'),
    picking: !!document.body.dataset.typographyPick,
    toolbar: !document.querySelector('#element-toolbar').hidden,
    dialog: document.querySelector('#typography-dialog').open,
    label: document.querySelector('#toggle-edit strong').textContent,
    editorFocus: !!document.activeElement.closest('[data-edit-id],#element-toolbar,#typography-dialog'),
  }));
  assert.equal(state.editing, expected);
  assert.equal(state.editable, expected);
  assert.equal(state.label, expected ? 'Salir de edición' : 'Editar texto');
  if (!expected) {
    for (const key of ['selected', 'picking', 'toolbar', 'dialog', 'editorFocus']) {
      assert.equal(state[key], false, `${key} remains active after exiting edit mode`);
    }
  }
}

async function main() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  });
  try {
    for (const viewport of viewports) {
      const touch = viewport.width < 900;
      const page = await browser.newPage({ viewport, hasTouch: touch, reducedMotion: 'reduce' });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(pathToFileURL(runtime).href);
      const title = page.locator('[data-edit-id="s01-title"]');
      const selectTitle = () => touch ? title.tap() : title.click();
      const outsideClick = async (letterbox = false) => {
        // Toolbar position is committed on requestAnimationFrame after selection.
        if(await page.locator('#element-toolbar').isVisible())await settle(page, '#element-toolbar');
        const point = await page.evaluate(letterbox => {
          const rect = document.querySelector('.slide.is-active .slide-grid').getBoundingClientRect();
          const points = letterbox ? [{ x: 2, y: 2 }] : [];
          if (!letterbox) {
            for (let row = 1; row < 12; row++) {
              for (let col = 1; col < 12; col++) {
                points.push({ x: rect.left + rect.width * col / 12, y: rect.top + rect.height * row / 12 });
              }
            }
          }
          for (const point of points) {
            const hit = document.elementFromPoint(point.x, point.y);
            if (hit && !hit.closest('[data-edit-id],[data-style-id],#element-toolbar,.deck-chrome,.studio-dialog')) return point;
          }
          throw new Error('No exposed outside-click test point found');
        }, letterbox);
        if (touch) await page.touchscreen.tap(point.x, point.y);
        else await page.mouse.click(point.x, point.y);
      };

      await page.keyboard.press('e');
      await assertEditing(page, true);
      await page.keyboard.press('Escape');
      await assertEditing(page, false);

      await page.keyboard.press('e');
      await selectTitle();
      await title.fill('Texto editado que debe conservarse.');
      await page.keyboard.press('Escape');
      await assertEditing(page, false);
      assert.equal(await title.textContent(), 'Texto editado que debe conservarse.');
      assert.match(await page.title(), /^●/);
      assert.equal(await page.locator('#save-status').getAttribute('data-state'), 'dirty');

      // Both stage whitespace and the area surrounding the stage exit editing.
      for (const letterbox of [false, true]) {
        await page.keyboard.press('e');
        await selectTitle();
        await outsideClick(letterbox);
        await assertEditing(page, false);
      }
      await page.keyboard.press('e');
      await outsideClick();
      await assertEditing(page, false);

      // Selecting another editable component and applying toolbar styles keeps editing active.
      await page.keyboard.press('e');
      await selectTitle();
      await page.locator('[data-edit-id="s01-kicker"]').click();
      await assertEditing(page, true);
      await selectTitle();
      await page.locator('#context-type-size').fill('96');
      await page.locator('#context-type-size').press('Tab');
      await assertEditing(page, true);
      assert.equal(await title.evaluate(node => node.style.fontSize), '96px');
      await page.locator('#context-type-size').focus();
      await page.keyboard.press('Escape');
      await assertEditing(page, false);
      assert.equal(await title.evaluate(node => node.style.fontSize), '96px');

      // Escape from the full typography dialog must not reopen the toolbar on close.
      await page.keyboard.press('e');
      await selectTitle();
      await page.locator('#context-more-type').click();
      assert.equal(await page.locator('#typography-dialog').evaluate(node => node.open), true);
      await page.locator('#type-size-number').click();
      await assertEditing(page, true);
      await page.keyboard.press('Escape');
      await assertEditing(page, false);

      // Exit also cancels typography selection before a target has been picked.
      await page.keyboard.press('Alt+y');
      await assertEditing(page, true);
      await page.keyboard.press('Escape');
      await assertEditing(page, false);

      // Visual components use the same exit path as text.
      await page.keyboard.press('e');
      const surfacePoint = await page.locator('[data-qa-box="hero"]').evaluate(surface => {
        const rect = surface.getBoundingClientRect();
        for (let row = 1; row < 10; row++) {
          for (let col = 1; col < 10; col++) {
            const point = { x: rect.left + rect.width * col / 10, y: rect.top + rect.height * row / 10 };
            const hit = document.elementFromPoint(point.x, point.y);
            if (hit?.closest('[data-style-id]') === surface && !hit.closest('[data-edit-id]')) return point;
          }
        }
        throw new Error('No exposed visual surface found');
      });
      await page.mouse.click(surfacePoint.x, surfacePoint.y);
      assert.equal(await page.locator('#element-toolbar').getAttribute('data-mode'), 'visual');
      await page.keyboard.press('Escape');
      await assertEditing(page, false);

      if (!touch) {
        await page.locator('#menu-trigger').click();
        await page.locator('#toggle-edit').click();
        await assertEditing(page, true);
        await page.locator('#menu-trigger').click();
        await assertEditing(page, true);
        await page.keyboard.press('Escape');
        await assertEditing(page, false);
      }
      await page.keyboard.press('ArrowRight');
      assert.match(page.url(), /#hoja-01\/estado-01$/);
      assert.deepEqual(errors, []);
      console.log(`PASS edit mode exit and preservation: ${viewport.width}x${viewport.height}`);
      await page.close();
    }
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
