import math
import os
from Bio.Seq import Seq
from Bio.Data import IUPACData

class SequenceAnalyzerBLL:
    def __init__(self):
        self.file_path = ""
        self.sequence_id = ""
        self.total_length = 0
        self.gc_percentage = 0.0
        self.counts = {'A': 0, 'T': 0, 'G': 0, 'C': 0}
        self.tm_wallace = 0.0
        self.tm_salt = 0.0
        self.mol_weight = 0.0
        self.protein_seq = ""
        self.restriction_sites = {'EcoRI': [], 'HindIII': [], 'BamHI': []}
        self.entropy = 0.0
        self.invalid_count = 0

    def parse_fasta(self, file_path):
        """
        Validates the file and extracts the first sequence ID without loading the whole file into memory.
        """
        if not os.path.exists(file_path):
            raise Exception("File does not exist.")
        self.file_path = file_path
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    self.sequence_id = line[1:].split()[0]
                    break
                elif line and not line.startswith((';', '!', '#')):
                    # If we find sequence data without a fasta header
                    self.sequence_id = "Custom_Sequence_Extracted"
                    break
        
        if not self.sequence_id:
            raise Exception("Could not detect any valid sequence data in the file.")
            
        return True

    def calculate_metrics(self):
        if not self.file_path: return False
        
        counts = {'A': 0, 'T': 0, 'G': 0, 'C': 0}
        invalid_count = 0
        total_length = 0
        
        # Buffer to catch restriction sites that span across line chunks (all targeted sites are 6bp, so 5bp buffer is sufficient)
        buffer = ""
        
        # We only need the first 600 bases for the protein translation (200 amino acids)
        first_600_bases = []
        
        # Restriction sites positions
        ecori_positions = []
        hindiii_positions = []
        bamhi_positions = []
        
        current_pos = 0 # tracks position in the purely valid DNA sequence
        
        with open(self.file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(('>', ';', '!', '#')):
                    continue
                
                raw_chunk = line.upper()
                total_length += len(raw_chunk)
                
                # filter invalid bases
                chunk = "".join(c for c in raw_chunk if c in 'ATGC')
                invalid_count += len(raw_chunk) - len(chunk)
                
                if not chunk: continue
                
                for b in chunk:
                    counts[b] += 1
                    
                if len(first_600_bases) < 600:
                    first_600_bases.append(chunk)
                
                search_seq = buffer + chunk
                
                def find_all(sub, s, offset):
                    res = []
                    idx = s.find(sub)
                    while idx != -1:
                        # 1-indexed to match Bio.Restriction output formatting
                        res.append(offset + idx + 1)
                        idx = s.find(sub, idx + 1)
                    return res

                # Adjust offset for the search_seq relative to the global valid sequence length
                offset = current_pos - len(buffer)
                
                # Cap storing positions to avoid memory blowup on GB-sized files
                if len(ecori_positions) < 1000:
                    ecori_positions.extend(find_all("GAATTC", search_seq, offset))
                if len(hindiii_positions) < 1000:
                    hindiii_positions.extend(find_all("AAGCTT", search_seq, offset))
                if len(bamhi_positions) < 1000:
                    bamhi_positions.extend(find_all("GGATCC", search_seq, offset))
                
                current_pos += len(chunk)
                buffer = search_seq[-5:] if len(search_seq) >= 5 else search_seq

        valid_length = current_pos
        if valid_length == 0:
            raise ValueError("Sequence contains no valid ATGC nucleotides. Ensure the file contains DNA data.")
            
        self.total_length = total_length
        self.counts = counts
        self.invalid_count = invalid_count
        
        gc_count = counts['G'] + counts['C']
        self.gc_percentage = (gc_count / valid_length) * 100 if valid_length > 0 else 0
        
        # Calculate DNA Molecular Weight EXACTLY matching BioPython
        weight_sum = sum(counts[b] * IUPACData.unambiguous_dna_weights[b] for b in counts)
        weight_of_water = 18.01528
        self.mol_weight = weight_sum - (valid_length - 1) * weight_of_water
                           
        # Tm Wallace
        self.tm_wallace = 2.0 * (counts['A'] + counts['T']) + 4.0 * (counts['G'] + counts['C'])
        
        # Tm Salt (Tm_GC) using BioPython's default valueset=7 and saltcorr=1
        self.tm_salt = 81.5 + 0.41 * self.gc_percentage - (600.0 / valid_length) + 16.6 * math.log10(0.05)
        
        # Shannon Entropy
        self.entropy = 0.0
        for b in counts:
            p = counts[b] / total_length if total_length > 0 else 0
            if p > 0: self.entropy -= p * math.log2(p)

        # Translation (only first 200 aa = 600 bp)
        first_bases_str = "".join(first_600_bases)[:600]
        seq_obj = Seq(first_bases_str)
        c_len = (len(seq_obj) // 3) * 3
        self.protein_seq = str(seq_obj[:c_len].translate(to_stop=True))
        
        self.restriction_sites = {
            'EcoRI': ecori_positions[:1000],
            'HindIII': hindiii_positions[:1000],
            'BamHI': bamhi_positions[:1000]
        }
        
        return True