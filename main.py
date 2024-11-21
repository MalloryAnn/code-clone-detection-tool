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

current_sensitivity = 9  # Default sensitivity for detection
clone_results = []  # Store results of clone detection

# Global counters for the different types of clones
total_exact_clones = 0  # Counter for exact clones (Type 1)
total_renamed_clones = 0  # Counter for renamed clones (Type 2)
total_modified_clones = 0  # Counter for modified clones (Type 3)


def calculate_similarity(code1: str, code2: str) -> float:
    """
    Calculates similarity between two pieces of code using difflib's SequenceMatcher.
    Cleans code strings before calculation.

    Parameters:
        code1 (str): The first code snippet to compare.
        code2 (str): The second code snippet to compare.

    Returns:
        float: The similarity ratio between code1 and code2.
    """
    cleaned_code1 = clean_code(code1)  # Clean the first code snippet
    cleaned_code2 = clean_code(code2)  # Clean the second code snippet
    return difflib.SequenceMatcher(None, cleaned_code1, cleaned_code2).ratio()  # Return similarity ratio


def clean_code(code: str) -> str:
    """
    Removes comments, import statements, and excess whitespace from code.

    Parameters:
        code (str): The code to clean.

    Returns:
        str: The cleaned code.
    """
    cleaned = re.sub(r"^\s*(#.*|from .*|import .*)$", "", code, flags=re.MULTILINE)  # Remove comments and imports
    return "\n".join([line for line in cleaned.splitlines() if line.strip()])  # Return cleaned code


def load_code_from_files(file_paths: list[str]) -> list[tuple[str, list[str]]]:
    """
    Loads and returns code from specified files.

    Parameters:
        file_paths (list[str]): List of file paths to load code from.

    Returns:
        list[tuple[str, list[str]]]: A list of tuples containing file names and their code as a list of lines.
    """
    code_files = []  # Initialize list to hold code file data
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as f:
            code_files.append((os.path.basename(file_path), f.read().splitlines()))  # Append file name and lines
    return code_files


def detect_clones_with_sensitivity(code_files: list[tuple[str, list[str]]]):
    """
    Detects clones with sensitivity adjustments, including renamed and modified clones.

    Parameters:
        code_files (list[tuple[str, list[str]]]): List of code files to analyze.
    """
    global clone_results
    clone_results.clear()  # Clear previous results

    for file_name, lines in code_files:  # Iterate over each file and its lines
        for i, line1 in enumerate(lines):  # Compare each line to others
            for j, line2 in enumerate(lines):
                if i != j:  # Ensure not comparing the same line
                    # Calculate exact similarity
                    similarity = calculate_similarity(line1, line2)
                    classify_clone(file_name, i, j, similarity)  # Classify based on similarity

                    # Additional logic for renamed and modified clones
                    if is_renamed_clone(line1, line2):
                        classify_clone(file_name, i, j, 0.85)  # Threshold for renamed clones
                    elif is_modified_clone(line1, line2):
                        classify_clone(file_name, i, j, 0.75)  # Threshold for modified clones


def is_renamed_clone(line1: str, line2: str) -> bool:
    """
    Determines if line1 is a renamed version of line2.

    Parameters:
        line1 (str): The first line of code.
        line2 (str): The second line of code.

    Returns:
        bool: True if line1 is a renamed version of line2, False otherwise.
    """
    # Logic to compare structures while ignoring variable names will go here
    return False  # Placeholder for actual implementation


def is_modified_clone(line1: str, line2: str) -> bool:
    """
    Determines if line1 has minor modifications compared to line2.

    Parameters:
        line1 (str): The first line of code.
        line2 (str): The second line of code.

    Returns:
        bool: True if line1 has modifications compared to line2, False otherwise.
    """
    # Logic for detecting slight modifications should go here
    return False  # Placeholder for actual implementation


