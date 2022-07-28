import unittest
import filecmp
import sbol3
import os
from pathlib import Path
from helpers import copy_to_tmp
from sbol_utilities.sbol_diff import doc_diff
from sbol_utilities.sbol3_genbank_conversion import (
    GenBank_SBOL3_Converter,
    TEST_NAMESPACE,
)


class TestGenBankSBOL3(unittest.TestCase):
    # Create converter instance
    converter = GenBank_SBOL3_Converter()

    def _test_genbank_to_sbol3(self, SAMPLE_SBOL3_FILE: Path, SAMPLE_GENBANK_FILE: Path):
        """Helper method to test conversion of a given GenBank file to SBOL3 using new converter.
        :param SAMPLE_SBOL3_FILE: Path of expected SBOL3 converted file
        :param SAMPLE_GENBANK_FILE: Path of given GenBank file to convert
        """
        TEST_OUTPUT_SBOL3 = str(SAMPLE_SBOL3_FILE) + ".test"
        # Don't write to file for testing, we directly compare sbol documents
        test_output_sbol3 = self.converter.convert_genbank_to_sbol3(
            str(SAMPLE_GENBANK_FILE),
            TEST_OUTPUT_SBOL3,
            namespace=TEST_NAMESPACE,
            write=False,
        )
        sbol3_file_1 = sbol3.Document()
        sbol3_file_1.read(
            location=str(SAMPLE_SBOL3_FILE), file_format=sbol3.SORTED_NTRIPLES
        )
        assert not doc_diff(
            test_output_sbol3, sbol3_file_1
        ), f"Converted SBOL3 file: {TEST_OUTPUT_SBOL3} not identical to expected file: {SAMPLE_SBOL3_FILE}"
    
    def _test_sbol3_to_genbank(self, SAMPLE_SBOL3_FILE: Path, SAMPLE_GENBANK_FILE: Path):
        """Helper method to test conversion of a given SBOL3 file to GenBank using new converter.
        :param SAMPLE_SBOL3_FILE: Path of given SBOL3 file to convert
        :param SAMPLE_GENBANK_FILE: Path of expected GenBank converted file 
        """
        # create tmp directory to store generated genbank file in for comparison
        tmp_sub = copy_to_tmp(package=[str(SAMPLE_SBOL3_FILE)])
        doc3 = sbol3.Document()
        doc3.read(str(SAMPLE_SBOL3_FILE))
        # Convert to GenBank and check contents
        outfile = os.path.join(tmp_sub, str(SAMPLE_GENBANK_FILE).split("/")[-1] + ".test")
        self.converter.convert_sbol3_to_genbank(
            sbol3_file=None, doc=doc3, gb_file=outfile, write=True
        )
        comparison_file = str(SAMPLE_GENBANK_FILE)
        assert filecmp.cmp(
            outfile, comparison_file
        ), f"Converted GenBank file {outfile} is not identical to expected file {comparison_file}"

    def _test_round_trip_genbank(self, SAMPLE_GENBANK_FILE: Path):
        """Helper method to test conversion of a given GenBank file to SBOL3 and then back to GenBank 
        and confirm the final file is exactly the same as the initial provided file.
        :param SAMPLE_GENBANK_FILE: Path of given GenBank file to round trip test
        """
        sbol3.set_namespace(TEST_NAMESPACE)
        TEST_OUTPUT_SBOL3 = str(SAMPLE_GENBANK_FILE) + ".nt"
        # Don't write to file for testing, we directly compare sbol documents
        test_output_sbol3 = self.converter.convert_genbank_to_sbol3(
            str(SAMPLE_GENBANK_FILE),
            TEST_OUTPUT_SBOL3,
            namespace=TEST_NAMESPACE,
            write=False,
        )
        # create tmp directory to store generated genbank file in for comparison
        tmp_sub = copy_to_tmp(package=[str(SAMPLE_GENBANK_FILE)])
        # Convert to GenBank and check contents
        outfile = os.path.join(tmp_sub, str(SAMPLE_GENBANK_FILE).split("/")[-1] + ".test")
        self.converter.convert_sbol3_to_genbank(
            sbol3_file=None, doc=test_output_sbol3, gb_file=outfile, write=True
        )
        comparison_file = str(SAMPLE_GENBANK_FILE)
        assert filecmp.cmp(
            outfile, comparison_file
        ), f"Converted GenBank file {outfile} is not identical to expected file {comparison_file}"

    def test_gbtosbol3_1(self):
        """Test conversion of a simple genbank file with a single sequence"""
        GENBANK_FILE = Path(__file__).parent / "test_files" / "BBa_J23101.gb"
        SBOL3_FILE = (
            Path(__file__).parent
            / "test_files"
            / "sbol3_genbank_conversion"
            / "BBa_J23101_from_genbank_to_sbol3_direct.nt"
        )
        sbol3.set_namespace(TEST_NAMESPACE)
        self._test_genbank_to_sbol3(SAMPLE_SBOL3_FILE=SBOL3_FILE, SAMPLE_GENBANK_FILE=GENBANK_FILE)

    def test_gbtosbol3_2(self):
        """Test conversion of a simple genbank file with a multiple sequence with multiple features"""
        GENBANK_FILE = (
            Path(__file__).parent / "test_files" / "iGEM_SBOL2_imports.gb"
        )
        SBOL3_FILE = (
            Path(__file__).parent
            / "test_files"
            / "sbol3_genbank_conversion"
            / "iGEM_SBOL2_imports_from_genbank_to_sbol3_direct.nt"
        )
        sbol3.set_namespace(TEST_NAMESPACE)
        self._test_genbank_to_sbol3(SAMPLE_SBOL3_FILE=SBOL3_FILE, SAMPLE_GENBANK_FILE=GENBANK_FILE)

    def test_sbol3togb_1(self):
        """Test ability to convert from SBOL3 to GenBank using new converter"""
        GENBANK_FILE = (
            Path(__file__).parent / "test_files" / "sbol3_genbank_conversion" / "BBa_J23101_from_sbol3_direct.gb"
        )
        SBOL3_FILE = (
            Path(__file__).parent
            / "test_files"
            / "sbol3_genbank_conversion"
            / "BBa_J23101_from_genbank_to_sbol3_direct.nt"
        )
        self._test_sbol3_to_genbank(SAMPLE_SBOL3_FILE=SBOL3_FILE, SAMPLE_GENBANK_FILE=GENBANK_FILE)

    def test_sbol3togb_2(self):
        """Test ability to convert from SBOL3 to GenBank with multiple records/features using new converter"""
        GENBANK_FILE = (
            Path(__file__).parent / "test_files" / "sbol3_genbank_conversion" / "iGEM_SBOL2_imports_from_sbol3_direct.gb"
        )
        SBOL3_FILE = (
            Path(__file__).parent
            / "test_files"
            / "sbol3_genbank_conversion"
            / "iGEM_SBOL2_imports_from_genbank_to_sbol3_direct.nt"
        )
        self._test_sbol3_to_genbank(SAMPLE_SBOL3_FILE=SBOL3_FILE, SAMPLE_GENBANK_FILE=GENBANK_FILE)

    def test_round_trip_extra_properties(self):
        """Test ability to produce same genbank file on round trip when original genbank file has non standard
        values for extraneous properties
        """
        GENBANK_FILE = (
            Path(__file__).parent / "test_files" / "sbol3_genbank_conversion" / "test_extra_properties.gb"
        )
        self._test_round_trip_genbank(GENBANK_FILE)
    

if __name__ == "__main__":
    unittest.main()
