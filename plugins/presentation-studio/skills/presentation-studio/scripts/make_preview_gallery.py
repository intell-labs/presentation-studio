#!/usr/bin/env python3
"""Build an isolated, self-contained gallery for two or three visual microdecks."""

from __future__ import annotations

import argparse
import base64
import html.parser
import json
from pathlib import Path


PREVIEW_STYLE = """
<style id="presentation-studio-preview-isolation">
html,body{overflow:hidden!important}
.deck-chrome,.deck-controls,.deck-nav,.menu-trigger,.control-menu,.save-status,
.notes-drawer,dialog,.progress,.edit-hotzone,.edit-toggle,.edit-toast,.access-gate{
  display:none!important;visibility:hidden!important
}
.slide{visibility:hidden!important;opacity:0!important;pointer-events:none!important}
.deck-stage>.slide:nth-of-type(__SLIDE__){visibility:visible!important;opacity:1!important;pointer-events:none!important}
html body .deck-stage>.slide:nth-of-type(__SLIDE__) [data-present-step="required"]{opacity:1!important;transform:none!important;visibility:visible!important;filter:none!important}
</style>
<script id="presentation-studio-preview-history-isolation">
globalThis.__PPT_STUDIO_PREVIEW__=true;
try{history.pushState=history.replaceState=()=>{}}catch(_error){}
addEventListener('load',()=>{
  const reveal=()=>document.querySelectorAll('[data-present-step="required"]').forEach(element=>{element.classList.remove('step-hidden');element.setAttribute('aria-hidden','false')});
  const refresh=()=>{reveal();dispatchEvent(new Event('resize'))};
  requestAnimationFrame(()=>requestAnimationFrame(refresh));
  setTimeout(refresh,80);setTimeout(refresh,240);
});
</script>
"""


