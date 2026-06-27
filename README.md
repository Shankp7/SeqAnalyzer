# SeqAnalyzer 🧬

SeqAnalyzer is a secure, offline Python desktop utility designed to parse, analyze, and log massive genomic FASTA files. Built out of a desire to bridge software engineering with the life sciences, this application addresses the common challenge of processing heavy datasets locally without locking up the user interface.

## 🛠️ Architecture & Core Features

The application is built using a modular architecture that cleanly separates the user interface, background processing, and data storage layers.



### 1. Multithreaded Processing Engine
* **Responsive UI:** The core parsing engine offloads heavy computations to dedicated background worker threads. This prevents the interface from freezing, keeping the application 100% responsive even when crunching gigabytes of sequence data.
* **Stream Parsing:** Files are read iteratively rather than being loaded entirely into RAM, maintaining a highly optimized memory footprint.

### 2. Modern CustomTkinter Interface
* **Interactive Dashboard:** Designed with a sleek, dark-mode optimized GUI using CustomTkinter for a professional user experience.
* **Real-Time Feedback:** Includes live progress tracking and status indicators driven by thread-safe communication mechanics.

### 3. Local History Tracking (SQLite3)
* **Lightweight Storage:** Uses an embedded SQLite3 database to log historical analysis runs securely on your local machine.
* **Instant Recall:** Users can instantly review metrics and data from past sequences without needing to spend time re-parsing the original raw files.

### 4. Automated Reporting (ReportLab)
* **PDF Export:** Generates clean, publication-ready bioinformatics reports automatically using ReportLab.
* **Offline Sharing:** Reports are saved directly to the local file system for immediate offline review or distribution.

---

## 🚀 Feature Walkthrough & Usage

Below is a breakdown of the core workflow within the utility:

### Step 1: Data Ingestion
* Select a local `.fasta` file through the dashboard file picker. The application verifies file integrity before initializing the parsing sequence to prevent runtime allocation errors.

### Step 2: Sequence Analysis
![SeqAnalyzer Dashboard](dashboard.png)
* Once processing begins, the background thread extracts key genomic metrics (such as nucleotide distribution, GC-content, and sequence lengths) while you navigate the application.

### Step 3: History & Reports
* View past execution logs under the **History Logs** tab. 
* Click the export button to instantly generate a structured PDF report detailing the findings of your latest sequence analysis.

---

## 📈 Performance & Computational Complexity

* **Time Complexity:** $O(N)$ where $N$ is the total number of characters/lines in the FASTA file. The engine streams the file from top to bottom exactly once, ensuring execution time scales linearly with file size.
* **Space (Memory) Complexity:** $O(1)$ constant memory overhead for the streaming worker thread, ensuring the application remains lightweight regardless of dataset size.

---

## 🤝 Acknowledgments

A huge thank you to my project guide, **Dr. Pratima Bhagat**, for her invaluable microbiology expertise and for helping me bridge the gap between complex code and the life sciences during this capstone project.

---

## ⚖️ License

This project is open-source and licensed under the **GNU General Public License v3.0**. 

```text
SeqAnalyzer
Copyright (C) 2026 Shashank Parte

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.