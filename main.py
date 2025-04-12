#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
import tempfile
import re
from PIL import Image, ImageTk
import json
import platform
from pathlib import Path
from pdf2image import convert_from_path

class MathProblemEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Problem Editor")
        self.root.geometry("1600x900")
        
        # Initialize problem data
        self.problem_data = {
            "title": "",
            "latex_content": "",
            "images": []
        }
        
        # Settings with default values
        self.editor_font_size = 14
        self.preview_zoom = 2.5
        self.preview_dpi = 300
        
        self.current_file = None
        self.temp_dir = Path(tempfile.gettempdir()) / "problem_editor"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup MathML conversion
        try:
            import lxml.etree as ET
            self.mathml_converter_available = True
        except ImportError:
            self.mathml_converter_available = False
            print("lxml not installed. MathML conversion will be limited.")
        
        # Create UI
        self.create_menu()
        self.create_layout()
        
        # Insert initial template
        self.insert_initial_template()

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
        insert_menu.add_command(label="Insert Equation", command=self.insert_equation)
        insert_menu.add_command(label="Insert Align Environment", command=self.insert_align)
        insert_menu.add_command(label="Insert Figure", command=self.insert_figure)
        insert_menu.add_command(label="Insert Matrix", command=self.insert_matrix)
        insert_menu.add_separator()
        insert_menu.add_command(label="Paste MathML Equation", command=self.paste_mathml)
        menubar.add_cascade(label="Insert", menu=insert_menu)
        
        # View menu for size controls
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Increase Editor Font", command=self.increase_editor_font)
        view_menu.add_command(label="Decrease Editor Font", command=self.decrease_editor_font)
        view_menu.add_separator()
        view_menu.add_command(label="Increase Preview Size", command=self.increase_preview_zoom)
        view_menu.add_command(label="Decrease Preview Size", command=self.decrease_preview_zoom)
        view_menu.add_separator()
        view_menu.add_command(label="Reset Sizes to Default", command=self.reset_sizes)
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
        
        # Add size control toolbar
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Editor size controls
        ttk.Label(control_frame, text="Editor Size:").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="-", width=2, command=self.decrease_editor_font).pack(side=tk.LEFT)
        self.editor_size_label = ttk.Label(control_frame, text=f"{self.editor_font_size}pt")
        self.editor_size_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="+", width=2, command=self.increase_editor_font).pack(side=tk.LEFT)
        
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Preview size controls
        ttk.Label(control_frame, text="Preview Zoom:").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="-", width=2, command=self.decrease_preview_zoom).pack(side=tk.LEFT)
        self.preview_zoom_label = ttk.Label(control_frame, text=f"{self.preview_zoom:.1f}x")
        self.preview_zoom_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="+", width=2, command=self.increase_preview_zoom).pack(side=tk.LEFT)
        
        ttk.Button(control_frame, text="Reset", command=self.reset_sizes).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="Update Preview", command=self.update_preview).pack(side=tk.RIGHT, padx=5)
        
        # Title field
        title_frame = ttk.Frame(edit_frame)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_frame, text="Problem Title:").pack(side=tk.LEFT)
        self.title_entry = ttk.Entry(title_frame)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # LaTeX Editor
        editor_frame = ttk.LabelFrame(edit_frame, text="LaTeX Editor")
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Using scrolledtext for the editor
        self.editor = scrolledtext.ScrolledText(
            editor_frame, 
            wrap=tk.WORD, 
            undo=True, 
            font=('Courier', self.editor_font_size)
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Status label for feedback
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(edit_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Preview label
        ttk.Label(preview_frame, text="LaTeX Preview").pack(anchor=tk.W, padx=5, pady=5)
        
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

    def increase_editor_font(self):
        """Increase the font size in the editor"""
        if self.editor_font_size < 32:  # Set a reasonable upper limit
            self.editor_font_size += 2
            self.editor.configure(font=('Courier', self.editor_font_size))
            self.editor_size_label.configure(text=f"{self.editor_font_size}pt")
            self.status_var.set(f"Editor font size: {self.editor_font_size}pt")

    def decrease_editor_font(self):
        """Decrease the font size in the editor"""
        if self.editor_font_size > 8:  # Set a reasonable lower limit
            self.editor_font_size -= 2
            self.editor.configure(font=('Courier', self.editor_font_size))
            self.editor_size_label.configure(text=f"{self.editor_font_size}pt")
            self.status_var.set(f"Editor font size: {self.editor_font_size}pt")

    def increase_preview_zoom(self):
        """Increase the zoom level for the preview"""
        if self.preview_zoom < 5.0:  # Set a reasonable upper limit
            self.preview_zoom += 0.5
            self.preview_zoom_label.configure(text=f"{self.preview_zoom:.1f}x")
            self.status_var.set(f"Preview zoom: {self.preview_zoom:.1f}x")
            # Update the preview to reflect the new zoom level
            self.update_preview()

    def decrease_preview_zoom(self):
        """Decrease the zoom level for the preview"""
        if self.preview_zoom > 1.0:  # Set a reasonable lower limit
            self.preview_zoom -= 0.5
            self.preview_zoom_label.configure(text=f"{self.preview_zoom:.1f}x")
            self.status_var.set(f"Preview zoom: {self.preview_zoom:.1f}x")
            # Update the preview to reflect the new zoom level
            self.update_preview()

    def reset_sizes(self):
        """Reset all sizes to default values"""
        # Reset editor font size
        self.editor_font_size = 14
        self.editor.configure(font=('Courier', self.editor_font_size))
        self.editor_size_label.configure(text=f"{self.editor_font_size}pt")
        
        # Reset preview zoom
        self.preview_zoom = 2.5
        self.preview_zoom_label.configure(text=f"{self.preview_zoom:.1f}x")
        
        # Reset preview DPI
        self.preview_dpi = 300
        
        self.status_var.set("Size settings reset to defaults")
        
        # Update the preview
        self.update_preview()

    def insert_initial_template(self):
        """Insert initial LaTeX template"""
        template = r"""\documentclass[14pt]{extarticle}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{setspace}
\onehalfspacing

\begin{document}

\section*{Problem}
Write your problem statement here...

\section*{Solution}
Write your solution here...

\end{document}
"""
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", template)

    def insert_equation(self):
        """Insert an equation template at cursor position"""
        equation = r"""
\begin{equation}
    f(x) = ax^2 + bx + c
\end{equation}
"""
        self.editor.insert(tk.INSERT, equation)

    def insert_align(self):
        """Insert an align environment at cursor position"""
        align = r"""
\begin{align}
    f(x) &= ax^2 + bx + c \\
    &= a(x - h)^2 + k
\end{align}
"""
        self.editor.insert(tk.INSERT, align)

    def insert_figure(self):
        """Insert a figure environment at cursor position"""
        figure = r"""
\begin{figure}[h]
    \centering
    \includegraphics[width=0.5\textwidth]{imagename.png}
    \caption{Figure caption}
    \label{fig:mylabel}
\end{figure}
"""
        self.editor.insert(tk.INSERT, figure)

    def insert_matrix(self):
        """Insert a matrix environment at cursor position"""
        matrix = r"""
\begin{pmatrix}
    a_{11} & a_{12} & a_{13} \\
    a_{21} & a_{22} & a_{23} \\
    a_{31} & a_{32} & a_{33}
\end{pmatrix}
"""
        self.editor.insert(tk.INSERT, matrix)
        
    def paste_mathml(self):
        """Convert clipboard MathML content to LaTeX and insert at cursor"""
        try:
            # Get clipboard content
            mathml_content = self.root.clipboard_get()
            
            if not mathml_content.strip().startswith("<math") and not mathml_content.strip().startswith("<?xml"):
                messagebox.showwarning("Invalid Content", "Clipboard doesn't contain valid MathML content.")
                return
            
            # Convert MathML to LaTeX
            latex_content = self.convert_mathml_to_latex(mathml_content)
            
            if latex_content:
                # Format as an equation
                formatted_eq = self.format_as_equation(latex_content)
                
                # Insert the formatted equation at cursor position
                self.editor.insert(tk.INSERT, formatted_eq)
                self.status_var.set("MathML equation converted and inserted")
            else:
                self.status_var.set("Failed to convert MathML")
                
        except tk.TclError:
            messagebox.showwarning("Empty Clipboard", "No content in clipboard.")
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Error converting MathML to LaTeX: {str(e)}")
    
    def format_as_equation(self, latex_content):
        """Format LaTeX content as a displayed equation with proper spacing"""
        # Remove any existing math delimiters
        if latex_content.startswith("$") and latex_content.endswith("$"):
            latex_content = latex_content[1:-1]
        
        # Format with proper spacing and display math delimiters
        return f"\n\\[\n    {latex_content}\n\\]\n"
            
    def convert_mathml_to_latex(self, mathml_content):
        """Convert MathML content to LaTeX"""
        # Try the XML-based conversion first, falling back to regex-based if needed
        if self.mathml_converter_available:
            try:
                import lxml.etree as ET
                
                # Parse the MathML content
                if mathml_content.strip().startswith("<?xml"):
                    # It's a complete XML document
                    root = ET.fromstring(mathml_content.encode('utf-8'))
                    # Find the math element
                    math_element = root.find(".//{http://www.w3.org/1998/Math/MathML}math")
                    if math_element is None:
                        math_element = root.find(".//math")
                else:
                    # It's just a math element
                    math_element = ET.fromstring(mathml_content.encode('utf-8'))
                
                if math_element is None:
                    raise ValueError("No math element found in MathML content")
                
                # Process the math element and its children
                latex = self._process_mathml_element(math_element)
                return latex
                
            except Exception as e:
                print(f"Error in XML parsing: {e}")
                # Fall back to simple conversion
                return self._simple_mathml_to_latex(mathml_content)
        else:
            # Use simple conversion if lxml is not available
            return self._simple_mathml_to_latex(mathml_content)
    
    def _process_mathml_element(self, element):
        """Process a MathML element and convert it to LaTeX"""
        tag = element.tag
        if tag.endswith("math"):
            # Process children
            content = ""
            for child in element:
                content += self._process_mathml_element(child)
            return content
            
        elif tag.endswith("mi"):
            # Math identifier (variables)
            text = element.text or ""
            # Special handling for Greek letters
            greek_letters = {
                "alpha": r"\alpha", "beta": r"\beta", "gamma": r"\gamma",
                "delta": r"\delta", "epsilon": r"\epsilon", "zeta": r"\zeta",
                "eta": r"\eta", "theta": r"\theta", "iota": r"\iota",
                "kappa": r"\kappa", "lambda": r"\lambda", "mu": r"\mu",
                "nu": r"\nu", "xi": r"\xi", "omicron": r"\omicron",
                "pi": r"\pi", "rho": r"\rho", "sigma": r"\sigma",
                "tau": r"\tau", "upsilon": r"\upsilon", "phi": r"\phi",
                "chi": r"\chi", "psi": r"\psi", "omega": r"\omega"
            }
            if text.lower() in greek_letters:
                return greek_letters[text.lower()]
            return text
            
        elif tag.endswith("mn"):
            # Math number
            return element.text or ""
            
        elif tag.endswith("mo"):
            # Math operator
            operator = element.text or ""
            # Map common operators
            operator_map = {
                "+": "+", "-": "-", "×": r"\times", "÷": r"\div",
                "=": "=", "<": "<", ">": ">", "≤": r"\leq", "≥": r"\geq",
                "∑": r"\sum", "∫": r"\int", "∏": r"\prod",
                "∈": r"\in", "∉": r"\notin", "⊂": r"\subset",
                "∪": r"\cup", "∩": r"\cap",
                "√": r"\sqrt", "∞": r"\infty",
                "±": r"\pm", "∓": r"\mp", "·": r"\cdot",
                "≈": r"\approx", "≠": r"\neq", "≡": r"\equiv",
                "→": r"\rightarrow", "←": r"\leftarrow", 
                "⇒": r"\Rightarrow", "⇐": r"\Leftarrow",
                "↔": r"\leftrightarrow", "⇔": r"\Leftrightarrow"
            }
            return operator_map.get(operator, operator)
            
        elif tag.endswith("mrow"):
            # Row of math elements
            content = ""
            for child in element:
                content += self._process_mathml_element(child)
            return content.strip()
            
        elif tag.endswith("msup"):
            # Superscript
            children = list(element)
            if len(children) >= 2:
                base = self._process_mathml_element(children[0])
                exponent = self._process_mathml_element(children[1])
                return f"{{{base}}}^{{{exponent}}}"
            return ""
            
        elif tag.endswith("msub"):
            # Subscript
            children = list(element)
            if len(children) >= 2:
                base = self._process_mathml_element(children[0])
                subscript = self._process_mathml_element(children[1])
                return f"{{{base}}}_{{{subscript}}}"
            return ""
            
        elif tag.endswith("mfrac"):
            # Fraction
            children = list(element)
            if len(children) >= 2:
                numerator = self._process_mathml_element(children[0])
                denominator = self._process_mathml_element(children[1])
                # Handle whitespace
                numerator = numerator.strip()
                denominator = denominator.strip()
                return f"\\frac{{{numerator}}}{{{denominator}}}"
            return ""
            
        elif tag.endswith("msqrt"):
            # Square root
            content = ""
            for child in element:
                content += self._process_mathml_element(child)
            return f"\\sqrt{{{content.strip()}}}"
            
        elif tag.endswith("mroot"):
            # nth root
            children = list(element)
            if len(children) >= 2:
                base = self._process_mathml_element(children[0])
                index = self._process_mathml_element(children[1])
                return f"\\sqrt[{index.strip()}]{{{base.strip()}}}"
            return ""
            
        # Default: return text content if available
        return (element.text or "").strip()
    
    def _simple_mathml_to_latex(self, mathml_content):
        """Simple MathML to LaTeX conversion using string replacement"""
        import re
        
        # Extract content within <math> tags if present
        math_match = re.search(r'<math[^>]*>(.*?)</math>', mathml_content, re.DOTALL)
        if math_match:
            content = math_match.group(1)
        else:
            content = mathml_content
        
        # Try to process fractions with mfrac tag - this is key for proper handling
        frac_pattern = r'<mfrac>\s*<mrow>(.*?)</mrow>\s*<mrow>(.*?)</mrow>\s*</mfrac>'
        content = re.sub(frac_pattern, r'\\frac{\1}{\2}', content)
        
        # Simple fraction pattern (without mrow)
        simple_frac = r'<mfrac>\s*<mn>([^<]+)</mn>\s*<mrow>(.*?)</mrow>\s*</mfrac>'
        content = re.sub(simple_frac, r'\\frac{\1}{\2}', content)
        
        # Even simpler fraction pattern
        very_simple_frac = r'<mfrac>\s*(.*?)\s*(.*?)\s*</mfrac>'
        content = re.sub(very_simple_frac, r'\\frac{\1}{\2}', content)
        
        # Basic replacements for other elements
        replacements = [
            (r'<mi>\s*([^<]+)\s*</mi>', r'\1'),          # Math identifiers
            (r'<mn>\s*([^<]+)\s*</mn>', r'\1'),          # Numbers
            (r'<mo>\s*([^<]+)\s*</mo>', r'\1'),          # Operators
            (r'<mrow>\s*(.*?)\s*</mrow>', r'\1'),        # Rows
            (r'<msup>\s*<mi>([^<]+)</mi>\s*<mn>([^<]+)</mn>\s*</msup>', r'\1^{\2}'),  # Superscripts
            (r'<msub>\s*<mi>([^<]+)</mi>\s*<mn>([^<]+)</mn>\s*</msub>', r'\1_{\2}'),  # Subscripts
            (r'<msqrt>\s*(.*?)\s*</msqrt>', r'\\sqrt{\1}'),  # Square roots
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Remove any remaining tags
        content = re.sub(r'<[^>]*>', '', content)
        
        # Don't add math delimiters here - they will be added by format_as_equation
        return content

    def update_preview(self):
        """Update the LaTeX preview"""
        try:
            # Update status
            self.status_var.set("Compiling LaTeX...")
            self.root.update_idletasks()  # Force update to show status
            
            # Create a temporary LaTeX file
            latex_content = self.editor.get("1.0", tk.END)
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
            
            # Convert PDF to images using current DPI setting
            images = convert_from_path(pdf_path, dpi=self.preview_dpi)
            
            # Display each page with current zoom factor
            for i, img in enumerate(images):
                # Resize to fit canvas width if needed
                canvas_width = self.preview_canvas.winfo_width()
                if canvas_width > 50:  # Only resize if canvas has width
                    w, h = img.size
                    ratio = min(5.0, (canvas_width - 20) / w * self.preview_zoom)  # Apply zoom factor
                    new_w = int(w * ratio)
                    new_h = int(h * ratio)
                    img = img.resize((new_w, new_h), Image.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
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

    def new_problem(self):
        """Create a new problem"""
        self.current_file = None
        self.title_entry.delete(0, tk.END)
        self.insert_initial_template()
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
            
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", problem_data.get("latex_content", ""))
            
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
            # Update problem data
            self.problem_data["title"] = self.title_entry.get()
            self.problem_data["latex_content"] = self.editor.get("1.0", tk.END)
            
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
            # Compile LaTeX to PDF
            self.status_var.set("Exporting to PDF...")
            latex_content = self.editor.get("1.0", tk.END)
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