TEMPLATE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="dark">
<meta name="generator" content="Presentation Studio preview gallery">
<title>Direcciones visuales · Presentation Studio</title>
<style>
:root{color-scheme:dark;font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;background:#070b12;color:#f7f8fb}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(900px 520px at 50% -180px,#263355 0,#0c111d 54%,#070b12 100%)}
button{font:inherit}button:focus-visible{outline:3px solid #52e6d7;outline-offset:3px}
.shell{width:min(1680px,100%);margin:0 auto;padding:24px clamp(16px,3vw,44px) 44px}
header{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;padding-bottom:20px;border-bottom:1px solid #ffffff18}
.eyebrow{margin:0 0 7px;color:#61ddcf;font-size:11px;font-weight:750;letter-spacing:.16em;text-transform:uppercase}h1{font-size:clamp(20px,2vw,30px);line-height:1.1;letter-spacing:-.025em;margin:0;font-weight:680}.hint{margin:8px 0 0;font-size:12px;color:#8f9aac}
.tabs{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:7px}.tabs button{min-height:44px;border:1px solid #ffffff20;background:#ffffff08;color:#cbd3df;border-radius:999px;padding:9px 16px;cursor:pointer;transition:background 150ms ease,color 150ms ease,transform 150ms ease}.tabs button:hover{background:#ffffff12}.tabs button:active{transform:scale(.97)}.tabs button[aria-selected="true"]{background:#f5f7fb;color:#07101d;border-color:#f5f7fb}
.option-head{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;padding:26px 2px 16px}.option-title{margin:0;font-size:18px;font-weight:650}.option-description{max-width:760px;margin:0;color:#9aa6b6;font-size:13px;line-height:1.5;text-align:right}
.preview-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(12px,1.5vw,22px)}.preview-grid[data-count="2"]{grid-template-columns:repeat(2,minmax(0,1fr));max-width:1200px}.preview-card{min-width:0}.preview-meta{display:flex;align-items:center;gap:9px;margin:0 0 8px;color:#aab4c2;font-size:11px;font-weight:650;letter-spacing:.08em;text-transform:uppercase}.preview-number{display:grid;place-items:center;min-width:38px;height:25px;padding:0 8px;border-radius:7px;background:#ffffff0d;color:#62e0d2;font-variant-numeric:tabular-nums}.preview-name{letter-spacing:.1em}
.frame{position:relative;width:100%;aspect-ratio:16/9;overflow:hidden;border:1px solid #ffffff20;border-radius:13px;background:#101725;box-shadow:0 24px 64px #0007}.frame::after{content:"";position:absolute;inset:0;pointer-events:none;box-shadow:inset 0 0 0 1px #ffffff08;border-radius:inherit}.frame iframe{border:0;width:100%;height:100%;display:block;pointer-events:none;background:#080d16}
.frame iframe{opacity:1;transition:opacity 140ms ease}.is-loading .frame::before{content:"Cargando vista…";position:absolute;z-index:1;inset:0;display:grid;place-items:center;color:#aab4c2;font-size:12px}.is-loading .frame iframe{opacity:0}.load-error .frame::before{content:"No se pudo cargar esta opción";color:#ffadb3}.option-panel[hidden]{display:none}
@media(max-width:1100px) and (min-width:901px){.preview-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.preview-grid .preview-card:last-child:nth-child(odd){grid-column:1/-1;max-width:calc(50% - 7px)}}
@media(max-width:900px){.shell{padding:18px clamp(14px,4vw,28px) 36px}header{align-items:flex-start;flex-direction:column}.tabs{justify-content:flex-start;width:100%}.tabs button{flex:1 1 210px}.option-head{align-items:flex-start;flex-direction:column;gap:8px;padding-top:22px}.option-description{text-align:left}.preview-grid,.preview-grid[data-count="2"]{grid-template-columns:minmax(0,1fr);max-width:none}.preview-card{width:100%;max-width:none}.hint{display:none}}
@media(max-width:520px){.tabs{display:grid;grid-template-columns:1fr}.tabs button{width:100%;text-align:center}.option-title{font-size:17px}.option-description{font-size:12px}.preview-meta{font-size:10px}.frame{border-radius:10px}}
@media(prefers-reduced-motion:reduce){.tabs button{transition-duration:1ms}}
@media(prefers-contrast:more){header{border-color:#ffffff70}.tabs button,.frame{border-color:#ffffff80}.hint,.option-description,.preview-meta{color:#fff}}
</style>
</head>
<body>
<div class="shell">
  <header><div><p class="eyebrow">Presentation Studio · exploración visual</p><h1>Direcciones visuales</h1><p class="hint">Compara la tesis completa de cada opción. Usa A, B, C o las flechas.</p></div><div class="tabs" id="tabs" role="tablist" aria-label="Direcciones visuales"></div></header>
  <main id="option-panels" aria-live="polite"></main>
</div>
<script>
const options=__OPTIONS__;let current=0;
const tabs=document.querySelector('#tabs'),panels=document.querySelector('#option-panels');
function decode(data){const bytes=Uint8Array.from(atob(data),character=>character.charCodeAt(0));return new TextDecoder().decode(bytes)}
function buildPanel(option,optionIndex){
  const panel=document.createElement('section');panel.className='option-panel';panel.id=`option-panel-${optionIndex}`;panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby',`option-tab-${optionIndex}`);panel.hidden=optionIndex!==0;
  panel.innerHTML=`<div class="option-head"><h2 class="option-title"></h2><p class="option-description"></p></div><div class="preview-grid"></div>`;panel.querySelector('.option-title').textContent=option.label;panel.querySelector('.option-description').textContent=option.description;
  const grid=panel.querySelector('.preview-grid');grid.dataset.count=String(option.slides.length);
  option.slides.forEach((slide,slideIndex)=>{const card=document.createElement('article');card.className='preview-card is-loading';const optionName=`Opción ${option.code}-${slideIndex+1}`;card.innerHTML=`<div class="preview-meta"><span class="preview-number">${option.code}-${slideIndex+1}</span><span class="preview-name">${optionName}</span></div><div class="frame"><iframe title="${optionName}: ${option.label}" sandbox="allow-scripts" loading="eager" tabindex="-1" data-ppt-preview="true"></iframe></div>`;const iframe=card.querySelector('iframe');iframe.dataset.source=slide.data;grid.append(card)});
  return panel;
}
function loadPanel(panel){if(panel.dataset.started==='true')return;panel.dataset.started='true';const frames=[...panel.querySelectorAll('iframe[data-source]')];requestAnimationFrame(()=>requestAnimationFrame(()=>frames.forEach((iframe,index)=>{const card=iframe.closest('.preview-card');iframe.addEventListener('load',()=>{card.classList.remove('is-loading','load-error');iframe.dataset.loaded='true'},{once:true});iframe.srcdoc=decode(iframe.dataset.source);iframe.removeAttribute('data-source');setTimeout(()=>{if(iframe.dataset.loaded!=='true')card.classList.add('load-error')},8000+index*500)})))}
function show(index,focus=false){
  current=(index+options.length)%options.length;[...panels.children].forEach((panel,panelIndex)=>{panel.hidden=panelIndex!==current});loadPanel(panels.children[current]);
  [...tabs.children].forEach((button,buttonIndex)=>{const selected=buttonIndex===current;button.setAttribute('aria-selected',String(selected));button.tabIndex=selected?0:-1});if(focus)tabs.children[current].focus();
}
options.forEach((option,index)=>{const button=document.createElement('button');button.type='button';button.id=`option-tab-${index}`;button.setAttribute('role','tab');button.textContent=option.label;button.setAttribute('aria-controls',`option-panel-${index}`);button.setAttribute('aria-selected','false');button.addEventListener('click',()=>show(index));tabs.append(button);panels.append(buildPanel(option,index))});
addEventListener('keydown',event=>{if(event.target.matches('input,textarea,[contenteditable="true"]'))return;if(event.key==='ArrowRight'){event.preventDefault();show(current+1,true)}else if(event.key==='ArrowLeft'){event.preventDefault();show(current-1,true)}else{const index=['A','B','C'].indexOf(event.key.toUpperCase());if(index>=0&&index<options.length){event.preventDefault();show(index,true)}}});show(0);
</script>
</body>
</html>
"""


class SlideCounter(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.count = 0

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = next((value for name, value in attrs if name.lower() == "class"), "") or ""
        if "slide" in classes.split():
            self.count += 1


def count_slides(source: str) -> int:
    parser = SlideCounter()
    parser.feed(source)
    return parser.count


def isolated_slide(source: str, slide_number: int) -> str:
    style = PREVIEW_STYLE.replace("__SLIDE__", str(slide_number))
    marker = "</head>"
    if marker not in source.lower():
        raise ValueError("Microdeck does not contain </head>.")
    index = source.lower().index(marker)
    return source[:index] + style + source[index:]


def encode(source: str) -> str:
    return base64.b64encode(source.encode("utf-8")).decode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", nargs="+", type=Path)
    parser.add_argument("--labels", nargs="*")
    parser.add_argument("--descriptions", nargs="*")
    parser.add_argument("--output", type=Path, default=Path("visual-options.html"))
    args = parser.parse_args()
    if not 2 <= len(args.html) <= 3:
        parser.error("Provide two or three HTML files.")
    labels = args.labels or [f"Opción {chr(65 + index)}" for index in range(len(args.html))]
    descriptions = args.descriptions or ["" for _path in args.html]
    if len(labels) != len(args.html):
        parser.error("--labels must match the number of HTML files.")
    if len(descriptions) != len(args.html):
        parser.error("--descriptions must match the number of HTML files.")

    options = []
    try:
        for option_index, (label, description, path) in enumerate(zip(labels, descriptions, args.html)):
            source = path.read_text(encoding="utf-8")
            if "base-deck-v2" not in source:
                raise ValueError(f"{path} does not use the required base-deck-v2 runtime.")
            slide_count = count_slides(source)
            if not 2 <= slide_count <= 3:
                raise ValueError(f"{path} has {slide_count} slides; microdecks require two or three.")
            slides = [
                {"data": encode(isolated_slide(source, slide_number))}
                for slide_number in range(1, slide_count + 1)
            ]
            options.append({"code": chr(65 + option_index), "label": label, "description": description, "slides": slides})
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))

    output = TEMPLATE.replace("__OPTIONS__", json.dumps(options, ensure_ascii=False))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
