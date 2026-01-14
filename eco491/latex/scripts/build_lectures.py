import os
import glob
import subprocess
import re
from datetime import datetime

# --- Configuration ---
MASTER_FILE = "master.tex"
PREAMBLE_FILE = "preamble.tex"
LECTURE_DIR = "./" 
TEMP_MASTER_FILE = "temp_master.tex"
LECTURE_FILE_PREFIX = "PREFIX OF COURSE NOTES" 
NUM_RECENT_TO_COMPILE = 2 # This variable controls how many recent files to compile

# Markers in the master file
LECTURE_INCLUDES_START_MARKER = "SCRIPT_LECTURE_INCLUDES_START"
LECTURE_INCLUDES_END_MARKER = "SCRIPT_LECTURE_INCLUDES_END"

# --- Helper Functions ---

def get_lecture_files(directory, prefix, recent_count=None):
    """
    Finds .tex files matching the prefix.
    If recent_count is specified, returns the 'recent_count' most recently modified files.
    Otherwise, returns all files sorted alphabetically.
    Returns a list of base names (without .tex).
    """
    lecture_files = []
    for filepath in glob.glob(os.path.join(directory, f"{prefix}*.tex")):
        filename = os.path.basename(filepath)
        mod_time = os.path.getmtime(filepath)
        lecture_files.append((mod_time, os.path.splitext(filename)[0]))

    if recent_count:
        # Sort by modification time to get the most recent
        lecture_files.sort(key=lambda x: x[0], reverse=True)
        return [f[1] for f in lecture_files[:recent_count]]
    else:
        # Sort by name for consistent order in the master document
        lecture_files.sort(key=lambda x: x[1])
        return [f[1] for f in lecture_files]

def update_master_file_inputs(master_filepath, all_lectures_basenames):
    """
    Updates the master file to ensure all lecture files are included via \input
    between the START and END markers. This keeps your master file up-to-date.
    """
    try:
        with open(master_filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start_index, end_index = -1, -1
        for i, line in enumerate(lines):
            if LECTURE_INCLUDES_START_MARKER in line:
                start_index = i
            elif LECTURE_INCLUDES_END_MARKER in line:
                end_index = i
        
        if start_index == -1 or end_index == -1:
            print("Error: Could not find lecture include markers in master file.")
            return

        new_include_block = [lines[start_index]]
        for basename in all_lectures_basenames:
            new_include_block.append(f"\\input{{{basename}}}\n")
        new_include_block.append(lines[end_index])

        updated_lines = lines[:start_index] + new_include_block + lines[end_index+1:]
        
        with open(master_filepath, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        print(f"Updated '{master_filepath}' with all lecture \\input commands.")

    except Exception as e:
        print(f"Error updating master file: {e}")
        exit(1)


def compile_latex_selectively():
    """
    Handles finding all files, updating the master list, then creating a 
    temporary master file where older files are commented out, and finally compiles it.
    """
    all_lectures = get_lecture_files(LECTURE_DIR, LECTURE_FILE_PREFIX)
    if not all_lectures:
        print("No lecture files found. Nothing to compile.")
        return
    update_master_file_inputs(MASTER_FILE, all_lectures)

    # This is where the script gets the 2 most recent files
    recent_lectures_to_compile = get_lecture_files(LECTURE_DIR, LECTURE_FILE_PREFIX, recent_count=NUM_RECENT_TO_COMPILE)
    print(f"\nWill compile only the most recent {NUM_RECENT_TO_COMPILE} files: {recent_lectures_to_compile}")

    try:
        with open(MASTER_FILE, 'r', encoding='utf-8') as f_in, \
             open(TEMP_MASTER_FILE, 'w', encoding='utf-8') as f_out:
            
            in_lecture_block = False
            for line in f_in:
                if LECTURE_INCLUDES_START_MARKER in line:
                    in_lecture_block = True
                elif LECTURE_INCLUDES_END_MARKER in line:
                    in_lecture_block = False

                if in_lecture_block:
                    match = re.search(r'\\input\{([^}]+)\}', line)
                    if match:
                        basename = match.group(1)
                        # This is the logic that comments out older files
                        if basename not in recent_lectures_to_compile:
                            f_out.write(f"% {line.strip()}\n")
                            continue
                
                f_out.write(line)
        print(f"Created temporary file '{TEMP_MASTER_FILE}' with older lectures commented out.")

    except Exception as e:
        print(f"Error creating temporary compile file: {e}")
        exit(1)

    print(f"\nStarting LaTeX compilation of '{TEMP_MASTER_FILE}'...")
    try:
        subprocess.run(
            ['latexmk', '-pdf', '-interaction=nonstopmode', '-file-line-error', TEMP_MASTER_FILE],
            check=True
        )
        print(f"LaTeX compilation successful. Check '{os.path.splitext(TEMP_MASTER_FILE)[0]}.pdf'")
    except subprocess.CalledProcessError as e:
        print(f"Error during LaTeX compilation: {e}")
        print(f"Check the log file for details: '{os.path.splitext(TEMP_MASTER_FILE)[0]}.log'")
    except FileNotFoundError:
        print("Error: 'latexmk' command not found. Please ensure LaTeX and latexmk are installed and in your PATH.")

if __name__ == "__main__":
    compile_latex_selectively()