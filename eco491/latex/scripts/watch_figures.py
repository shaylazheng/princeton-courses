import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURATION ---
FIGURES_DIR = 'figures'
# Absolute path for Inkscape on macOS
INKSCAPE_PATH = '/Applications/Inkscape.app/Contents/MacOS/inkscape'

class SvgSaveHandler(FileSystemEventHandler):
    """Handles SVG save events and triggers PDF+LaTeX export."""
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.svg'):
            self.export_figure(event.src_path)

    def export_figure(self, svg_path):
        """Exports an SVG to PDF and PDF_LaTeX using Inkscape CLI."""
        print(f"Change detected in '{os.path.basename(svg_path)}'. Exporting...")
        
        basename = os.path.splitext(os.path.basename(svg_path))[0]
        output_pdf_path = os.path.join(FIGURES_DIR, f"{basename}.pdf")

        try:
            # This is the modern Inkscape 1.x command line syntax
            command = [
                INKSCAPE_PATH,
                svg_path,
                '--export-area-drawing',
                f'--export-filename={output_pdf_path}',
                '--export-latex'
            ]
            
            # Run the command, hiding the output unless there's an error
            subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Successfully exported '{basename}.pdf' and '{basename}.pdf_tex'.")
        except FileNotFoundError:
            print(f"Error: Inkscape not found at '{INKSCAPE_PATH}'. Please check the path.")
        except subprocess.CalledProcessError as e:
            print(f"Error during Inkscape export for '{svg_path}':")
            print(e.stderr)

def watch_figures():
    """Starts the file watcher."""
    if not os.path.isdir(FIGURES_DIR):
        os.makedirs(FIGURES_DIR)
        print(f"Created figures directory: '{FIGURES_DIR}'")

    print(f"Watching for changes in '{os.path.abspath(FIGURES_DIR)}'...")
    event_handler = SvgSaveHandler()
    observer = Observer()
    observer.schedule(event_handler, FIGURES_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("Figure watcher stopped.")

if __name__ == "__main__":
    watch_figures()