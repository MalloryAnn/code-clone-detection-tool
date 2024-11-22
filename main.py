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

marked_clones = []  # Global list to store clones marked for refactoring


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
    cleaned_code1 = clean_code(code1)
    cleaned_code2 = clean_code(code2)

    if not cleaned_code1.strip() or not cleaned_code2.strip():
        print(
            f"Debug: Skipped comparison due to empty code after cleaning:\nCode1: {cleaned_code1}\nCode2: {cleaned_code2}")
        return 0.0  # Skip empty comparisons

    # Debugging output to verify cleaned code and similarity
    print(f"Debug: Comparing cleaned code:\n{cleaned_code1}\n---VS---\n{cleaned_code2}")
    similarity = difflib.SequenceMatcher(None, cleaned_code1, cleaned_code2).ratio()
    print(f"Debug: Similarity = {similarity:.2%}")

    return similarity


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


def view_marked_clones():
    """
    Opens a window displaying all clones marked for refactoring.
    """
    if not marked_clones:
        messagebox.showinfo("No Marked Clones", "No clones have been marked for refactoring.")
        return

    # Create a new window to display marked clones
    marked_window = tk.Toplevel(root)
    marked_window.title("Marked Clones for Refactoring")
    marked_window.geometry("600x400")

    # Add a title
    tk.Label(marked_window, text="Marked Clones for Refactoring", font=("Arial", 14, "bold")).pack(pady=5)

    # Add a listbox to display marked clones
    marked_listbox = tk.Listbox(marked_window, width=80, height=20)
    marked_listbox.pack(padx=10, pady=10)

    # Populate the listbox with marked clones
    for i, clone in enumerate(marked_clones, start=1):
        marked_listbox.insert(tk.END, f"{i}. Clone Type: {clone['type']}, File: {clone['file']}, "
                                      f"Lines: {clone['lines']}, Similarity: {clone['similarity']}")

    # Add a close button
    close_button = tk.Button(marked_window, text="Close", command=marked_window.destroy)
    close_button.pack(pady=5)


