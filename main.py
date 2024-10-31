"""
Code Clone Detection Tool

This script provides a GUI-based tool for detecting code clones within a specified directory.
It uses Tkinter for the GUI, allowing users to:
- Load code files from a selected directory.
- Run a clone detection process, which classifies clones based on similarity.
- Adjust sensitivity settings for detection.
- Save clone detection reports as CSV or PDF files.

Detection sensitivity is controlled by a slider in the settings window, which allows users to define
how strict the similarity threshold should be for clone classification.

Clone detection types:
- Type 1: 100% similarity.
- Type 2: 90% similarity.
- Type 3: 70% similarity.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import difflib
import os
import threading
import re
import csv
from fpdf import FPDF  # Install with: pip install fpdf

current_sensitivity = 9  # Default sensitivity
clone_results = []  # Store clone results


def calculate_similarity(code1, code2):
    """
    Calculates similarity between two pieces of code using difflib's SequenceMatcher.
    Cleans code strings before calculation.

    Parameters:
        code1 (str): The first code snippet to compare.
        code2 (str): The second code snippet to compare.

    Returns:
        float: The similarity ratio between code1 and code2.
    """
    cleaned_code1 = clean_code(code1)
    cleaned_code2 = clean_code(code2)
    return difflib.SequenceMatcher(None, cleaned_code1, cleaned_code2).ratio()


def clean_code(code):
    """
    Removes comments, import statements, and excess whitespace from code.

    Parameters:
        code (str): The code to clean.

    Returns:
        str: The cleaned code.
    """
    cleaned = re.sub(r"^\s*(#.*|from .*|import .*)$", "", code, flags=re.MULTILINE)
    return "\n".join([line for line in cleaned.splitlines() if line.strip()])


def load_code_from_directory(directory):
    """
    Loads and returns code files from a specified directory.

    Parameters:
        directory (str): Directory path to load code files from.

    Returns:
        list: A list of tuples containing file names and their code as a list of lines.
    """
    code_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".py", ".java")):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    code_files.append((file, f.read().splitlines()))
    return code_files


def detect_clones_with_sensitivity(code_files):
    """
    Detects and classifies code clones based on current sensitivity level.

    Parameters:
        code_files (list): List of tuples containing file names and code lines.
    """
    global clone_results
    clone_results.clear()
    for file_name, lines in code_files:
        for i, line1 in enumerate(lines):
            for j, line2 in enumerate(lines):
                if i != j:
                    similarity = calculate_similarity(line1, line2)
                    classify_clone(file_name, i, j, similarity)


def classify_clone(file_name, line1, line2, similarity):
    """
    Classifies a clone based on similarity into one of three types.

    Parameters:
        file_name (str): Name of the file where the clone was detected.
        line1 (int): First line number of the clone.
        line2 (int): Second line number of the clone.
        similarity (float): Calculated similarity between the two code lines.
    """
    if similarity >= 1.0 * (current_sensitivity / 10):
        clone_results.append(("Type 1", line1 + 1, line2 + 1, f"{similarity:.2%}", file_name))
    elif similarity >= 0.9 * (current_sensitivity / 10):
        clone_results.append(("Type 2", line1 + 1, line2 + 1, f"{similarity:.2%}", file_name))
    elif similarity >= 0.7 * (current_sensitivity / 10):
        clone_results.append(("Type 3", line1 + 1, line2 + 1, f"{similarity:.2%}", file_name))


def open_directory():
    """
    Opens a file dialog to select a directory and loads code files for display.
    """
    directory_path = filedialog.askdirectory(title="Select a Directory")
    if directory_path:
        code_files = load_code_from_directory(directory_path)
        code_display.delete(1.0, tk.END)
        for file_name, lines in code_files:
            code_display.insert(tk.END, f"### {file_name} ###\n")
            code_display.insert(tk.END, "\n".join(lines) + "\n")


def run_clone_detection_in_thread():
    """
    Runs clone detection in a separate thread to prevent GUI freezing.
    """
    threading.Thread(target=detect_clones).start()


def detect_clones():
    """
    Loads code files and detects clones, then displays the results.
    """
    code_files = load_code_from_directory(filedialog.askdirectory())
    detect_clones_with_sensitivity(code_files)
    display_clone_results()


def display_clone_results():
    """
    Displays clone detection results in the GUI's listbox.
    """
    results_listbox.delete(0, tk.END)
    for result in clone_results:
        results_listbox.insert(tk.END, f"{result}")


def save_report_as_csv():
    """
    Saves clone detection results as a CSV file.
    """
    report_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if report_path:
        with open(report_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Clone Type", "Line 1", "Line 2", "Similarity", "File"])
            writer.writerows(clone_results)
        messagebox.showinfo("Save Report", f"Report saved successfully at {report_path}")


def save_report_as_pdf():
    """
    Saves clone detection results as a PDF file.
    """
    report_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if report_path:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Code Clone Detection Report", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=10)
        for clone_type, line1, line2, similarity, file_name in clone_results:
            pdf.cell(200, 10, txt=f"{clone_type}: {file_name} - Lines {line1} and {line2} (Similarity: {similarity})",
                     ln=True)
        pdf.output(report_path)
        messagebox.showinfo("Save Report", f"PDF saved successfully at {report_path}")


def open_settings():
    """
    Opens settings window to adjust detection sensitivity.
    """
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    tk.Label(settings_window, text="Detection Sensitivity").pack(pady=10)
    sensitivity_slider = tk.Scale(settings_window, from_=1, to=10, orient=tk.HORIZONTAL)
    sensitivity_slider.set(current_sensitivity)
    sensitivity_slider.pack(pady=10)
    tk.Button(settings_window, text="Apply", command=lambda: apply_settings(sensitivity_slider.get())).pack(pady=10)


def apply_settings(sensitivity):
    """
    Applies the selected sensitivity setting to adjust clone detection threshold.

    Parameters:
        sensitivity (int): The selected sensitivity level (1-10).
    """
    global current_sensitivity
    current_sensitivity = sensitivity


# Tkinter GUI Setup

root = tk.Tk()
root.title("Code Clone Detection Tool")
root.geometry("900x700")

code_display = tk.Text(root, wrap="none", height=15, width=80)
code_display.pack(padx=10, pady=10)

results_listbox = tk.Listbox(root, height=15, width=80)
results_listbox.pack(padx=10, pady=10)

open_button = tk.Button(root, text="Open Codebase", command=open_directory)
open_button.pack(pady=5)

run_button = tk.Button(root, text="Run Clone Detection", command=run_clone_detection_in_thread)
run_button.pack(pady=5)

settings_button = tk.Button(root, text="Settings", command=open_settings)
settings_button.pack(pady=5)

save_csv_button = tk.Button(root, text="Save Report as CSV", command=save_report_as_csv)
save_csv_button.pack(pady=5)

save_pdf_button = tk.Button(root, text="Save Report as PDF", command=save_report_as_pdf)
save_pdf_button.pack(pady=5)

progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='indeterminate')
progress.pack(pady=10)

root.mainloop()
