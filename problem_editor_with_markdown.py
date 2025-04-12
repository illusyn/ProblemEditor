import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
import tempfile
import json
from pathlib import Path
from pdf2image import convert_from_path
import platform

# Import the LatexMarkdownParser
from latex_markdown_parser import LatexMarkdownParser

class MathProblemEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Problem Editor")
        self.root.geometry("1200x700")
        
        # Initialize problem data
        self.problem_data = {
            "title": "",
            "markdown_content": "",
            "latex_content": ""
        }
        
        self.current_file = None
        self.temp_dir = Path(tempfile.gettempdir()) / "problem_editor"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create markdown parser
        self.markdown_parser = LatexMarkdownParser()
        
        # Create UI
        self.create_menu()
        self.create_layout()
        
        # Insert initial template
        self.insert_markdown_template()

    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Problem", command=self.new_problem)
        file_menu.add_command(label="Open Problem...", command=self.open_problem)
        file_menu.add_command(label="Save", command=self.save_problem)
        file_menu.add_command(label="Save As...", command=self.save_problem_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export to PDF", command=self.export_to_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Insert menu
        insert_menu = tk.Menu(menubar, tearoff=0)
        insert_menu.add_command(label="Problem Template", command=self.insert_markdown_template)
        insert_menu.add_command(label="Section: Problem", command=self.insert_problem_section)
        insert_menu.add_command(label="Section: Solution", command=self.insert_solution_section)
        insert_menu.add_separator()
        insert_menu.add_command(label="Equation", command=self.insert_equation)
        insert_menu.add_command(label="Aligned Equations", command=self.insert_align)
        insert_menu.add_command(label="Question", command=self.insert_question)
        insert_menu.add_command(label="Figure", command=self.insert_figure)
        insert_menu.add_separator()
        insert_menu.add_command(label="Problem Part (a)", command=lambda: self.insert_part("a"))
        insert_menu.add_command(label="Problem Part (b)", command=lambda: self.insert_part("b"))
        insert_menu.add_command(label="Problem Part (c)", command=lambda: self.insert_part("c"))
        menubar.add_cascade(label="Insert", menu=insert_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Show LaTeX", command=self.show_latex)
        menubar.add_cascade(label="View", menu=view_menu)
        
        self.root.config(menu=menubar)

    def create_layout(self):
        """Create the main application layout"""
        # Main paned window to divide editor and preview
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create left frame for editing
        edit_frame = ttk.Frame(main_paned)
        main_paned.add(edit_frame, weight=1)
        
        # Create right frame for preview
        preview_frame = ttk.Frame(main_paned)
        main_paned.add(preview_frame, weight=1)
        
        # Title field
        title_frame = ttk.Frame(edit_frame)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_frame, text="Problem Title:").pack(side=tk.LEFT)
        self.title_entry = ttk.Entry(title_frame)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Syntax help button
        help_button = ttk.Button(title_frame, text="Syntax Help", command=self.show_syntax_help)
        help_button.pack(side=tk.RIGHT, padx=5)
        
        # Editor tabs
        self.notebook = ttk.Notebook(edit_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Markdown Editor Tab
        markdown_frame = ttk.Frame(self.notebook)
        self.notebook.add(markdown_frame, text="Markdown Editor")
        
        # Using scrolledtext for the editor
        self.markdown_editor = scrolledtext.ScrolledText(markdown_frame, wrap=tk.WORD, undo=True, font=('Courier', 10))
        self.markdown_editor.pack(fill=tk.BOTH, expand=True)
        
        # LaTeX Preview Tab
        latex_frame = ttk.Frame(self.notebook)
        self.notebook.add(latex_frame, text="LaTeX Preview")
        
        self.latex_editor = scrolledtext.ScrolledText(latex_frame, wrap=tk.WORD, font=('Courier', 10))
        self.latex_editor.pack(fill=tk.BOTH, expand=True)
        
        # Status label for feedback
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(edit_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Preview button
        preview_button = ttk.Button(edit_frame, text="Update Preview", command=self.update_preview)
        preview_button.pack(pady=5)
        
        # Preview label
        ttk.Label(preview_frame, text="PDF Preview").pack(anchor=tk.W, padx=5, pady=5)
        
        # Preview scrollable area
        preview_canvas_frame = ttk.Frame(preview_frame)
        preview_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a canvas with scrollbar for preview
        self.preview_canvas = tk.Canvas(preview_canvas_frame, background="white")
        preview_scrollbar = ttk.Scrollbar(preview_canvas_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preview_canvas.configure(yscrollcommand=preview_scrollbar.set)
        
        # Frame inside canvas for preview content
        self.preview_frame = ttk.Frame(self.preview_canvas)
        self.preview_canvas.configure(background="white")
        self.canvas_window = self.preview_canvas.create_window((0, 0), window=self.preview_frame, anchor=tk.NW)
        
        # Configure canvas when frame size changes
        self.preview_frame.bind("<Configure>", self.on_frame_configure)
        self.preview_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Store a reference to preview images to prevent garbage collection
        self.preview_images = []

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Adjust the width of the frame to fill the canvas"""
        canvas_width = event.width
        self.preview_canvas.itemconfig(self.canvas_window, width=canvas_width)

    def insert_markdown_template(self):
        """Insert initial markdown template"""
        template = """#problem
Write your problem statement here...

#eq
y = mx + b

#question
What is the value of m?

#solution
Write your solution here...

#eq
m = 2
"""
        self.markdown_editor.delete("1.0", tk.END)
        self.markdown_editor.insert("1.0", template)

    def insert_problem_section(self):
        """Insert a problem section marker"""
        self.markdown_editor.insert(tk.INSERT, "\n#problem\n")

    def insert_solution_section(self):
        """Insert a solution section marker"""
        self.markdown_editor.insert(tk.INSERT, "\n#solution\n")

    def insert_equation(self):
        """Insert an equation template"""
        self.markdown_editor.insert(tk.INSERT, "\n#eq\ny = mx + b\n")

    def insert_align(self):
        """Insert an align environment"""
        align = """
#align
y &= mx + b \\\\
y - b &= mx
"""
        self.markdown_editor.insert(tk.INSERT, align)

    def insert_question(self):
        """Insert a question marker"""
        self.markdown_editor.insert(tk.INSERT, "\n#question\nWhat is the value of...?\n")

    def insert_figure(self):
        """Insert a figure"""
        self.markdown_editor.insert(tk.INSERT, "\n#figure[imagename.png][Figure caption]\n")

    def insert_part(self, part_letter):
        """Insert a problem part marker"""
        self.markdown_editor.insert(tk.INSERT, f"\n#part({part_letter}) Write part {part_letter} here...\n")

    def show_latex(self):
        """Convert markdown to LaTeX and show in LaTeX tab"""
        try:
            markdown_content = self.markdown_editor.get("1.0", tk.END)
            latex_content = self.markdown_parser.parse(markdown_content)
            
            self.latex_editor.delete("1.0", tk.END)
            self.latex_editor.insert("1.0", latex_content)
            
            # Switch to LaTeX tab
            self.notebook.select(1)  # Index 1 is the LaTeX tab
            
            self.status_var.set("LaTeX generated")
        except Exception as e:
            self.status_var.set(f"Error generating LaTeX: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate LaTeX: {e}")

    def update_preview(self):
        """Update the LaTeX preview"""
        try:
            # Update status
            self.status_var.set("Compiling LaTeX...")
            self.root.update_idletasks()  # Force update to show status
            
            # Get markdown content
            markdown_content = self.markdown_editor.get("1.0", tk.END)
            
            # Convert to LaTeX
            latex_content = self.markdown_parser.parse(markdown_content)
            
            # Update LaTeX preview
            self.latex_editor.delete("1.0", tk.END)
            self.latex_editor.insert("1.0", latex_content)
            
            # Create a temporary LaTeX file
            tex_file = os.path.join(self.temp_dir, "preview.tex")
            
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(latex_content)
            
            # Compile LaTeX to PDF
            current_dir = os.getcwd()
            os.chdir(self.temp_dir)
            
            # Run pdflatex
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "preview.tex"],
                capture_output=True,
                text=True
            )
            
            os.chdir(current_dir)
            
            if result.returncode != 0:
                error_log = result.stdout + "\n" + result.stderr
                self.status_var.set("LaTeX compilation failed")
                messagebox.showerror("LaTeX Error", f"Failed to compile LaTeX.\n\nError details:\n{error_log[-500:]}")
                return
            
            # Convert PDF to images and display
            pdf_path = os.path.join(self.temp_dir, "preview.pdf")
            self.display_pdf(pdf_path)
            self.status_var.set("Preview updated")
            
        except Exception as e:
            self.status_var.set(f"Preview error: {str(e)}")
            messagebox.showerror("Error", f"Preview error: {str(e)}")

    def display_pdf(self, pdf_path):
        """Convert and display PDF preview"""
        try:
            # Clear previous preview
            for widget in self.preview_frame.winfo_children():
                widget.destroy()
            self.preview_images = []  # Clear image references
            
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=120)  # Lower DPI for faster preview
            
            # Display each page
            for i, img in enumerate(images):
                # Resize to fit canvas width if needed
                canvas_width = self.preview_canvas.winfo_width()
                if canvas_width > 50:  # Only resize if canvas has width
                    w, h = img.size
                    ratio = min(1.0, (canvas_width - 20) / w)  # Don't enlarge, leave some margin
                    new_w = int(w * ratio)
                    new_h = int(h * ratio)
                    img = img.resize((new_w, new_h), Image.LANCZOS)
                
                # Convert to PhotoImage
                photo = tk.PhotoImage(data=img.tobytes())
                self.preview_images.append(photo)  # Keep reference
                
                # Create label to display image
                img_label = ttk.Label(self.preview_frame, image=photo)
                img_label.pack(pady=10)
                
                # Add separator between pages
                if i < len(images) - 1:
                    ttk.Separator(self.preview_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=5)
            
            # Update canvas scroll region
            self.preview_canvas.update_idletasks()
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
        except Exception as e:
            self.status_var.set(f"Display error: {str(e)}")
            messagebox.showerror("Display Error", str(e))

    def show_syntax_help(self):
        """Show help window with markdown syntax reference"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Markdown Syntax Help")
        help_window.geometry("500x600")
        
        help_text = """
# LaTeX Markdown Syntax Reference

## Sections
#problem       - Starts a problem section
#solution      - Starts a solution section
#question      - Defines the question text

## Equations
#eq            - Single equation
#align         - Aligned equations
#$...$         - Inline math

## Problem Parts
#part(a)       - Part (a) of a multi-part problem
#part(b)       - Part (b) of a multi-part problem
#part(c)       - Part (c) of a multi-part problem

## Figures
#figure[filename.png][caption]
               - Insert a figure with optional caption

## Example
#problem
Find the solution to the following equation:

#eq
2x + 3 = 7

#question
What is the value of x?

#solution
To solve this equation, we isolate x:

#eq
2x = 4

#eq
x = 2
"""
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=('Courier', 10))
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_text_widget.insert("1.0", help_text)
        help_text_widget.configure(state="disabled")  # Make read-only
        
        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)

    def new_problem(self):
        """Create a new problem"""
        self.current_file = None
        self.title_entry.delete(0, tk.END)
        self.insert_markdown_template()
        self.status_var.set("New problem created")

    def open_problem(self):
        """Open a problem file"""
        file_path = filedialog.askopenfilename(
            title="Open Problem",
            filetypes=[("Problem files", "*.prob"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                problem_data = json.load(file)
            
            self.problem_data = problem_data
            self.current_file = file_path
            
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, problem_data.get("title", ""))
            
            self.markdown_editor.delete("1.0", tk.END)
            self.markdown_editor.insert("1.0", problem_data.get("markdown_content", ""))
            
            # Update LaTeX view
            latex_content = problem_data.get("latex_content", "")
            if not latex_content:
                # If no latex content saved, generate it from markdown
                latex_content = self.markdown_parser.parse(problem_data.get("markdown_content", ""))
                
            self.latex_editor.delete("1.0", tk.END)
            self.latex_editor.insert("1.0", latex_content)
            
            self.status_var.set(f"Opened: {os.path.basename(file_path)}")
            
            # Update preview
            self.update_preview()
            
        except Exception as e:
            self.status_var.set(f"Error opening file: {str(e)}")
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def save_problem(self):
        """Save the current problem"""
        if not self.current_file:
            return self.save_problem_as()
            
        return self._save_to_file(self.current_file)

    def save_problem_as(self):
        """Save the problem to a new file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Problem As",
            defaultextension=".prob",
            filetypes=[("Problem files", "*.prob"), ("All files", "*.*")]
        )
        
        if not file_path:
            return False
            
        return self._save_to_file(file_path)

    def _save_to_file(self, file_path):
        """Save problem data to file"""
        try:
            # Get markdown content
            markdown_content = self.markdown_editor.get("1.0", tk.END)
            
            # Convert to LaTeX
            latex_content = self.markdown_parser.parse(markdown_content)
            
            # Update problem data
            self.problem_data["title"] = self.title_entry.get()
            self.problem_data["markdown_content"] = markdown_content
            self.problem_data["latex_content"] = latex_content
            
            # Save problem data
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.problem_data, file, indent=4)
            
            self.current_file = file_path
            self.status_var.set(f"Saved to: {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            self.status_var.set(f"Error saving: {str(e)}")
            messagebox.showerror("Error", f"Failed to save file: {e}")
            return False

    def export_to_pdf(self):
        """Export the current problem to a PDF file"""
        file_path = filedialog.asksaveasfilename(
            title="Export to PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Get markdown content and convert to LaTeX
            markdown_content = self.markdown_editor.get("1.0", tk.END)
            latex_content = self.markdown_parser.parse(markdown_content)
            
            # Compile LaTeX to PDF
            self.status_var.set("Exporting to PDF...")
            tex_file = os.path.join(self.temp_dir, "export.tex")
            
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(latex_content)
            
            current_dir = os.getcwd()
            os.chdir(self.temp_dir)
            
            result = subprocess.run(["pdflatex", "-interaction=nonstopmode", "export.tex"], capture_output=True)
            
            os.chdir(current_dir)
            
            if result.returncode != 0:
                self.status_var.set("PDF export failed")
                messagebox.showerror("Error", "LaTeX compilation failed")
                return
            
            # Copy the resulting PDF to the target path
            pdf_path = os.path.join(self.temp_dir, "export.pdf")
            import shutil
            shutil.copy2(pdf_path, file_path)
            
            self.status_var.set(f"Exported to: {os.path.basename(file_path)}")
            
            # Ask if user wants to open the PDF
            if messagebox.askyesno("Export Complete", f"PDF exported to {file_path}. Open now?"):
                self.open_file(file_path)
            
        except Exception as e:
            self.status_var.set(f"Export error: {str(e)}")
            messagebox.showerror("Export Error", str(e))
            
    def open_file(self, file_path):
        """Open a file with the default application"""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            self.status_var.set(f"Error opening file: {str(e)}")
            messagebox.showerror("Error", f"Failed to open file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MathProblemEditor(root)
    root.mainloop()