def save_marked_clones():
    """
    Saves the marked clones for refactoring to a CSV file.
    """
    if not marked_clones:
        messagebox.showinfo("No Marked Clones", "No clones have been marked for refactoring.")
        return

    # Open a file dialog to select the save location
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not save_path:
        return  # User canceled the save dialog

    try:
        # Write the marked clones to a CSV file
        with open(save_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Clone Type", "File", "Line Range", "Similarity"])
            for clone in marked_clones:
                # Add quotes around the line range to avoid Excel interpreting it as a date
                line_range = f'"{clone["lines"]}"'  # Force text format
                writer.writerow([clone["type"], clone["file"], line_range, clone["similarity"]])
        messagebox.showinfo("Success", f"Marked clones saved to {save_path}.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save marked clones: {e}")


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
    global clone_results
    clone_results.clear()  # Clear previous results
    similarity_threshold = similarity_slider.get() / 100  # Convert slider value to decimal

    for file_name, lines in code_files:
        for i, line1 in enumerate(lines):
            for j, line2 in enumerate(lines):
                if i >= j:
                    continue

                similarity = calculate_similarity(line1, line2)
                if similarity >= similarity_threshold:
                    classify_clone(file_name, i, j, similarity)


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
    Classifies a clone based on similarity.

    Parameters:
        file_name (str): Name of the file where the clone was detected.
        line1 (int): First line number of the clone.
        line2 (int): Second line number of the clone.
        similarity (float): Calculated similarity between the two code lines.
    """
    global total_exact_clones, total_renamed_clones, total_modified_clones

    # Avoid duplicate or reversed comparisons
    if line1 >= line2:
        print(f"Debug: Skipping redundant comparison between lines {line1 + 1} and {line2 + 1}")
        return

    # Type 1 clones: Exact matches
    # Relax the condition for Type 1 clones to allow minor floating-point differences
    if 0.99 <= similarity <= 1.0:  # Type 1 clones: Near-exact matches treated as exact
        print(f"Debug: Classifying Type 1 clone between lines {line1 + 1} and {line2 + 1} in {file_name}")
        clone_results.append(("Type 1", line1 + 1, line2 + 1, f"{similarity:.2%}", file_name))
        total_exact_clones += 1

    # Type 2 clones: Renamed
    elif 0.8 <= similarity < 1.0:
        print(f"Debug: Classifying Type 2 clone with similarity {similarity:.2%}")
        clone_results.append(("Type 2", line1 + 1, line2 + 1, f"{similarity:.2%}", file_name))
        total_renamed_clones += 1
    # Type 3 clones: Modified
    elif 0.7 <= similarity < 0.8:
        print(f"Debug: Classifying Type 3 clone with similarity {similarity:.2%}")
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
    root.update_idletasks()  # Refresh the GUI after action


def load_clone_for_editing():
    """
    Loads the selected clone from the results list into the editor for modification.
    Ensures the file exists and prompts the user to locate missing files.
    """
    selected_index = results_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("No Selection", "Please select a clone from the list.")
        return

    selected_clone = results_listbox.get(selected_index[0])
    try:
        clone_type, line1, line2, similarity, file_name = eval(selected_clone)

        # Check if the file exists
        if not os.path.exists(file_name):
            # Prompt the user to locate the missing file
            file_name = filedialog.askopenfilename(
                title=f"Locate Missing File: {file_name}",
                filetypes=[("Python Files", "*.py"), ("Java Files", "*.java")]
            )
            if not file_name:
                messagebox.showwarning("File Missing", "The file could not be found or opened.")
                return

        # Load the corresponding code snippet into the editor
        with open(file_name, "r") as file:
            lines = file.readlines()

        # Validate line numbers
        if line1 < 1 or line2 > len(lines):
            raise IndexError(f"Line numbers out of range. File has {len(lines)} lines.")

        # Extract clone lines
        clone_code = "".join(lines[int(line1) - 1:int(line2)])
        clone_editor.delete(1.0, tk.END)  # Clear the editor
        clone_editor.insert(tk.END, clone_code)  # Insert clone code into the editor

    except FileNotFoundError as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"File not found. Please check the file path.")
    except IndexError as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Invalid line numbers: {line1}-{line2}. Please check the clone details.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        messagebox.showerror("Error", "Failed to load the selected clone. Please check the file and clone details.")

def view_clone_details():
    """
    Opens a detailed view window for the selected clone, including refactoring suggestions.
    """
    # Get the selected item from the results listbox
    selected_index = results_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("No Selection", "Please select a clone from the list.")
        return

    # Parse the selected result
    selected_clone = results_listbox.get(selected_index[0])
    print(f"Debug: Raw selected item: {selected_clone}")

    try:
        # Adjust parsing logic to handle actual format
        clone_type, line1, line2, similarity, file_name = eval(selected_clone)

        # Create a new window for clone details
        details_window = tk.Toplevel(root)
        details_window.title("Clone Details")
        details_window.geometry("500x400")

        # Display clone details
        tk.Label(details_window, text="Clone Details", font=("Arial", 14, "bold")).pack(pady=5)
        details_text = (
            f"Clone Type: {clone_type}\n"
            f"File: {file_name}\n"
            f"Line Range: {line1} - {line2}\n"
            f"Similarity: {similarity}\n"
        )
        tk.Label(details_window, text=details_text, justify="left").pack(pady=5)

        # Add refactoring suggestions
        tk.Label(details_window, text="Refactoring Suggestions", font=("Arial", 12, "bold")).pack(pady=5)
        if clone_type == "Type 1":
            suggestion = "Remove exact duplicates by refactoring or consolidating repeated code."
        elif clone_type == "Type 2":
            suggestion = "Rename variables and parameters to avoid redundancy."
        elif clone_type == "Type 3":
            suggestion = "Refactor similar logic into reusable functions or classes."
        else:
            suggestion = "No specific suggestion available."
        tk.Label(details_window, text=suggestion, wraplength=400, justify="left").pack(pady=5)

        # Add a "Mark for Refactoring" button
        def mark_for_refactoring():
            """
            Marks the selected clone for refactoring and stores it in the global list.
            """
            global marked_clones

            # Create a dictionary of the clone details
            marked_clone = {
                "type": clone_type,
                "file": file_name,
                "lines": f"{line1} - {line2}",
                "similarity": similarity
            }

            # Add the marked clone to the global list
            marked_clones.append(marked_clone)

            # Display confirmation to the user
            messagebox.showinfo("Marked", f"Clone marked for refactoring:\n\n{details_text}")
            print(f"Debug: Marked clone added: {marked_clone}")  # Debugging output

        mark_button = tk.Button(details_window, text="Mark for Refactoring", command=mark_for_refactoring)
        mark_button.pack(pady=10)

    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", "Failed to load clone details. Please check the selected item.")



def save_modified_code():
    """
    Saves the modified code back to the file and updates the clone detection results.
    """
    # Get the selected item from the results listbox
    selected_index = results_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("No Selection", "Please select a clone from the list.")
        return

    # Parse the selected result
    selected_clone = results_listbox.get(selected_index[0])
    clone_type, line1, line2, similarity, file_name = eval(selected_clone)

    # Get the modified code from the editor
    modified_code = clone_editor.get(1.0, tk.END).strip()

    # Replace the corresponding lines in the file
    with open(file_name, "r") as file:
        lines = file.readlines()

    # Update the file with the modified code
    lines[line1 - 1:line2] = [modified_code + "\n"]  # Replace the lines
    with open(file_name, "w") as file:
        file.writelines(lines)

    # Show a confirmation message
    messagebox.showinfo("Save Changes", f"Changes saved to {file_name}. Re-running clone detection...")

    # Re-run clone detection
    run_clone_detection_in_thread()


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


def apply_filters():
    """
    Filters clone detection results based on the selected clone type and similarity threshold.
    """
    filtered_results = []  # List to store filtered results
    similarity_threshold = similarity_slider.get()  # Get the slider's current value

    for clone_type, line1, line2, similarity, file_name in clone_results:
        # Filter by clone type
        if selected_clone_type.get() != "All" and clone_type != selected_clone_type.get():
            continue  # Skip if the clone type doesn't match the selected type

        # Filter by similarity threshold
        if float(similarity.strip('%')) < similarity_threshold:
            continue  # Skip if similarity is below the threshold

        # Add result to filtered list
        filtered_results.append((clone_type, line1, line2, similarity, file_name))

    # Display the filtered results
    results_listbox.delete(0, tk.END)  # Clear the listbox
    for result in filtered_results:
        results_listbox.insert(tk.END, f"{result}")



def add_filters_to_gui():
    """
    Adds GUI components for filtering results.
    """
    # Clone Type Filter
    tk.Label(root, text="Filter by Clone Type").pack(pady=5)
    clone_type_menu = ttk.Combobox(root, textvariable=selected_clone_type)
    clone_type_menu['values'] = ["All", "Type 1", "Type 2", "Type 3"]
    clone_type_menu.pack(pady=5)

    # Similarity Threshold Filter
    tk.Label(root, text="Minimum Similarity Threshold (%)").pack(pady=5)
    similarity_threshold_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL,
                                           variable=similarity_threshold_filter)
    similarity_threshold_slider.pack(pady=5)

    # Apply Filters Button
    apply_filters_button = tk.Button(root, text="Apply Filters", command=apply_filters)
    apply_filters_button.pack(pady=10)


def display_clone_results():
    """
    Displays filtered clone detection results in the GUI's listbox based on the selected clone type.
    """
    results_listbox.delete(0, tk.END)  # Clear previous results
    selected_type = selected_clone_type.get()  # Get selected clone type from dropdown

    for result in clone_results:
        clone_type, line1, line2, similarity, file_name = result
        if selected_type == "All" or clone_type == selected_type:  # Match selected type or show all
            results_listbox.insert(tk.END, f"{result}")  # Insert matching result into the listbox


def save_report_as_csv():
    """
    Saves the detection results as a CSV file, including clone metrics and recommendations.
    """
    report_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if report_path:
        with open(report_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write header row with Recommendations
            writer.writerow(["Clone Type", "Line 1", "Line 2", "Similarity", "File Path", "Recommendations"])  # Updated header

            # Generate and write recommendations for each clone
            for clone in clone_results:
                clone_type, line1, line2, similarity, file_name = clone
                # Use the absolute file path to avoid issues when reopening the report
                full_path = os.path.abspath(file_name)

                # Generate recommendations
                if clone_type == "Type 1":
                    recommendation = f"Consider removing exact duplicates in {full_path} at lines {line1} and {line2}."
                elif clone_type == "Type 2":
                    recommendation = f"Rename variables in {full_path} to avoid redundancy at lines {line1} and {line2}."
                elif clone_type == "Type 3":
                    recommendation = f"Consolidate similar code in {full_path} found at lines {line1} and {line2}."
                else:
                    recommendation = "No recommendation available."

                # Write clone result with recommendation
                writer.writerow([clone_type, line1, line2, similarity, full_path, recommendation])  # Save full file path

            # Add metrics section
            writer.writerow([])  # Add empty row for separation
            writer.writerow(["Metrics"])  # Metrics header
            writer.writerow(["Total Exact Clones", total_exact_clones])  # Total exact clones
            writer.writerow(["Total Renamed Clones", total_renamed_clones])  # Total renamed clones
            writer.writerow(["Total Modified Clones", total_modified_clones])  # Total modified clones

        # Confirmation message after saving
        messagebox.showinfo("Save Report", f"Report saved successfully at {report_path}")


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

def open_clone_report():
    """
    Opens a previously saved clone detection report (CSV file) and displays its content in the results listbox.
    """
    # Open a file dialog to select the report file
    report_path = filedialog.askopenfilename(
        title="Select Clone Report",
        filetypes=[("CSV files", "*.csv")]
    )

    if not report_path:  # Check if a file was selected
        messagebox.showwarning("No File Selected", "Please select a clone report file.")
        return

    try:
        # Read the report file
        with open(report_path, "r", newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row

            # Clear existing results and load the new ones
            results_listbox.delete(0, tk.END)  # Clear the listbox
            for row in reader:
                # Ensure the row has the expected structure
                if len(row) >= 5:  # Expected structure: Clone Type, Line 1, Line 2, Similarity, File
                    clone_type, line1, line2, similarity, file_name = row[:5]

                    # Format the row into a tuple-like string that matches the expected format
                    formatted_result = f"('{clone_type}', {line1}, {line2}, '{similarity}', '{file_name}')"
                    results_listbox.insert(tk.END, formatted_result)

        # Confirmation message
        messagebox.showinfo("Success", "Clone report loaded successfully.")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", "Failed to load the clone report. Please check the file format and try again.")

def open_instructions():
    """
    Opens a window displaying instructions for using the Code Clone Detection Tool.
    """
    instructions_window = tk.Toplevel(root)
    instructions_window.title("Instructions")
    instructions_window.geometry("700x700")

    # Create a Text widget to display instructions
    text_widget = tk.Text(instructions_window, wrap="word", height=40, width=70)
    text_widget.pack(padx=10, pady=10)

    # Insert instructions into the Text widget with formatting
    text_widget.insert(tk.END, "Welcome to the Code Clone Detection Tool!\n\n", "bold")
    text_widget.insert(tk.END, "This tool helps you detect, analyze, and refactor code clones in Python or Java files. Follow these steps to navigate and utilize the features effectively:\n\n")

    text_widget.insert(tk.END, "Step 1: Set Similarity Threshold\n", "bold")
    text_widget.insert(tk.END, "1. Adjust Similarity Slider: Use the Detection Similarity Scale slider at the bottom of the GUI. Set the threshold (e.g., 100% for exact matches, 70% for broader matches).\n")
    text_widget.insert(tk.END, "2. Click Apply Detection Similarity to confirm your setting.\n\n")

    text_widget.insert(tk.END, "Step 2: Load Your Code Files\n", "bold")
    text_widget.insert(tk.END, "1. Click Open Code File to load your Python or Java files.\n")
    text_widget.insert(tk.END, "2. Select one or more files from your system. The files will be displayed in the Code Display section.\n\n")

    text_widget.insert(tk.END, "Step 3: Run Clone Detection\n", "bold")
    text_widget.insert(tk.END, "1. Click Run Clone Detection to analyze the loaded files for code clones.\n")
    text_widget.insert(tk.END, "2. Detected clones will be listed in the Detection Results section, showing Clone Type, Line Range, Similarity, and File Path.\n\n")

    text_widget.insert(tk.END, "Step 4: Review Clones\n", "bold")
    text_widget.insert(tk.END, "1. Use Filter Results by Clone Type to view specific clone types or all results.\n")
    text_widget.insert(tk.END, "2. Select a clone and click View Clone Details to see detailed information and refactoring suggestions.\n\n")

    text_widget.insert(tk.END, "Step 5: Mark Clones for Refactoring\n", "bold")
    text_widget.insert(tk.END, "1. In the Clone Details window, click Mark for Refactoring to tag the clone.\n")
    text_widget.insert(tk.END, "2. Save Marked Clones: Click Save Marked Clones to save the marked clones to a CSV file.\n\n")

    text_widget.insert(tk.END, "Step 6: Edit and Refactor Clones\n", "bold")
    text_widget.insert(tk.END, "1. Select a clone and click Load Clone for Editing.\n")
    text_widget.insert(tk.END, "2. Modify the code in the editor.\n")
    text_widget.insert(tk.END, "3. Click Save Changes to save the modifications and rerun clone detection.\n\n")

    text_widget.insert(tk.END, "Step 7: Open Previously Saved Reports\n", "bold")
    text_widget.insert(tk.END, "1. Click Open Previously Saved Report to load a CSV report.\n")
    text_widget.insert(tk.END, "2. Review the clones from the report in the Detection Results section.\n\n")

    text_widget.insert(tk.END, "Step 8: Save Clone Reports\n", "bold")
    text_widget.insert(tk.END, "1. Click Save Report as CSV or Save Report as PDF to export clone detection results.\n\n")

    text_widget.insert(tk.END, "Tips for Best Results\n", "bold")
    text_widget.insert(tk.END, "- Ensure files are accessible and properly formatted.\n")
    text_widget.insert(tk.END, "- Use refactoring suggestions to improve code quality.\n")
    text_widget.insert(tk.END, "- Mark clones for refactoring to track necessary changes.\n\n")

    text_widget.insert(tk.END, "Clone Types Explained\n", "bold")
    text_widget.insert(tk.END, "- Type 1: Exact clones (100% similarity).\n")
    text_widget.insert(tk.END, "- Type 2: Renamed clones (90%-99% similarity).\n")
    text_widget.insert(tk.END, "- Type 3: Modified clones (70%-89% similarity).\n\n")

    text_widget.insert(tk.END, "Happy Coding!\n", "bold")

    # Add bold formatting
    text_widget.tag_configure("bold", font=("Arial", 10, "bold"))
    text_widget.config(state="disabled")  # Make the text read-only

    # Add a Close button
    close_button = tk.Button(instructions_window, text="Close", command=instructions_window.destroy)
    close_button.pack(pady=10)


def handle_button_action(action):
    """
    Handles button actions and ensures proper focus and event triggering.
    """
    try:
        action()  # Call the button's associated function
    except Exception as e:
        print(f"Error executing action: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

# Tkinter GUI Setup
root = tk.Tk()

# Add the Instructions button to the main GUI
instructions_button = tk.Button(root, text="Instructions", command=open_instructions)
instructions_button.pack(pady=5)
# Filter variables for GUI
selected_clone_type = tk.StringVar(value="All")  # Default to "All"
similarity_threshold_filter = tk.DoubleVar(value=0.0)  # Default to 0.0%

root.title("Code Clone Detection Tool")
root.geometry("900x990")
# Text area to display code
code_display = tk.Text(root, wrap="none", height=10, width=100)
code_display.pack(padx=10, pady=10)

# Listbox to display detection results
results_listbox = tk.Listbox(root, height=8, width=100)
results_listbox.pack(padx=10, pady=10)

# Text area to display and edit selected clone
tk.Label(root, text="Edit Selected Clone").pack(pady=5)
clone_editor = tk.Text(root, height=10, width=100)
clone_editor.pack(pady=5)

# Buttons for editing actions
button_frame = tk.Frame(root)  # Create a frame to organize buttons
button_frame.pack(pady=10)

load_clone_button = tk.Button(button_frame, text="Load Clone for Editing", command=load_clone_for_editing)
load_clone_button.grid(row=0, column=0, padx=5, pady=5)

view_details_button = tk.Button(button_frame, text="View Clone Details", command=view_clone_details)
view_details_button.grid(row=0, column=1, padx=5, pady=5)

open_saved_button = tk.Button(button_frame, text="Open Previously Saved Report", command=open_clone_report)
open_saved_button.grid(row=0, column=2, padx=5, pady=5)

save_changes_button = tk.Button(button_frame, text="Save Changes", command=save_modified_code)
save_changes_button.grid(row=0, column=3, padx=5, pady=5)

# Dropdown for filtering by clone type
selected_clone_type = tk.StringVar(value="All")  # Default to "All"
tk.Label(root, text="Filter Results by Clone Type").pack(pady=5)  # Label for dropdown
type_filter = tk.OptionMenu(root, selected_clone_type, "All", "Type 1", "Type 2", "Type 3",
                            command=lambda _: display_clone_results())
type_filter.pack(pady=5)

# Buttons for various actions
open_button = tk.Button(root, text="Open Code File", command=open_code_files)
open_button.pack(pady=5)

run_button = tk.Button(root, text="Run Clone Detection", command=run_clone_detection_in_thread)
run_button.pack(pady=5)

# Add similarity slider directly to the main GUI
tk.Label(root, text="Detection Similarity Scale: Select BEFORE running the clone detection").pack(pady=10)  # Clearer label for slider

similarity_slider = tk.Scale(
    root,
    from_=10,  # Minimum similarity
    to=100,  # Maximum similarity
    orient=tk.HORIZONTAL,
    resolution=10,  # Slider steps in increments of 10
    command=lambda _: apply_filters()  # Call apply_filters whenever the slider is adjusted
)
similarity_slider.set(70)  # Default to 70% similarity
similarity_slider.pack(pady=10)  # Add slider to GUI



# Add the View Marked Clones button
view_marked_button = tk.Button(root, text="View Marked Clones", command=view_marked_clones)
view_marked_button.pack(pady=5)

save_marked_button = tk.Button(root, text="Save Marked Clones", command=save_marked_clones)
save_marked_button.pack(pady=5)


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

# Start the Tkinter event loop
root.mainloop()
