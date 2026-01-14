import os
import glob
import subprocess
import pyperclip
import platform
import sys

# --- CONFIGURATION ---
FIGURES_DIR = 'figures'
# Absolute path for Inkscape app on macOS
INKSCAPE_APP_PATH = '/Applications/Inkscape.app'

def edit_figure():
    """
    Shows a list of existing figures, lets the user choose one,
    opens it in Inkscape, and copies its include code to the clipboard.
    """
    if not os.path.isdir(FIGURES_DIR):
        print(f"Error: Figures directory '{FIGURES_DIR}' not found.")
        return

    svg_files = sorted(glob.glob(os.path.join(FIGURES_DIR, '*.svg')))
    
    if not svg_files:
        print("No figures found to edit.")
        return

    print("\n--- Select a figure to edit ---")
    for i, f_path in enumerate(svg_files):
        print(f"  [{i+1}] {os.path.basename(f_path)}")
    print("-------------------------------")

    try:
        choice = int(input("Enter number: ")) - 1
        if not 0 <= choice < len(svg_files):
            raise ValueError
    except (ValueError, EOFError):
        print("Invalid choice. Aborting.")
        return

    selected_path = svg_files[choice]
    figure_basename = os.path.splitext(os.path.basename(selected_path))[0]
    
    include_code = f"\\incfig{{{figure_basename}}}"
    try:
        pyperclip.copy(include_code)
        print(f"\nCopied to clipboard: {include_code}")
    except pyperclip.PyperclipException:
        print("\nWarning: Could not copy to clipboard. `xclip` or `xsel` may be needed on Linux.")
        print(f"Your include code is: {include_code}")

    # Use a direct call to the Inkscape executable for maximum reliability on macOS
    print(f"Opening '{selected_path}' in Inkscape...")
    try:
        if platform.system() == "Darwin": # Darwin is the system name for macOS
            inkscape_executable = f"{INKSCAPE_APP_PATH}/Contents/MacOS/inkscape"
            subprocess.run([inkscape_executable, selected_path], check=True)
        else: # Fallback for other systems
            # This assumes 'inkscape' is in the system PATH on Linux/Windows
            subprocess.run(['inkscape', selected_path], check=True)

    except Exception as e:
        print(f"Error: Could not open Inkscape. Please check it is installed at '{INKSCAPE_APP_PATH}'.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)


if __name__ == "__main__":
    edit_figure()
