import sys
import os
import re
import shutil
import subprocess
import platform

# --- CONFIGURATION ---
FIGURES_DIR_NAME = 'figures' # Renamed to avoid confusion with path variable

# Get the directory where THIS SCRIPT resides.
# If script is in '.../orf309_independent_notes/scripts/', this is '.../scripts/'
SCRIPT_LOCATION = os.path.dirname(os.path.abspath(__file__))

# The project root (where master.tex, preamble.tex, and figures/ directory are)
# is one level up from the 'scripts/' directory.
PROJECT_ROOT_DIR = os.path.dirname(SCRIPT_LOCATION)

# Correct path to the FIGURES directory, relative to the project root
FIGURES_PATH_FULL = os.path.join(PROJECT_ROOT_DIR, FIGURES_DIR_NAME)

# Correct path to the TEMPLATE file
TEMPLATE_PATH_FULL = os.path.join(FIGURES_PATH_FULL, 'figure_template.svg')

# Absolute path for Inkscape app on macOS
INKSCAPE_APP_PATH = '/Applications/Inkscape.app'


def slugify(text):
    """Converts a string to a filename-safe slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text

def create_figure(title):
    """
    Creates a new figure from a template if it doesn't exist,
    opens it in Inkscape, and prints the LaTeX include code.
    """
    if not title:
        print("Error: No title provided.", file=sys.stderr)
        sys.exit(1)

    # Ensure the correct FIGURES_PATH_FULL exists
    os.makedirs(FIGURES_PATH_FULL, exist_ok=True)
    
    slug = slugify(title)
    figure_basename = slug
    
    # New figure SVG path within the correct FIGURES_PATH_FULL
    figure_svg_path = os.path.join(FIGURES_PATH_FULL, f"{figure_basename}.svg")

    if os.path.exists(figure_svg_path):
        print(f"Figure '{figure_svg_path}' already exists. Opening it.", file=sys.stderr)
    else:
        # Check for the template at its correct full path
        if not os.path.exists(TEMPLATE_PATH_FULL):
            print(f"Error: Template file not found at '{TEMPLATE_PATH_FULL}'", file=sys.stderr)
            sys.exit(1)
        shutil.copy(TEMPLATE_PATH_FULL, figure_svg_path) # Use full template path here
        print(f"Created new figure '{figure_svg_path}'.", file=sys.stderr)

    # --- Start of the fix for Inkscape opening on macOS ---
    try:
        if platform.system() == "Darwin": # macOS
            inkscape_executable = os.path.join(INKSCAPE_APP_PATH, "Contents", "MacOS", "inkscape")
            subprocess.run([inkscape_executable, figure_svg_path], check=True)
        else: # Fallback for other systems like Linux/Windows
            # Assuming 'inkscape' is in the system PATH or provided a direct path
            subprocess.run(['inkscape', figure_svg_path], check=True)
            
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"Error: Could not open Inkscape. Please check it is installed at '{INKSCAPE_APP_PATH}' and is accessible.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    # --- End of the fix ---
    
    # Print the LaTeX include code. The path is relative to the master.tex file.
    # So it should be just 'figures/<basename>.pdf_tex'
    print(f"\\incfig{{{figure_basename}}}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_figure(sys.argv[1])
    else:
        print("Usage: python create_figure.py \"My Figure Title\"", file=sys.stderr)