def classify_clone(file_name: str, line1: int, line2: int, similarity: float):
    """
    Classifies a clone based on similarity exclusively based on the slider setting.

    Parameters:
        file_name (str): Name of the file where the clone was detected.
        line1 (int): First line number of the clone.
        line2 (int): Second line number of the clone.
        similarity (float): Calculated similarity between the two code lines.
    """
    global total_exact_clones, total_renamed_clones, total_modified_clones

    # Convert current sensitivity from percentage to decimal
    threshold = current_sensitivity / 100.0

    # Adjust logic to ensure exclusive detection
    if threshold == 1.0 and similarity == 1.0:  # Type 1 clones only at 100% threshold
        clone_results.append(("Type 1", line1 + 1, line2 + 1, f"{similarity:.2%}", file_name))
        total_exact_clones += 1
    elif threshold == 0.9 and 0.9 <= similarity < 1.0:  # Type 2 clones only at 90% threshold
        clone_results.append(("Type 2", line1 + 1, line2 + 1, f"{similarity:.2%}", file_name))
        total_renamed_clones += 1

    elif threshold == 0.7 and 0.7 <= similarity < 0.9:  # Type 3 clones only at 70% threshold
        clone_results.append(("Type 3", line1 + 1, line2 + 1, f"{similarity:.2%}", file_name))
        total_modified_clones += 1


def open_code_files():
    """Opens a file dialog to select code files and loads them for display."""
    file_paths = filedialog.askopenfilenames(
        title="Select Code Files",
        filetypes=[("Python Files", "*.py"), ("Java Files", "*.java")]
    )

    if file_paths:  # Check if any files were selected
        code_display.delete(1.0, tk.END)  # Clear the text display
        code_files = load_code_from_files(file_paths)  # Load the selected files

        for file_name, lines in code_files:
            code_display.insert(tk.END, f"### {file_name} ###\n")  # Display file name
            code_display.insert(tk.END, "\n".join(lines) + "\n")  # Display code lines
    else:
        messagebox.showwarning("Warning", "No files selected.")  # Warning if no files selected


def run_clone_detection_in_thread():
    """
    Runs clone detection in a separate thread to prevent GUI freezing.
    """
    threading.Thread(target=detect_clones).start()  # Start detection in a new thread


def detect_clones():
    """
    Loads code files and detects clones, then displays the results.
    """
    file_paths = filedialog.askopenfilenames(
        title="Select Code Files",
        filetypes=[("Python Files", "*.py"), ("Java Files", "*.java")]
    )

    # Convert the tuple of file paths to a list for further processing
    file_paths = list(file_paths)

    if file_paths:  # Check if any files were selected
        code_files = load_code_from_files(file_paths)  # Load the selected files
        detect_clones_with_sensitivity(code_files)  # Detect clones with specified sensitivity
        display_clone_results()  # Display the results in the GUI
    else:
        messagebox.showwarning("Warning", "No files selected.")  # Warning if no files selected


def display_clone_results():
    """
    Displays clone detection results in the GUI's listbox.
    """
    results_listbox.delete(0, tk.END)  # Clear previous results
    for result in clone_results:
        results_listbox.insert(tk.END, f"{result}")  # Insert each result into the listbox


