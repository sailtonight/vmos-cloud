import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location('vmos', Path(__file__).parents[1] / 'scripts/vmos.py')
vmos = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vmos)


def element(text, i=0):
    return dict(text=text, desc='', id='', click=True, i=i, x=i * 100, y=100)


class CliTests(unittest.TestCase):
    def run_cli(self, phone, *args):
        with patch.object(vmos, 'Phone', return_value=phone), \
             patch.object(vmos, 'resolve_pad', return_value='test-pad'), \
             patch.object(vmos.sys, 'argv', ['vmos', *args]), \
             contextlib.redirect_stdout(io.StringIO()):
            vmos.main()

    def test_exact_button_beats_earlier_explanatory_text(self):
        phone = Mock()
        phone.ui.return_value = [element('点击同意并继续即表示同意条款'), element('同意并继续', 1)]
        self.run_cli(phone, 'tap', '--text', '同意并继续')
        phone.tap.assert_called_once_with(100, 100)

    def test_substring_fallback_remains_available(self):
        phone = Mock()
        phone.ui.return_value = [element('Search videos', 2)]
        self.run_cli(phone, 'tap', '--text', 'Search')
        phone.tap.assert_called_once_with(200, 100)

    def test_exact_option_does_not_fall_back(self):
        phone = Mock()
        phone.ui.return_value = [element('Search videos')]
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            self.run_cli(phone, 'tap', '--text', 'Search', '--exact')
        self.assertEqual(error.exception.code, 1)
        phone.tap.assert_not_called()

    @patch.object(vmos.time, 'sleep')
    def test_verify_polls_stale_tree_without_resending(self, sleep):
        phone = Mock()
        phone.ui.side_effect = [[], [element('lipstick 美妆 123')]]
        self.run_cli(phone, 'text', 'lipstick 美妆 123', '--verify')
        phone.api.assert_called_once_with('inputText', {'text': 'lipstick 美妆 123'})
        self.assertEqual(phone.ui.call_count, 2)

    @patch.object(vmos.time, 'sleep')
    def test_verify_failure_does_not_resend(self, sleep):
        phone = Mock()
        phone.ui.return_value = [element('prefix lipstick')]
        with patch.object(vmos.time, 'monotonic', side_effect=[0, 0, 21]), \
             contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            self.run_cli(phone, 'text', 'lipstick', '--verify')
        self.assertEqual(error.exception.code, 1)
        phone.api.assert_called_once_with('inputText', {'text': 'lipstick'})

    @patch.object(vmos.time, 'sleep')
    def test_wait_app_requires_exact_package(self, sleep):
        phone = Mock()
        target = {'packageName': 'com.ss.android.ugc.trill', 'versionName': '36.0.1'}
        phone.api.side_effect = [
            {'data': [{'apps': [{'packageName': 'com.ss.android.ugc.trill.lite'}]}]},
            {'data': [{'apps': [target]}]},
        ]
        self.assertEqual(vmos.wait_app(phone, target['packageName'], 120), target)
        self.assertEqual(phone.api.call_count, 2)

    @patch.object(vmos.time, 'sleep')
    def test_wait_app_timeout_is_unconfirmed(self, sleep):
        phone = Mock()
        phone.api.return_value = {'data': [{'apps': []}]}
        with patch.object(vmos.time, 'monotonic', side_effect=[0, 0, 121]), \
             self.assertRaisesRegex(vmos.VmosError, 'may still be running'):
            vmos.wait_app(phone, 'missing.package', 120)


if __name__ == '__main__':
    unittest.main()
