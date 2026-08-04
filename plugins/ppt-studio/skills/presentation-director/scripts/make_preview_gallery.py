#!/usr/bin/env python3
"""Combine two or three HTML microdecks into one self-contained comparison gallery."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path


TEMPLATE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Comparación visual · PPT Studio</title>
<style>
:root{color-scheme:dark;font-family:ui-sans-serif,system-ui,sans-serif;background:#080b12;color:#f7f8fb}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(circle at 50% 0,#18213a 0,#080b12 52%)}
header{height:72px;display:flex;align-items:center;justify-content:space-between;padding:0 28px;border-bottom:1px solid #ffffff18}
h1{font-size:17px;margin:0;font-weight:650}.tabs{display:flex;gap:8px}.tabs button{border:1px solid #ffffff22;background:#ffffff0a;color:#cbd2e2;border-radius:999px;padding:9px 14px;cursor:pointer}.tabs button[aria-selected="true"]{background:#f7f8fb;color:#0a0d14}
main{height:calc(100vh - 72px);padding:22px;display:grid;place-items:center}.frame{width:min(100%,calc((100vh - 116px)*16/9));aspect-ratio:16/9;border:1px solid #ffffff22;background:#111827;box-shadow:0 24px 80px #0008}.frame iframe{border:0;width:100%;height:100%;display:block}
.hint{font-size:12px;color:#8e97aa} @media(max-width:700px){header{height:auto;min-height:72px;align-items:flex-start;gap:12px;flex-direction:column;padding:16px}.hint{display:none}main{height:calc(100vh - 104px);padding:12px}}
</style>
</head>
<body>
<header><div><h1>Direcciones visuales</h1><div class="hint">Usa A, B, C o las flechas para comparar.</div></div><div class="tabs" id="tabs"></div></header>
<main><div class="frame"><iframe id="preview" title="Vista previa"></iframe></div></main>
<script>
const options=__OPTIONS__;let current=0;const tabs=document.querySelector('#tabs');const frame=document.querySelector('#preview');
function show(index){current=(index+options.length)%options.length;frame.src='data:text/html;base64,'+options[current].data;[...tabs.children].forEach((b,i)=>b.setAttribute('aria-selected',String(i===current)));}
options.forEach((option,index)=>{const button=document.createElement('button');button.textContent=option.label;button.onclick=()=>show(index);button.setAttribute('aria-selected','false');tabs.append(button)});
addEventListener('keydown',event=>{if(event.key==='ArrowRight')show(current+1);if(event.key==='ArrowLeft')show(current-1);const key=event.key.toUpperCase();const index=['A','B','C'].indexOf(key);if(index>=0&&index<options.length)show(index)});show(0);
</script>
</body></html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", nargs="+", type=Path)
    parser.add_argument("--labels", nargs="*")
    parser.add_argument("--output", type=Path, default=Path("visual-options.html"))
    args = parser.parse_args()
    if not 2 <= len(args.html) <= 3:
        parser.error("Provide two or three HTML files.")
    labels = args.labels or [f"Opción {chr(65 + i)}" for i in range(len(args.html))]
    if len(labels) != len(args.html):
        parser.error("--labels must match the number of HTML files.")
    options = []
    for label, path in zip(labels, args.html):
        raw = path.read_bytes()
        options.append({"label": label, "data": base64.b64encode(raw).decode("ascii")})
    output = TEMPLATE.replace("__OPTIONS__", json.dumps(options, ensure_ascii=False))
    args.output.write_text(output, encoding="utf-8")
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