def save_report_as_csv():
    """
    Saves the detection results as a CSV file, including clone metrics.
    """
    report_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if report_path:
        with open(report_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Clone Type", "Line 1", "Line 2", "Similarity", "File"])  # Write header
            writer.writerows(clone_results)  # Write detected clone results
            # Add overall metrics
            writer.writerow([])  # Add empty row for separation
            writer.writerow(["Metrics"])  # Write metrics header
            writer.writerow(["Total Exact Clones", total_exact_clones])  # Total exact clones
            writer.writerow(["Total Renamed Clones", total_renamed_clones])  # Total renamed clones
            writer.writerow(["Total Modified Clones", total_modified_clones])  # Total modified clones
        messagebox.showinfo("Save Report", f"Report saved successfully at {report_path}")  # Confirmation message


def save_report_as_pdf():
    """
    Saves clone detection results as a PDF file.
    """
    report_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if report_path:
        pdf = FPDF()  # Create PDF instance
        pdf.add_page()  # Add a new page
        pdf.set_font("Arial", size=12)  # Set font for title
        pdf.cell(200, 10, txt="Code Clone Detection Report", ln=True, align='C')  # Title of the report
        pdf.ln(10)  # Add line break
        pdf.set_font("Arial", size=10)  # Set font for content
        for clone_type, line1, line2, similarity, file_name in clone_results:
            # Write each clone result to the PDF
            pdf.cell(200, 10, txt=f"{clone_type}: {file_name} - Lines {line1} and {line2} (Similarity: {similarity})",
                     ln=True)
        pdf.output(report_path)  # Save the PDF
        messagebox.showinfo("Save Report", f"PDF saved successfully at {report_path}")  # Confirmation message


def recommend_refactoring():
    """
    Generates recommendations for refactoring based on detected clones.
    """
    recommendations = []  # Initialize recommendations list
    for clone in clone_results:
        clone_type, line1, line2, similarity, file_name = clone
        if clone_type == "Type 1":
            recommendations.append(
                f"Consider removing exact duplicates in {file_name} at lines {line1} and {line2}.")  # Recommendation for Type 1
        elif clone_type == "Type 2":
            recommendations.append(
                f"Rename variables in {file_name} to avoid redundancy at lines {line1} and {line2}.")  # Recommendation for Type 2
        elif clone_type == "Type 3":
            recommendations.append(
                f"Consolidate similar code in {file_name} found at lines {line1} and {line2}.")  # Recommendation for Type 3
    return recommendations  # Return list of recommendations


def open_settings():
    """
    Opens settings window to adjust detection sensitivity.
    """
    settings_window = tk.Toplevel(root)  # Create a new window for settings
    settings_window.title("Settings")  # Set window title
    tk.Label(settings_window, text="Detection Sensitivity").pack(pady=10)  # Label for sensitivity slider
    sensitivity_slider = tk.Scale(settings_window, from_=1, to=10, orient=tk.HORIZONTAL)  # Create slider
    sensitivity_slider.set(current_sensitivity)  # Set slider to current sensitivity
    sensitivity_slider.pack(pady=10)  # Pack the slider into the window
    tk.Button(settings_window, text="Apply", command=lambda: apply_settings(sensitivity_slider.get())).pack(
        pady=10)  # Button to apply settings


def apply_settings(sensitivity):
    """
    Applies the selected sensitivity setting to adjust clone detection threshold.

    Parameters:
        sensitivity (int): The selected sensitivity level (1-10).
    """
    global current_sensitivity
    current_sensitivity = sensitivity  # Update current sensitivity level

# Tkinter GUI Setup
root = tk.Tk()
root.title("Code Clone Detection Tool")
root.geometry("900x900")

# Text area to display code
code_display = tk.Text(root, wrap="none", height=15, width=80)
code_display.pack(padx=10, pady=10)

# Listbox to display detection results
results_listbox = tk.Listbox(root, height=15, width=80)
results_listbox.pack(padx=10, pady=10)

# Buttons for various actions
open_button = tk.Button(root, text="Open Code Files", command=open_code_files)
open_button.pack(pady=5)

run_button = tk.Button(root, text="Run Clone Detection", command=run_clone_detection_in_thread)
run_button.pack(pady=5)


# Add similarity slider directly to the main GUI
tk.Label(root, text="Detection Similarity Scale: Select BEFORE choosing the file").pack(pady=10)  # Clearer label for slider
similarity_slider = tk.Scale(root, from_=10, to=100, orient=tk.HORIZONTAL, resolution=10)  # Slider for similarity scale
similarity_slider.set(70)  # Default to 70% similarity
similarity_slider.pack(pady=10)  # Add slider to GUI

# Apply button to update similarity threshold
def update_similarity():
    global current_sensitivity
    current_sensitivity = similarity_slider.get()  # Update similarity to the selected value
    messagebox.showinfo("Similarity Updated", f"Detection Similarity set to: {current_sensitivity}%")

apply_button = tk.Button(root, text="Apply Detection Similarity", command=update_similarity)
apply_button.pack(pady=5)  # Add Apply button to GUI


save_csv_button = tk.Button(root, text="Save Report as CSV", command=save_report_as_csv)
save_csv_button.pack(pady=5)

save_pdf_button = tk.Button(root, text="Save Report as PDF", command=save_report_as_pdf)
save_pdf_button.pack(pady=5)

progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='indeterminate')
progress.pack(pady=10)  # Progress bar for visual feedback

root.mainloop()  # Start the Tkinter event loop

