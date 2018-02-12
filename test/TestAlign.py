import os
import unittest
import tempfile
import evcouplings.align as align

from evcouplings.align.protocol import run

class TestAlign(unittest.TestCase):
    # def test_submitter_factory_available(self):
    #     print()

    # def test_run_no_args(self):
    #     return self.assertRaises(TypeError, align.run)

    def test_run_missing_args(self):
        run(**{"protocol":"standard"})


if __name__ == '__main__':
    unittest.main()