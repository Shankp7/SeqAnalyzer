import customtkinter as ctk
import os
import csv
import subprocess
import threading
import queue
import matplotlib.pyplot as plt
from tkinter import filedialog, messagebox
from core.seq_analyzer import SequenceAnalyzerBLL
from database.db_handler import DatabaseHandlerDAL
from reports.pdf_generator import ReportGenerator

ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("green") 

class MainWindowUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SeqAnalyzer: A Professional Genomic Analysis Suite")
        self.width, self.height = 1150, 850

        icon_path = os.path.join(os.path.dirname(__file__), "laptop-dna.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        
        # Thread-safe mailbox
        self.thread_queue = queue.Queue()

        self.analyzer = SequenceAnalyzerBLL()
        self.db = DatabaseHandlerDAL()
        self.db.connect()
        self.session_id = self.db.start_session()
        self.reporter = ReportGenerator()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # UI Setup
        self.tabs = ctk.CTkTabview(self, corner_radius=15)
        self.tabs.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.tabs.add("Dashboard")
        self.tabs.add("History Logs")
        self.tabs.add("User Manual")

        self.setup_sidebar()
        self.setup_dashboard_tab()
        self.setup_history_tab()
        self.setup_help_tab()
        
        self.validate_button()
        self.center_window()

    def on_closing(self):
        self.quit()
        self.destroy()

    def center_window(self):
        # 1. Grab the monitor's logical dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (self.width / 2))
        y = int((screen_height / 2) - (self.height / 2)) - 40 # -40 pixels to lift it above the Taskbar
        
        # 3. Snap the window to the exact coordinates instantly
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Clean, punchy branding for the UI
        ctk.CTkLabel(self.sidebar, text="SeqAnalyzer", font=("Inter", 28, "bold")).pack(pady=30)
        
        self.name_var = ctk.StringVar()
        self.name_entry = ctk.CTkEntry(self.sidebar, textvariable=self.name_var, placeholder_text="Researcher Name")
        self.name_entry.pack(pady=5, padx=20)
        self.name_var.trace_add("write", self.validate_button)
        
        self.id_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Researcher ID")
        self.id_entry.pack(pady=5, padx=20)

        self.upload_btn = ctk.CTkButton(self.sidebar, text="Analyze Sequence", command=self.open_file_dialog)
        self.upload_btn.pack(pady=15, padx=20)

        self.loading_bar = ctk.CTkProgressBar(self.sidebar, mode="indeterminate", height=6)
        self.loading_bar.set(0)

        self.clear_btn = ctk.CTkButton(
            self.sidebar, 
            text="Clear Dashboard", 
            fg_color="#ef4444", 
            hover_color="#b91c1c",
            command=self.clear_dashboard
        )
        self.clear_btn.pack(pady=(20, 10), padx=20, side="bottom")

    def validate_button(self, *args):
        st = "normal" if self.name_var.get().strip() else "disabled"
        self.upload_btn.configure(state=st)

    def setup_dashboard_tab(self):
        self.dash_frame = self.tabs.tab("Dashboard")
        self.status_label = ctk.CTkLabel(self.dash_frame, text="System Ready", font=("Inter", 22, "bold"))
        self.status_label.pack(pady=(20, 5))
        
        self.metrics_box = ctk.CTkTextbox(self.dash_frame, font=("Consolas", 13), height=450, width=700)
        self.metrics_box.pack()
        
        self.btn_f = ctk.CTkFrame(self.dash_frame, fg_color="transparent")
        self.btn_f.pack(pady=15)
        
        self.pdf_btn = ctk.CTkButton(self.btn_f, text="PDF Report", command=self.save_report, state="disabled")
        self.pdf_btn.grid(row=0, column=0, padx=5)
        self.viz_btn = ctk.CTkButton(self.btn_f, text="Visualize", command=self.show_visuals, state="disabled", fg_color="#3498db")
        self.viz_btn.grid(row=0, column=1, padx=5)
        self.csv_btn = ctk.CTkButton(self.btn_f, text="Export CSV", command=self.export_csv, state="disabled")
        self.csv_btn.grid(row=0, column=2, padx=5)
        self.copy_btn = ctk.CTkButton(self.btn_f, text="Copy", border_width=1, command=self.copy_to_clipboard, state="disabled")
        self.copy_btn.grid(row=0, column=3, padx=5)

    def setup_history_tab(self):
        h_frame = self.tabs.tab("History Logs")
        search_f = ctk.CTkFrame(h_frame, fg_color="transparent")
        search_f.pack(fill="x", padx=20, pady=10)
        
        self.s_entry = ctk.CTkEntry(search_f, placeholder_text="Search Filename...", width=350)
        self.s_entry.pack(side="left", padx=10)
        self.s_entry.bind("<KeyRelease>", lambda e: self.refresh_history(self.s_entry.get()))

        self.wipe_btn = ctk.CTkButton(search_f, text="Wipe History", fg_color="#e74c3c", command=self.confirm_wipe)
        self.wipe_btn.pack(side="right", padx=10)

        self.hist_box = ctk.CTkTextbox(h_frame, font=("Consolas", 12), width=850, height=450)
        self.hist_box.pack(pady=10, padx=20)
        self.refresh_history()

    def setup_help_tab(self):
        m_frame = self.tabs.tab("User Manual")
        m_box = ctk.CTkTextbox(m_frame, font=("Inter", 13), width=850, height=550, wrap="word")
        m_box.pack(pady=20, padx=20)
        
        manual_text = """SeqAnalyzer: A Professional Genomic Analysis Suite - Comprehensive User Manual
========================================================

Welcome to SeqAnalyzer! This professional suite is designed to process, analyze, and visualize genomic sequences efficiently. Follow this guide to utilize all available features.

1. GETTING STARTED (AUTHENTICATION)
• Researcher Name: Enter your name in the sidebar. This field is required to unlock the analysis tools.
• Researcher ID: (Optional) Enter your institutional or project ID. Both fields will be embedded into your final exported PDF reports.

2. UPLOADING & ANALYZING DATA
• Click "Analyze Sequence" to upload your genomic data.
• Supported formats include: .fasta, .txt, .fna.
• The system features a robust "Waterfall Parser" that automatically handles standard FASTA, Pearson-formatted, or raw text sequences, filtering out comments and noise automatically.
• A background engine processes large files securely, ensuring the interface remains responsive while calculations are performed.

3. UNDERSTANDING THE DASHBOARD METRICS
Once loaded, the dashboard displays your Bio-Intelligence Summary:
• Primary Metrics: Includes Sequence Length, Molecular Weight, GC Content (with an automated structural stability rating), and the Shannon Entropy (Complexity Index).
• Thermal Dynamics: Displays Melting Temperatures (Tm) using both standard Wallace rules and Salt-Adjusted algorithms.
• Enzyme Mapping: Scans the sequence to locate EcoRI, HindIII, and BamHI restriction sites.
• Proteomic Translation: Provides the corresponding amino acid sequence (up to the first 200 characters).

4. INTERACTIVE VISUALIZATION
• Click "Visualize" to open a dedicated, high-resolution interactive chart showing the nucleotide distribution (A, T, G, C).
• This native graphing window allows you to hover over sections for exact percentages, pan, zoom, and save the chart directly to your system.

5. EXPORTING PROFESSIONAL REPORTS
• PDF Report: Generates a presentation-ready document containing all calculated metrics, your metadata, and an embedded distribution chart.
• Export CSV: Saves raw primary and thermal metrics into a spreadsheet format for external statistical tracking.
• Note: The software will automatically offer to open the destination folder once the export is successful.

6. MANAGING HISTORY LOGS
• Navigate to the "History Logs" tab to view all past analyses from your current session.
• Search: Type a filename in the search bar to instantly filter the internal SQLite database.
• Wipe History: Clears the local database completely (requires confirmation).
"""
        m_box.insert("0.0", manual_text)
        m_box.configure(state="disabled")

    def clear_dashboard(self):
        """Resets all UI elements and action buttons to their default state."""
        # 1. Clear the researcher inputs (clearing name_var auto-disables the upload button via validation)
        self.name_var.set("")
        self.id_entry.delete(0, 'end')
        
        # 2. Reset the main text box
        self.metrics_box.delete("0.0", "end")
        
        # 3. Reset the Title Label text back to default
        self.status_label.configure(text="System Ready", text_color="white")
        
        # 4. Disable the action buttons to prevent exporting empty reports
        for b in [self.pdf_btn, self.viz_btn, self.csv_btn, self.copy_btn]:
            b.configure(state="disabled")

    def show_visuals(self):
        plt.close('all') 
        filtered_data = {k: v for k, v in self.analyzer.counts.items() if v > 0}
        
        fig, ax = plt.subplots(figsize=(6, 6))
        fig.canvas.manager.set_window_title(f"Genomic Analytics: {self.analyzer.sequence_id}")
        fig.patch.set_facecolor('#2b2b2b')
        
        labels = list(filtered_data.keys())
        sizes = list(filtered_data.values())
        color_map = {'A': '#ff9999', 'T': '#66b3ff', 'G': '#99ff99', 'C': '#ffcc99'}
        colors = [color_map[label] for label in labels]

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, textprops={'color':"w", 'weight':'bold'})
        ax.set_title("Nucleotide Distribution", color="white", pad=20, fontsize=14)
        
        plt.show(block=False)

    def open_file_dialog(self):
        f_path = filedialog.askopenfilename(filetypes=[
            ("Genomic Files", "*.fasta *.fa *.fna *.txt"),
            ("All Files", "*.*")
        ])
        
        if not f_path: return

        self.upload_btn.configure(state="disabled", text="Processing...")
        self.loading_bar.pack(pady=(0, 10), padx=20)
        self.loading_bar.start()
        self.status_label.configure(text="Analyzing Bio-Data...", text_color="#f1c40f")

        def process_file_thread():
            success = False
            error_msg = "Unknown Error"
            try:
                if self.analyzer.parse_fasta(f_path):
                    if self.analyzer.calculate_metrics():
                        self.db.insert_log(self.session_id, os.path.basename(f_path), self.analyzer.total_length, self.analyzer.gc_percentage)
                        success = True
                    else:
                        error_msg = "Calculations failed. File data may be corrupted."
                else:
                    error_msg = "Could not detect a valid FASTA sequence format."
            except Exception as e:
                error_msg = str(e)
            
            self.thread_queue.put({"success": success, "path": f_path, "error": error_msg})

        threading.Thread(target=process_file_thread, daemon=True).start()
        self.check_queue()

    def check_queue(self):
        try:
            result = self.thread_queue.get_nowait()
            self.finish_processing(result["success"], result["path"], result["error"])
        except queue.Empty:
            self.after(100, self.check_queue)

    def finish_processing(self, success, f_path, error_msg=""):
        self.loading_bar.stop()
        self.loading_bar.pack_forget() 
        self.upload_btn.configure(state="normal", text="Analyze Sequence")

        if success:
            self.update_ui(os.path.basename(f_path))
            self.refresh_history()
        else:
            self.status_label.configure(text="System Ready", text_color="white")
            messagebox.showerror("Analysis Error", f"Failed to process file:\n\n{error_msg}")

    def update_ui(self, name):
        self.status_label.configure(text=f"Analysis: {name}", text_color="#2ecc71")
        stability_val = "High" if self.analyzer.gc_percentage > 55 else "Moderate" if self.analyzer.gc_percentage > 40 else "Low"
        
        res = (f"GENOMIC BIO-INTELLIGENCE SUMMARY\n{'='*40}\n\n"
               f"[PRIMARY METRICS]\nID: {self.analyzer.sequence_id}\nLength: {self.analyzer.total_length} bp\n"
               f"Molecular Weight: {self.analyzer.mol_weight:.2f} Da\n"
               f"GC Content: {self.analyzer.gc_percentage:.2f}% (Stability: {stability_val})\n"
               f"Complexity Index: {self.analyzer.entropy:.4f}\n"
               f"Invalid Bases: {self.analyzer.invalid_count}\n\n"
               f"[THERMAL PROPERTIES]\nTm Wallace: {self.analyzer.tm_wallace:.2f} C\nTm Salt: {self.analyzer.tm_salt:.2f} C\n\n"
               f"[ENZYME MAPPING]\n" + "\n".join([f"{k}: {', '.join(map(str,v)) if v else 'None'}" for k,v in self.analyzer.restriction_sites.items()]) + "\n\n"
               f"[PROTEIN TRANSLATION]\n{self.analyzer.protein_seq[:200]}...")
               
        self.metrics_box.delete("0.0", "end")
        self.metrics_box.insert("0.0", res)
        
        for b in [self.pdf_btn, self.viz_btn, self.csv_btn, self.copy_btn]: b.configure(state="normal")

    def save_report(self):
        s_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not s_path: return
        
        t_chart = "temp_p.png"
        filtered = {k: v for k, v in self.analyzer.counts.items() if v > 0}
        
        plt.figure(figsize=(4, 4))
        plt.pie(filtered.values(), labels=filtered.keys(), autopct='%1.1f%%')
        plt.savefig(t_chart, bbox_inches='tight')
        plt.close('all')
        
        stability_val = "High" if self.analyzer.gc_percentage > 55 else "Moderate" if self.analyzer.gc_percentage > 40 else "Low"
        
        r_data = {
            'id': self.analyzer.sequence_id, 'length': self.analyzer.total_length, 
            'gc': self.analyzer.gc_percentage, 'tm_w': self.analyzer.tm_wallace, 
            'tm_s': self.analyzer.tm_salt, 'sites': self.analyzer.restriction_sites, 
            'protein': self.analyzer.protein_seq, 'entropy': self.analyzer.entropy,
            'weight': self.analyzer.mol_weight, 
            'invalid': self.analyzer.invalid_count,  
            'stability': stability_val               
        }
        
        try:
            self.reporter.generate_analysis_report(r_data, self.name_entry.get(), self.id_entry.get(), s_path, t_chart)
            if os.path.exists(t_chart): os.remove(t_chart)
            if messagebox.askyesno("Success", "Professional PDF Generated! Open folder?"):
                subprocess.Popen(f'explorer /select,"{os.path.normpath(s_path)}"')
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save PDF:\n{str(e)}")
            if os.path.exists(t_chart): os.remove(t_chart)

    def export_csv(self):
        s_path = filedialog.asksaveasfilename(defaultextension=".csv")
        if s_path:
            with open(s_path, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(["Category", "Metric", "Value"])
                w.writerow(["PRIMARY", "ID", self.analyzer.sequence_id])
                w.writerow(["PRIMARY", "Length", f"{self.analyzer.total_length} bp"])
                w.writerow(["PRIMARY", "GC Content", f"{self.analyzer.gc_percentage:.2f}%"])
                w.writerow(["PRIMARY", "Complexity", f"{self.analyzer.entropy:.4f}"])
                w.writerow(["THERMAL", "Tm Wallace", f"{self.analyzer.tm_wallace:.2f} C"])
                w.writerow(["THERMAL", "Tm Salt", f"{self.analyzer.tm_salt:.2f} C"])
            if messagebox.askyesno("Success", "CSV Data Exported! Open folder?"):
                subprocess.Popen(f'explorer /select,"{os.path.normpath(s_path)}"')

    def refresh_history(self, f=""):
        logs = self.db.fetch_session_history(f)
        self.hist_box.delete("0.0", "end")
        self.hist_box.insert("0.0", f"{'FILENAME':<35} | {'LENGTH':<10} | {'GC%'}\n" + "-"*60 + "\n")
        for l in logs: self.hist_box.insert("end", f"{l[0]:<35} | {l[1]:<10} | {l[2]:.2f}%\n")

    def confirm_wipe(self):
        if messagebox.askyesno("Confirm", "Wipe all history records?"):
            self.db.clear_logs(); self.refresh_history()

    def copy_to_clipboard(self):
        self.clipboard_clear(); self.clipboard_append(self.metrics_box.get("0.0", "end"))
        messagebox.showinfo("Copied", "Data copied.")

if __name__ == "__main__":
    app = MainWindowUI()
    
    try:
        import pyi_splash  # type: ignore
        pyi_splash.close()
    except ImportError:
        pass
        
    app.mainloop()