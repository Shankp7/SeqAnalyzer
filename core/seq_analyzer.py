import re
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqUtils import MeltingTemp as mt, molecular_weight
from Bio.Restriction import EcoRI, HindIII, BamHI
import math

class SequenceAnalyzerBLL:
    def __init__(self):
        self.raw_sequence_string = ""
        self.sequence_id = ""
        self.total_length = 0
        self.gc_percentage = 0.0
        self.counts = {}
        self.tm_wallace = 0.0
        self.tm_salt = 0.0
        self.mol_weight = 0.0
        self.protein_seq = ""
        self.restriction_sites = {}
        self.entropy = 0.0
        self.invalid_count = 0

    def parse_fasta(self, file_path):
        # 1. The Waterfall Parser: Try all formats BioPython supports
        formats_to_try = ["fasta", "fasta-pearson", "fasta-blast"]
        last_error = None

        for fmt in formats_to_try:
            try:
                records = list(SeqIO.parse(file_path, fmt))
                if records:
                    self.sequence_id = records[0].id
                    self.raw_sequence_string = str(records[0].seq).upper()
                    return True  # Success! Stop trying other formats.
            except Exception as e:
                last_error = e
                continue # If it fails, loop around and try the next format

        # 2. Extreme Fallback: If BioPython completely rejects it, read it as raw text
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                seq_lines = [line.strip() for line in lines if not line.startswith(('>', ';', '!', '#'))]
                raw_text = "".join(seq_lines).upper()
                
                if len(raw_text) > 0:
                    self.sequence_id = "Custom_Sequence_Extracted"
                    self.raw_sequence_string = raw_text
                    return True
        except Exception as e:
            pass

        # 3. If we reach this point, the file is genuinely unreadable
        raise Exception(f"All parsing formats failed. BioPython reported: {str(last_error)}")

    def calculate_metrics(self):
        if not self.raw_sequence_string: return False
        
        clean_str = re.sub(r'[^ATGC]', '', self.raw_sequence_string)
        if len(clean_str) == 0:
            raise ValueError("Sequence contains no valid ATGC nucleotides. Ensure the file contains DNA data.")
            
        seq_obj = Seq(clean_str)
        self.total_length = len(self.raw_sequence_string)
        self.counts = {b: self.raw_sequence_string.count(b) for b in 'ATGC'}
        self.invalid_count = self.total_length - len(clean_str)
        
        self.gc_percentage = (self.counts['G'] + self.counts['C']) / len(clean_str) * 100 if len(clean_str) > 0 else 0
        
        self.mol_weight = molecular_weight(seq_obj, seq_type="DNA")
        self.tm_wallace = mt.Tm_Wallace(seq_obj)
        self.tm_salt = mt.Tm_GC(seq_obj, saltcorr=1)
        self.restriction_sites = {e.__name__: e.search(seq_obj) for e in [EcoRI, HindIII, BamHI]}
        
        self.entropy = 0.0
        for b in self.counts:
            p = self.counts[b] / self.total_length if self.total_length > 0 else 0
            if p > 0: self.entropy -= p * math.log2(p)

        c_len = (len(seq_obj) // 3) * 3
        self.protein_seq = str(seq_obj[:c_len].translate(to_stop=True))
        return True