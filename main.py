import tkinter as tk  # Import Tkinter for GUI
from tkinter import filedialog, messagebox  # For file dialogs and message boxes
import difflib  # For similarity comparison

# Define global variable for sensitivity (used to control detection thresholds)
current_sensitivity = 9  # Default sensitivity


def calculate_similarity(code1, code2):
    """
    Calculate the similarity ratio between two pieces of code.

    Args:
        code1 (str): The first code snippet.
        code2 (str): The second code snippet.

    Returns:
        float: A similarity ratio between 0 and 1.
    """
    # Strip whitespace and ignore commented lines
    stripped_code1 = [line.strip() for line in code1.splitlines() if line.strip() and not line.startswith('#')]
    stripped_code2 = [line.strip() for line in code2.splitlines() if line.strip() and not line.startswith('#')]

    # Use SequenceMatcher to calculate similarity ratio
    return difflib.SequenceMatcher(None, stripped_code1, stripped_code2).ratio()


def detect_clones_with_sensitivity(codebase, sensitivity):
    """
    Detect code clones within the provided codebase based on sensitivity settings.

    Args:
        codebase (str): The code content to analyze.
        sensitivity (int): Sensitivity level (1-10) that controls detection thresholds.

    Returns:
        list: A list of detected clone results.
    """
    clone_results = []  # Store clone detection results
    lines = codebase.splitlines()  # Split codebase into lines

    # Define similarity thresholds based on the sensitivity setting
    type1_threshold = 1.0 * (sensitivity / 10)  # Type 1 clone: Exact match
    type2_threshold = 0.9 * (sensitivity / 10)  # Type 2 clone: Slightly modified
    type3_threshold = 0.7 * (sensitivity / 10)  # Type 3 clone: Moderately modified

    # Compare every line with every other line in the codebase
    for i, line1 in enumerate(lines):
        for j, line2 in enumerate(lines):
            if i != j:  # Skip comparison with the same line
                similarity = calculate_similarity(line1, line2)
                # Check similarity against the thresholds
                if similarity >= type1_threshold:
                    clone_results.append(f"Type 1 Clone detected at lines {i + 1} and {j + 1}")
                elif similarity >= type2_threshold:
                    clone_results.append(f"Type 2 Clone detected at lines {i + 1} and {j + 1}")
                elif similarity >= type3_threshold:
                    clone_results.append(f"Type 3 Clone detected at lines {i + 1} and {j + 1}")

    return clone_results


def open_file():
    """
    Open a file dialog to select and load a codebase into the text display widget.
    """
    try:
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=[("Python Files", "*.py"), ("Java Files", "*.java"), ("All Files", "*.*")]
        )
        if file_path:
            print(f"File selected: {file_path}")  # Debug: Print selected file path

            # Read the contents of the selected file
            with open(file_path, "r", encoding="utf-8") as file:
                code = file.read()
                print(f"Code read from file:\n{code[:100]}...")  # Debug: Preview code

                # Display the code in the text widget
                code_display.delete(1.0, tk.END)  # Clear existing content
                code_display.insert(tk.END, code)  # Insert new content

    except Exception as e:
        # Show an error message if something goes wrong
        messagebox.showerror("Error", f"Failed to open file: {str(e)}")
        print(f"Error occurred: {str(e)}")


def detect_clones():
    """
    Retrieve the code from the text display widget and run clone detection.
    Display the results in the listbox.
    """
    code = code_display.get("1.0", tk.END)  # Get the displayed code
    sensitivity = current_sensitivity  # Use the current sensitivity setting

    # Perform clone detection and get the results
    clone_results = detect_clones_with_sensitivity(code, sensitivity)

    # Display the clone detection results in the listbox
    results_listbox.delete(0, tk.END)  # Clear existing results
    for result in clone_results:
        results_listbox.insert(tk.END, result)  # Add each result to the listbox


def save_report():
    """
    Save the clone detection results to a text file.
    """
    report_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if report_path:
        with open(report_path, 'w') as report_file:
            for result in results_listbox.get(0, tk.END):
                report_file.write(result + '\n')
        messagebox.showinfo("Save Report", f"Report saved successfully at {report_path}")


def open_settings():
    """
    Open a new window to adjust the detection sensitivity using a slider.
    """
    settings_window = tk.Toplevel(root)  # Create a new top-level window
    settings_window.title("Settings")
    settings_window.geometry("300x200")

    # Add label and slider for sensitivity adjustment
    tk.Label(settings_window, text="Detection Sensitivity").pack(pady=10)
    sensitivity_slider = tk.Scale(settings_window, from_=1, to=10, orient=tk.HORIZONTAL)
    sensitivity_slider.pack(pady=10)

    # Apply button to save the selected sensitivity
    apply_button = tk.Button(settings_window, text="Apply", command=lambda: apply_settings(sensitivity_slider.get()))
    apply_button.pack(pady=10)


def apply_settings(sensitivity):
    """
    Apply the selected sensitivity value and print it for debugging.

    Args:
        sensitivity (int): The new sensitivity value (1-10).
    """
    global current_sensitivity  # Modify the global sensitivity variable
    current_sensitivity = sensitivity
    print(f"Sensitivity set to: {sensitivity}")


# Tkinter GUI Setup

# Create the main window
root = tk.Tk()
root.title("Code Clone Detection Tool")
root.geometry("800x600")  # Set the size of the main window

# Text widget to display the code
code_display = tk.Text(root, wrap="none", height=10, width=80)
code_display.pack(padx=10, pady=10)

# Listbox to display clone detection results
results_listbox = tk.Listbox(root, height=10, width=80)
results_listbox.pack(padx=10, pady=10)

# Button to open a codebase
open_button = tk.Button(root, text="Open Codebase", command=open_file)
open_button.pack(pady=5)

# Button to run clone detection
run_button = tk.Button(root, text="Run Clone Detection", command=detect_clones)
run_button.pack(pady=5)

# Button to open settings for sensitivity adjustment
settings_button = tk.Button(root, text="Settings", command=open_settings)
settings_button.pack(pady=5)

# Button to save the clone detection report
save_button = tk.Button(root, text="Save Report", command=save_report)
save_button.pack(pady=5)

# Start the Tkinter event loop
root.mainloop()
