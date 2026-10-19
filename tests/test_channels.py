"""Protect channel selection and interrupted-promotion recovery."""
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('channels', Path(__file__).parents[1] / 'scripts/channels.py')
channels = importlib.util.module_from_spec(spec)
spec.loader.exec_module(channels)


class ChannelsTest(unittest.TestCase):
    def test_annotated_tag_is_peeled_to_commit(self):
        with patch.object(channels, 'gh', side_effect=[{'object': {'type': 'tag', 'sha': 'tag'}}, {'object': {'type': 'commit', 'sha': 'commit'}}]):
            self.assertEqual(channels.commit('tags/v.4.0.1'), 'commit')

    def test_missing_alias_requires_retry(self):
        with patch.object(channels.subprocess, 'run', side_effect=[subprocess.CompletedProcess([], 0, '{}'), subprocess.CompletedProcess([], 1, '')]):
            self.assertFalse(channels.published('candidate', 'alias'))

    def test_alias_must_match_candidate(self):
        with patch.object(channels.subprocess, 'run', side_effect=[subprocess.CompletedProcess([], 0, '{"digest":"new"}'), subprocess.CompletedProcess([], 0, '{"digest":"old"}')]):
            self.assertFalse(channels.published('candidate', 'alias'))

    def test_formal_release_selection_and_development_source(self):
        import base64
        def api(path):
            if path.startswith('releases'):
                return [dict(tag_name=t, draft=False, prerelease=pre) for t, pre in [('v.4.0.0', False), ('v.4.0.2', True), ('v.4.0.1', False), ('v.3.1.7', False)]]
            if path.startswith('contents/'):
                return {'content': base64.b64encode(b'__version__ = "4.0.2"').decode()}
            return {'object': {'type': 'commit', 'sha': ('d' if 'master' in path else 'a') * 40}}
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            try:
                Path('scripts').mkdir()
                Path('.github/workflows').mkdir(parents=True)
                for p in ['Dockerfile.cpu', 'Dockerfile.gpu', '.github/workflows/publish.yml']:
                    Path(p).write_text('packaging')
                with patch.object(channels, 'gh', side_effect=api), patch.dict(os.environ, GITHUB_SHA='b' * 40, IMAGE='image', GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_OUTPUT='output'):
                    channels.main()
                matrix = json.loads(Path('output').read_text().splitlines()[0].removeprefix('matrix='))['include']
                self.assertEqual(len(matrix), 6)
                self.assertEqual({x['version'] for x in matrix if x['channel'] == 'v4'}, {'4.0.1'})
                self.assertEqual({x['source'] for x in matrix if x['channel'] == 'devel'}, {'master'})
                self.assertTrue(all('latest' not in tag for x in matrix if x['channel'] != 'v4' for tag in x['tags']))
            finally:
                os.chdir(previous)
