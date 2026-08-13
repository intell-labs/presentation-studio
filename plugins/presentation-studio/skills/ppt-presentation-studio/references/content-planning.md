# Content planning and representation

## Existing structure

Ask whether a structure already exists. If yes, extract it before proposing alternatives. Preserve valid user intent, then identify gaps, redundancy, sequencing problems, and unsupported claims.

If no structure exists, propose one based on the desired decision. Explain what evidence each section needs and co-create it progressively.

## Slide contract

For each slide record:

```json
{
  "id": "hoja-01",
  "section": "",
  "purpose": "",
  "takeaway": "",
  "title": "",
  "content": [],
  "evidence": [],
  "visual_form": "",
  "speaker_notes": "",
  "states": [],
  "open_questions": []
}
```

## Representation matrix

| Information shape | Preferred form |
| --- | --- |
| One decisive metric | Data hero |
| Change over time | Line, slope, or timeline |
| Two alternatives | Direct comparison |
| Distribution of a total | Segmented bar or composition |
| Process | Sequence or flow |
| Risks | Matrix or ranked ledger |
| Ecosystem or ownership | Relationship map |
| Several related metrics | Editorial table or dashboard |
| Story, testimony, or identity | Image, quote, and context |
| Dense supporting detail | On-demand state, notes, or appendix |

Do not use progress bars for unrelated absolute values. Do not use cards merely because they are easy to generate. Use hierarchy, space, typography, and composition before adding containers.

## Density

Classify the deck:

- speaker-led: one idea per slide, fewer words, more section beats;
- reading-first: self-contained explanation, structured annotations, more evidence;
- mixed: choose a primary mode and use notes or appendices for the secondary need.

Split overloaded slides instead of shrinking text below comfortable reading size.

## Content approval

Before visual work, show:

- narrative arc;
- ordered slide list;
- title and takeaway per slide;
- evidence and source status;
- missing information;
- assumptions;
- recommended visual form.

Wait for explicit approval. Store the approved human-readable version in `content-approved.md` and set `approvals.structure` and `approvals.content` separately.
