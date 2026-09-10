"""Anonymous regression fixture derived from failure shapes, not client artifacts."""
import copy
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "plugins/presentation-studio/skills/presentation-studio"
sys.path.insert(0, str(SKILL / "scripts"))
from design_contract import inventory, artifact_errors, design_errors, digest, contract_digest
from validate_evidence import evidence_errors
from init_project import build_contract


def make_fixture(directory):
    """15 -> 6 organizations: five retained original SVG logos, one supplied new."""
    directory.mkdir(parents=True, exist_ok=True)
    def logo(i):
        return f'<svg data-asset-id="logo-{i}" viewBox="0 0 80 80" width="80" height="80" role="img" aria-label="Organization {i}"><circle cx="40" cy="40" r="{12+i}" fill="#314cff"/></svg>'
    baseline = directory / "baseline.html"
    baseline.write_text('<section class="slide" id="hoja-02">' + ''.join(logo(i) for i in range(15)) + '</section>')
    baseline_inventory = inventory(baseline)
    project = build_contract()
    project['workflow']['mode'] = 'enhance'
    project['design_contract']['visual_system'] = {key:{'decision':'not-applicable','reason':'Anonymous regression fixture','source':''} for key in project['design_contract']['visual_system']}
    project['appearance']['available_themes'] = ['light', 'dark']
    project['design_contract'].update({
        'baseline_sha256': baseline_inventory['html_sha256'],
        'baseline_asset_hashes': sorted({a['sha256'] for a in baseline_inventory['assets']}),
        'readability': {'mode': 'speaker-led', 'max_words_per_slide': 65, 'supporting_text_min_px': 24, 'exceptions': []},
        'composition': {'reference': 'Approved anonymous shortlist', 'checks': [
            {'slide': 'hoja-02', 'boxes': [f'logo-{i}' for i in range(6)], 'property': 'width', 'value_px': 220, 'tolerance_px': 2}]},
    })
    for a in baseline_inventory['assets']:
        keep = int(a['id'].split('-')[1]) < 5
        project['design_contract']['assets'].append({**a, 'kind':'logo', 'decision':'keep' if keep else 'remove',
            'baseline_sha256':a['sha256'], 'reason':'Retained identity' if keep else 'Excluded from approved shortlist',
            'slides':['hoja-02'] if keep else []})
    # New supplied sixth logo has a distinct original fingerprint, not a recreated client logo.
    new_logo = logo(20).replace('logo-20', 'logo-5-new')
    supplied = directory / 'supplied.html'
    supplied.write_text('<section class="slide" id="hoja-02">'+new_logo+'</section>')
    a = inventory(supplied)['assets'][0]
    project['design_contract']['assets'].append({**a, 'kind':'logo', 'decision':'add', 'reason':'Missing sixth identity supplied', 'slides':['hoja-02']})
    sections = []
    def slide(number, role, title, body):
        identifier=f'hoja-{number:02d}'
        tone='anchor' if role in ('cover','closing') else 'content'
        project['slides'].append({'id':identifier,'role':role,'tone':tone,'purpose':title,'takeaway':title,
            'title':title,'content':[],'evidence':[],'visual_form':'semantic groups','speaker_notes':'','states':[],'open_questions':[]})
        sections.append(f'<section class="slide" id="{identifier}" data-slide-role="{role}" data-tone="{tone}"><h2 data-edit-id="{identifier}-title">{title}</h2>{body}</section>')
    slide(1,'cover','A clear decision.','<p data-edit-id="intro">Approved text stays unchanged.</p>')
    cells=''.join(f'<div class="logo-box" data-qa-box="logo-{i}" data-qa-role="content">{logo(i) if i<5 else new_logo}</div>' for i in range(6))
    slide(2,'content','Selected experience.',f'<div class="logos">{cells}</div>')
    services=''.join(f'<article data-qa-box="service-{i}" data-qa-role="content"><h3 data-edit-id="service-title-{i}">Service {i+1}</h3><p data-edit-id="service-copy-{i}">Local description, directly below its title.</p></article>' for i in range(5))
    slide(3,'content','Five services.',f'<div class="services">{services}</div>')
    slide(4,'closing','Next step.','<p data-edit-id="closing">Unrelated approved closing remains intact.</p>')
    source=(SKILL/'assets/runtime/base-deck.html').read_text()
    source=re.sub(r'(<div class="deck-stage" id="deck-stage">)[\s\S]*?(\n  </div>\n</main>)',lambda m:m[1]+''.join(sections)+m[2],source,count=1)
    source=source.replace('</style>', '.logos{display:flex;gap:24px;margin-top:56px}.logo-box{width:220px;height:220px;display:grid;place-items:center;border:1px solid var(--local-line);border-radius:24px}.services{display:grid;grid-template-columns:1fr 1fr;gap:36px;margin-top:48px}.services p{font-size:28px}.services h3{font-size:40px;margin:0 0 12px}.slide>p{font-size:30px}\n</style>',1)
    source=re.sub(r'(<script type="application/json" id="presentation-project-data">)[\s\S]*?(</script>)',lambda m:m[1]+json.dumps(project,ensure_ascii=False)+m[2],source,count=1)
    html=directory/'presentation.html'
    html.write_text(source)
    (directory/'presentation-project.json').write_text(json.dumps(project,ensure_ascii=False))
    return html,project


class DesignTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.html,self.project=make_fixture(Path(self.temp.name))

    def test_shortlist_preserves_five_originals_and_adds_sixth(self):
        self.assertEqual(artifact_errors(self.html,self.project), [])
        self.assertEqual(len(inventory(self.html)['assets']),6)
        self.assertEqual(sum(a['decision']=='keep' for a in self.project['design_contract']['assets']),5)

    def test_missing_logo_fails_without_geometry_issue(self):
        source=self.html.read_text()
        self.html.write_text(re.sub(r'<svg data-asset-id="logo-0"[\s\S]*?</svg>','',source))
        self.assertTrue(any('assets.missing: logo-0' in e for e in artifact_errors(self.html,self.project)))

    def test_same_id_but_substituted_logo_fails(self):
        self.html.write_text(self.html.read_text().replace('r="12"','r="11"'))
        self.assertTrue(any('assets.changed: logo-0' in e for e in artifact_errors(self.html,self.project)))

    def test_missing_anchor_cannot_masquerade_as_content(self):
        self.html.write_text(self.html.read_text().replace('data-tone="anchor"',''))
        errors=artifact_errors(self.html,self.project)
        self.assertTrue(any('design.anchor: hoja-01' in e for e in errors))
        self.assertTrue(any('design.anchor: hoja-04' in e for e in errors))

    def test_removing_inventory_decisions_fails(self):
        self.project['design_contract']['assets'].pop(0)
        self.assertTrue(any('assets.unaccounted' in e for e in design_errors(self.project)))

    def test_default_and_duplicate_themes_fail(self):
        self.project['appearance']['default_theme']='custom'
        self.assertTrue(any('default_theme' in e for e in design_errors(self.project)))
        self.project['appearance']['available_themes']=['light','light']
        self.assertTrue(any('unique list' in e for e in design_errors(self.project)))

    def test_old_qa_or_changed_capture_cannot_certify_new_html(self):
        folder=self.html.parent
        capture=folder/'capture.png';capture.write_bytes(b'test evidence, not a visual approval')
        report={'html_sha256':digest(self.html.read_bytes()),'contract_sha256':contract_digest(self.project),
                'layers':{},'screenshots':[{'path':str(capture),'sha256':digest(capture.read_bytes())}]}
        report_path=folder/'report.json';report_path.write_text(json.dumps(report))
        review={'html_sha256':report['html_sha256'],'report_sha256':digest(report_path.read_bytes())}
        review_path=folder/'visual-review.json';review_path.write_text(json.dumps(review))
        errors=evidence_errors(self.html,self.project,report_path,review_path)
        self.assertFalse(any('stale-html' in e for e in errors))
        self.assertTrue(any('visual-review' in e for e in errors))
        self.html.write_text(self.html.read_text()+'\n')
        capture.write_bytes(b'changed')
        errors=evidence_errors(self.html,self.project,report_path,review_path)
        self.assertTrue(any('stale-html' in e for e in errors))
        self.assertTrue(any('evidence.screenshot' in e for e in errors))

    def test_fixture_rebuild_is_identical(self):
        # Ignore discovery timestamps, not actual design differences.
        a=self.html.read_text()
        html,_=make_fixture(self.html.parent)
        normalize=lambda s:re.sub(r'"updated_at": "[^"]+"','"updated_at": "time"',s)
        self.assertEqual(normalize(a),normalize(html.read_text()))

    def test_complete_evidence_gate_and_stale_decisions(self):
        # Synthetic unit-test evidence, never used to approve a real presentation.
        folder=self.html.parent
        capture=folder/'synthetic.png';capture.write_bytes(b'unit-test-only')
        runs=[]
        for slide in self.project['slides']:
            for view in ('desktop','laptop','phone_portrait','phone_landscape'):
                runs.append({'label':view+slide['id'],'slide':slide['id'],'viewport':{'name':view},'state':0,'mode':'audience'})
            for theme in ('light','dark'):
                runs.append({'label':'desktop-theme-'+theme+slide['id'],'slide':slide['id'],'theme':theme})
        report={'html_sha256':digest(self.html.read_bytes()),'contract_sha256':contract_digest(self.project),
                'runs':runs,'failures':[],'review':[],
                'layers':{k:{'status':'passed'} for k in ('structure_runtime','geometry','resources','decision_fidelity','editorial_numeric')},
                'screenshots':[{'path':str(capture),'sha256':digest(capture.read_bytes()),'label':r['label']} for r in runs]}
        report_path=folder/'synthetic-report.json';report_path.write_text(json.dumps(report))
        review={'html_sha256':report['html_sha256'],'report_sha256':digest(report_path.read_bytes()),
                'status':'completed','reviewer':'unit-test-only','slides':[{'id':s['id'],'status':'approved',
                **{k:'Synthetic observation' for k in ('hierarchy','spacing','brand_and_assets','readability','contrast','editorial_numeric')}} for s in self.project['slides']]}
        review_path=folder/'synthetic-review.json';review_path.write_text(json.dumps(review))
        self.assertEqual(evidence_errors(self.html,self.project,report_path,review_path),[])
        review['slides'][0].pop('contrast');review_path.write_text(json.dumps(review))
        self.assertTrue(any('evidence.visual-review' in e for e in evidence_errors(self.html,self.project,report_path,review_path)))
        review['slides'][0]['contrast']='Synthetic per-surface check.';review_path.write_text(json.dumps(review))
        report['summary']={'unmeasured':[{'criterion':'contrast'}]}
        report_path.write_text(json.dumps(report))
        review['report_sha256']=digest(report_path.read_bytes());review_path.write_text(json.dumps(review))
        self.assertTrue(any('evidence.limitations' in e for e in evidence_errors(self.html,self.project,report_path,review_path)))
        review['limitations']='Synthetic complex paint reviewed separately.';review_path.write_text(json.dumps(review))
        self.assertEqual(evidence_errors(self.html,self.project,report_path,review_path),[])
        self.project['appearance']['available_themes'].append('custom')
        errors=evidence_errors(self.html,self.project,report_path,review_path)
        self.assertTrue(any('stale-contract' in e for e in errors))
        self.assertTrue(any('evidence.theme' in e for e in errors))


if __name__=='__main__':
    if len(sys.argv)==2:
        print(make_fixture(Path(sys.argv[1]))[0])
    else:
        unittest.main()
