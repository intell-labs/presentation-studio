import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCRIPTS=ROOT/'plugins/presentation-studio/skills/presentation-studio/scripts'
sys.path.insert(0,str(SCRIPTS))
from preserve_edits import reconcile, js_fnv1a


class ReconciliationTests(unittest.TestCase):
    def test_missing_dialog_target_blocks_strict_validation(self):
        runtime=SCRIPTS.parent/'assets/runtime/base-deck.html'
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'broken.html'
            file.write_text(runtime.read_text().replace('</body>','<button data-dialog-open="missing">Detail</button></body>'))
            result=subprocess.run([sys.executable,str(SCRIPTS/'validate_html.py'),str(file),'--strict'],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Dialog trigger has no matching dialog',result.stdout)

    def test_text_merge_preserves_later_design(self):
        base='<style>.card{color:red}</style><p data-edit-id="a">Original</p>'
        user=base.replace('Original','Curated')
        candidate=base.replace('color:red','color:blue').replace('<p ','<p style="font-size:28px" ')
        merged,report=reconcile(user,candidate,base,scope='text')
        self.assertIn('color:blue',merged)
        self.assertIn('font-size:28px',merged)
        self.assertIn('>Curated</p>',merged)
        self.assertEqual(report['conflicts'],[])

    def test_both_changed_and_unknown_base_block(self):
        base='<p data-edit-id="a">Original</p>'
        user=base.replace('Original','User')
        agent=base.replace('Original','Agent')
        merged,report=reconcile(user,agent,base)
        self.assertIsNone(merged)
        self.assertEqual(report['conflicts'][0]['reason'],'both-changed')
        merged,report=reconcile(user,agent)
        self.assertIsNone(merged)
        self.assertEqual(report['conflicts'][0]['reason'],'no-common-base')

    def test_browser_baselines_detect_competing_edits(self):
        user=f'<p data-edit-id="a" data-edit-baseline="{js_fnv1a("Original")}">User</p>'
        self.assertIsNone(reconcile(user,'<p data-edit-id="a">Agent</p>')[0])
        self.assertIn('>User</p>',reconcile(user,'<p data-edit-id="a">Original</p>')[0])

    def test_delete_versus_edit_and_styles_conflict(self):
        base='<p data-edit-id="a" style="color:red">Original</p>'
        user=base.replace('Original','User')
        self.assertIsNone(reconcile(user,'',base)[0])
        merged,report=reconcile(base.replace('red','blue'),base.replace('red','green'),base)
        self.assertIsNone(merged)
        self.assertIn('text-style:a',[c['id'] for c in report['conflicts']])

    def test_variant_original_intact_and_update_has_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);base=folder/'base.html';user=folder/'v1.html';candidate=folder/'candidate.html';out=folder/'v2.html'
            base.write_text('<p data-edit-id="a">Original</p>');user.write_text(base.read_text().replace('Original','User'));candidate.write_text(base.read_text())
            before=user.read_bytes()
            command=[sys.executable,str(SCRIPTS/'preserve_edits.py'),str(user),str(candidate),'--base',str(base),'--output',str(out),'--mode','variant']
            run=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(user.read_bytes(),before)
            self.assertIn('>User</p>',out.read_text())
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
            command[-1]='update';subprocess.run(command,check=True,capture_output=True)
            self.assertEqual(len(list(folder.glob('v2.backup-*.html'))),1)
            report=json.loads(out.with_suffix('.reconciliation.json').read_text())
            self.assertEqual(report['output_sha256'],hashlib.sha256(out.read_bytes()).hexdigest())
