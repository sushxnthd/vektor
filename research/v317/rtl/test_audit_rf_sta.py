"""Synthetic STA-log parser regression."""
import tempfile
import unittest
from pathlib import Path
from research.v317.rtl.audit_rf_sta import parse_report

class TestStaAudit(unittest.TestCase):
    def write(self, text):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        p = Path(t.name) / 'test.log'
        p.write_text(text)
        return p

    def test_valid(self):
        p = self.write('STA_PATH_BEGIN\nStartpoint: a\nEndpoint: b\n  0.314 data arrival time\n -0.314 data arrival time\nSTA_PATH_END\n')
        self.assertEqual(parse_report(p)['arrival_ns'], .314)

    def test_missing_path(self):
        p = self.write('STA_PATH_BEGIN\nNo paths found.\nSTA_PATH_END\n')
        with self.assertRaises(AssertionError): parse_report(p)

    def test_error(self):
        p = self.write('Error: invalid liberty\nSTA_PATH_BEGIN\nStartpoint: a\nEndpoint: b\n  0.3 data arrival time\nSTA_PATH_END\n')
        with self.assertRaises(AssertionError): parse_report(p)

    def test_unbounded(self):
        p = self.write('Startpoint: a\nEndpoint: b\n  0.3 data arrival time\n')
        with self.assertRaises(AssertionError): parse_report(p)

    def test_zero_delay(self):
        p = self.write('STA_PATH_BEGIN\nStartpoint: a\nEndpoint: b\n  0.0 data arrival time\nSTA_PATH_END\n')
        with self.assertRaises(AssertionError): parse_report(p)

if __name__ == '__main__':
    unittest.main()
