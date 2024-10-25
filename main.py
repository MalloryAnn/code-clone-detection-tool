import tkinter as tk
from tkinter import filedialog, messagebox
import difflib

# Define global variable for sensitivity
current_sensitivity = 9  # Default sensitivity


def calculate_similarity(code1, code2):
    stripped_code1 = [line.strip() for line in code1.splitlines() if line.strip() and not line.startswith('#')]
    stripped_code2 = [line.strip() for line in code2.splitlines() if line.strip() and not line.startswith('#')]

    return difflib.SequenceMatcher(None, stripped_code1, stripped_code2).ratio()


def detect_clones_with_sensitivity(codebase, sensitivity):
    clone_results = []
    lines = codebase.splitlines()

    # Adjust the similarity thresholds based on sensitivity (1-10 scale)
    type1_threshold = 1.0 * (sensitivity / 10)  # Type 1 clone
    type2_threshold = 0.9 * (sensitivity / 10)  # Type 2 clone
    type3_threshold = 0.7 * (sensitivity / 10)  # Type 3 clone

    for i, line1 in enumerate(lines):
        for j, line2 in enumerate(lines):
            if i != j:
                similarity = calculate_similarity(line1, line2)
                if similarity >= type1_threshold:
                    clone_results.append(f"Type 1 Clone detected at lines {i+1} and {j+1}")
                elif similarity >= type2_threshold:
                    clone_results.append(f"Type 2 Clone detected at lines {i+1} and {j+1}")
                elif similarity >= type3_threshold:
                    clone_results.append(f"Type 3 Clone detected at lines {i+1} and {j+1}")

    return clone_results


def open_file():
    try:
        # Open the file dialog to select a file
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=[("Python Files", "*.py"), ("Java Files", "*.java"), ("All Files", "*.*")]
        )

        if file_path:
            # Debug: Print file path to check if it's correct
            print(f"File selected: {file_path}")

            # Try opening and reading the file
            with open(file_path, "r", encoding="utf-8") as file:
                code = file.read()

                # Debug: Check if code is being read correctly
                print(f"Code read from file:\n{code[:100]}...")  # Print first 100 characters

                # Clear the text box and insert the code into it
                code_display.delete(1.0, tk.END)  # Clear any existing text in the box
                code_display.insert(tk.END, code)  # Insert the code into the text box

    except Exception as e:
        # Show error message box if something goes wrong
        messagebox.showerror("Error", f"Failed to open file: {str(e)}")
        print(f"Error occurred: {str(e)}")



def detect_clones():
    code = code_display.get("1.0", tk.END)  # Get the code from the display
    sensitivity = current_sensitivity  # Use the current sensitivity setting

    # Run clone detection with the sensitivity settings
    clone_results = detect_clones_with_sensitivity(code, sensitivity)

    # Display the results in the listbox
    results_listbox.delete(0, tk.END)  # Clear the listbox
    for result in clone_results:
        results_listbox.insert(tk.END, result)


def save_report():
    report_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if report_path:
        with open(report_path, 'w') as report_file:
            for result in results_listbox.get(0, tk.END):
                report_file.write(result + '\n')
        messagebox.showinfo("Save Report", f"Report saved successfully at {report_path}")


def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x200")

    tk.Label(settings_window, text="Detection Sensitivity").pack(pady=10)
    sensitivity_slider = tk.Scale(settings_window, from_=1, to=10, orient=tk.HORIZONTAL)
    sensitivity_slider.pack(pady=10)

    apply_button = tk.Button(settings_window, text="Apply", command=lambda: apply_settings(sensitivity_slider.get()))
    apply_button.pack(pady=10)


def apply_settings(sensitivity):
    global current_sensitivity
    current_sensitivity = sensitivity
    print(f"Sensitivity set to: {sensitivity}")



# Tkinter tings

# Create the main window
root = tk.Tk()
root.title("Code Clone Detection Tool")
root.geometry("800x600")  # Adjusted size


#  Text widget to display the code
code_display = tk.Text(root, wrap="none", height=10, width=80)
code_display.pack(padx=10, pady=10)

# Listbox to display the clone detection results
results_listbox = tk.Listbox(root, height=10, width=80)
results_listbox.pack(padx=10, pady=10)

# Add buttons for opening codebase/running detection
open_button = tk.Button(root, text="Open Codebase", command=open_file)
open_button.pack(pady=5)

run_button = tk.Button(root, text="Run Clone Detection", command=detect_clones)
run_button.pack(pady=5)


# Settings button for sensitivity
settings_button = tk.Button(root, text="Settings", command=open_settings)
settings_button.pack(pady=5)

# Button to save the clone detection report
save_button = tk.Button(root, text="Save Report", command=save_report)
save_button.pack(pady=5)


# Start Tkinter loop
root.mainloop()
