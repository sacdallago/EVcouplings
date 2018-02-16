import unittest
import tempfile
from evcouplings.align import *
from test import MONOMER_TEST_LOCATION

class TestAlign(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestAlign, self).__init__(*args, **kwargs)

    def test_run_missing_parameters(self):
        self.assertRaises(MissingParameterError, run)
        self.assertRaises(MissingParameterError, run, )
        self.assertRaises(MissingParameterError, run, prefix="random_name")
        self.assertRaises(MissingParameterError, run, protocol=list(PROTOCOLS.keys())[1])
        return

    def test_run_wrong_parameters(self):
        return self.assertRaises(InvalidParameterError, run, protocol="NONESENSE")

    def test_write_fasta(self):
        fasta_sequences = (
            ("seq1",
             "ADQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKDTDSEEEI"
             "REAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTAK*"
             ),
            ("seq2",
             "LCLYTHIGRNIYYGSYLYSETWNTGIMLLLITMATAFMGYVLPWGQMSFWGATVITNLFSAIPYIGTNLVMDSKGSSQKGSRLLL"
             "LLVVSNLLLCQGVVSTPVCPNGPGNCQVSLRDLFDRAVMVSHYIHDLSSARYSAFYNLLHCLRRDSSKIDTYLKLLNCRIIYNNNC*"
             ),
            ("seq3",
             "MKTLTRKLSRTAITLVLVILAFIAIFRAWVYYTESPWTRDARFSADVVAIAPDVAGLITHVNVHDNQLVKKDQVLFTIDQPRYQK"
             "ALAEAEADVAYYQVLAQEKRQEAGRRNRLGVQAMSREEIDQANNVLQTVLHQLAKAQATRDLAKLDLERTVIRAPADGWVTNLNV"
             "YAGEFITRGSTAVALVKKNSFYVQAYMEETKLEGVRPGYRAEITPLGSNRVLKGTVDSVAAGVTNASSTSDAKGMATIDSNLEWV"
             "RLAQRVPVRIRLDEQQGNLWPAGTTATVVITGKQDRDASQDSFFRKLAHRLREFG"
             ),
        )

        with tempfile.TemporaryFile("r+") as tf:
            write_fasta(fasta_sequences, tf)

            tf.seek(0)

            read_result = tuple(read_fasta(tf))
            self.assertEqual(read_result, fasta_sequences)
            pass
        return

    def test_read_fasta(self):
        print(tuple(read_fasta("/path/doesnt/exist")))
        with open(os.path.join(MONOMER_TEST_LOCATION, "fasta", "P01112.fasta"), 'r')  as fasta_file:
            self.assertEqual(tuple(read_fasta(fasta_file))[0],
                             ("sp|P01112|RASH_HUMAN GTPase HRas OS=Homo sapiens GN=HRAS PE=1 SV=1",
                              "MTEYKLVVVGAGGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDGETCLLDILDTAGQEEYSAMRDQYMRTGEGFLCVFAIN"
                              "NTKSFEDIHQYREQIKRVKDSDDVPMVLVGNKCDLAARTVESRQAQDLARSYGIPYIETSAKTRQGVEDAFYTLVREIRQHKLRK"
                              "LNPPDESGPGCMSCKCVLS"
                              )
                             )
            pass

        with open(os.path.join(MONOMER_TEST_LOCATION, "fasta", "valid.fasta"), 'r') as fasta_file:
            read_result = tuple(read_fasta(fasta_file))
            self.assertEqual(len(read_result), 3)

            self.assertEqual(read_result, (
                ("seq1",
                 "ADQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKDTDSEEEI"
                 "REAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTAK*"
                 ),
                ("seq2",
                 "LCLYTHIGRNIYYGSYLYSETWNTGIMLLLITMATAFMGYVLPWGQMSFWGATVITNLFSAIPYIGTNLVMDSKGSSQKGSRLLL"
                 "LLVVSNLLLCQGVVSTPVCPNGPGNCQVSLRDLFDRAVMVSHYIHDLSSARYSAFYNLLHCLRRDSSKIDTYLKLLNCRIIYNNNC*"
                 ),
                ("seq3",
                 "MKTLTRKLSRTAITLVLVILAFIAIFRAWVYYTESPWTRDARFSADVVAIAPDVAGLITHVNVHDNQLVKKDQVLFTIDQPRYQK"
                 "ALAEAEADVAYYQVLAQEKRQEAGRRNRLGVQAMSREEIDQANNVLQTVLHQLAKAQATRDLAKLDLERTVIRAPADGWVTNLNV"
                 "YAGEFITRGSTAVALVKKNSFYVQAYMEETKLEGVRPGYRAEITPLGSNRVLKGTVDSVAAGVTNASSTSDAKGMATIDSNLEWV"
                 "RLAQRVPVRIRLDEQQGNLWPAGTTATVVITGKQDRDASQDSFFRKLAHRLREFG"
                 ),
            )
                             )
            pass
        return

    def test_write_aln(self):
        pass

    def test_read_stockholm(self):
        pass

    def test_read_a3m(self):
        pass



if __name__ == '__main__':
    unittest.main()