import tkinter as tk
from tkinter import filedialog, messagebox

# Building blocks of main window
root = tk.Tk()
root.title("Code Clone Detection Tool")
root.geometry("800x9000")  # Size of the window

# Menu bar
menu_bar = tk.Menu(root)

# File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open Codebase", command=lambda: open_file())
menu_bar.add_cascade(label="File", menu=file_menu)

# Help menu for profesh reasons
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Help", command=lambda: show_help())
menu_bar.add_cascade(label="Help", menu=help_menu)

# Attach menu bar to the window
root.config(menu=menu_bar)

# Create a Text Widget to show the code
code_display = tk.Text(root, wrap="none", height=20, width=80)
code_display.pack(padx=10, pady=10)

# Function to open file dialog and show selected file
def open_file():
    file_path = filedialog.askopenfilename(
        title="Select a File",
        filetypes=[("Python Files", "*.py"), ("Java Files", "*.java"), ("All Files", "*.*")]
    )
    if file_path:
        with open(file_path, "r") as file:
            code = file.read()
            code_display.delete(1.0, tk.END)  # Clear existing content in the box
            code_display.insert(tk.END, code)  # Insert new code

# Add button to run clone detection
run_button = tk.Button(root, text="Run Clone Detection", command=lambda: detect_clones())
run_button.pack(pady=10)

# Create a Listbox to show the all clone results
results_label = tk.Label(root, text="Clone Detection Results:")
results_label.pack()

results_listbox = tk.Listbox(root, height=80, width=100)
results_listbox.pack(padx=10, pady=10)

# Placeholder for clone detection code
def detect_clones():
    # Replace with actual detection logic laters when we are further along
    results_listbox.delete(0, tk.END)  # Clear the listbox
    results_listbox.insert(tk.END, "Type 1 Clone detected at line 23 in File1.py")
    results_listbox.insert(tk.END, "Type 2 Clone detected at line 45 in File2.java")
    messagebox.showinfo("Clone Detection", "Clone detection complete!")

# Help function
def show_help():
    messagebox.showinfo("Help", "This tool helps you detect code clones in Python and Java files. Use 'Open Codebase' to select your file and 'Run Clone Detection' to identify potential clones.")

# Function to open Settings window
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
    print(f"Sensitivity set to: {sensitivity}")

# Settings button
settings_button = tk.Button(root, text="Settings", command=open_settings)
settings_button.pack(pady=10)

# Run the Tkinter loop
root.mainloop()
