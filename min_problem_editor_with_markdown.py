import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
import tempfile
import json
from pathlib import Path
import platform
from PIL import Image, ImageTk
from pdf2image import convert_from_path
import re

class ConfigurableLatexParser:
    """
    A parser that converts simple markdown to LaTeX with configurable formatting options.
    """
    
    def __init__(self, config_file=None):
        # Default configuration values
        self.config = {
            "fonts": {
                "main_text_size": "14pt",
                "problem_header_size": "18pt",
                "question_size": "16pt",
                "equation_size": "16pt"
            },
            "spacing": {
                "line_spacing": "1.5",
                "above_equation": "12pt",
                "below_equation": "12pt",
                "paragraph_spacing": "6pt"
            },
            "styling": {
                "question_format": "\\textbf{{Question:}} {0}",
                "problem_format": "\\section*{{{0}}}"
            },
            "margins": {
                "top": "0.75in",
                "right": "0.75in",
                "bottom": "0.75in",
                "left": "0.75in"
            }
        }
        
        # Load configuration from file if provided
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        
        # Create the document template with placeholders for configuration
        self.document_template = r"""\documentclass{{article}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{graphicx}}
\usepackage{{geometry}}
\usepackage{{setspace}}

% Configure fonts and spacing from config
\geometry{{top={margins[top]}, right={margins[right]}, bottom={margins[bottom]}, left={margins[left]}}}
\setstretch{{{spacing[line_spacing]}}}

% Set font sizes
\newcommand{{\problemheaderfont}}{{\fontsize{{{fonts[problem_header_size]}}}}{{24pt}}\selectfont}}
\newcommand{{\questionfont}}{{\fontsize{{{fonts[question_size]}}}}{{20pt}}\selectfont}}
\newcommand{{\maintextfont}}{{\fontsize{{{fonts[main_text_size]}}}}{{18pt}}\selectfont}}

% Customize section titles
\usepackage{{titlesec}}
\titleformat*{{\section}}{{\problemheaderfont\bfseries}}

% Ensure displaystyle for equations
\everymath{{\displaystyle}}

\begin{{document}}

\maintextfont

{0}

\end{{document}}
"""

    def load_config(self, config_file):
        """Load configuration from a JSON file."""
        try:
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                
            # Update the configuration with user values
            for category in user_config:
                if category in self.config:
                    self.config[category].update(user_config[category])
        except Exception as e:
            print(f"Error loading configuration: {e}")
    
    def save_config(self, config_file):
        """Save the current configuration to a JSON file."""
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False

    def parse(self, markdown_text):
        """Convert markdown to LaTeX using the current configuration."""
        # Process the content
        content = markdown_text.strip()
        
        # Process sections using the configured format
        problem_format = self.config["styling"]["problem_format"]
        content = content.replace("#problem\n", problem_format.format("Problem") + "\n")
        content = content.replace("#solution\n", problem_format.format("Solution") + "\n")
        
        # Process question using the configured format
        question_format = self.config["styling"]["question_format"]
        question_pattern = r'#question\s*(.*?)(?=\n#|\n\s*$|\s*$)'
        
        def question_replace(match):
            return question_format.format(match.group(1).strip())
            
        content = re.sub(question_pattern, question_replace, content, flags=re.DOTALL)
        
        # Setup equation spacing based on configuration
        above_eq_space = self.config["spacing"]["above_equation"]
        below_eq_space = self.config["spacing"]["below_equation"]
        
        # Process equations with configurable spacing
        lines = content.split('\n')
        processed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.strip() == "#eq":
                # Add spacing before equation
                processed_lines.append(f"\\vspace{{{above_eq_space}}}")
                processed_lines.append("\\begin{equation}")
                i += 1  # Move to next line
                
                # Collect all lines until we find another marker or end
                while i < len(lines) and not lines[i].strip().startswith('#'):
                    if lines[i].strip():  # Only add non-empty lines
                        processed_lines.append(lines[i])
                    i += 1
                
                processed_lines.append("\\end{equation}")
                processed_lines.append(f"\\vspace{{{below_eq_space}}}")
                
            elif line.strip() == "#align":
                # Add spacing before align environment
                processed_lines.append(f"\\vspace{{{above_eq_space}}}")
                processed_lines.append("\\begin{align}")
                i += 1
                
                while i < len(lines) and not lines[i].strip().startswith('#'):
                    if lines[i].strip():  # Only add non-empty lines
                        processed_lines.append(lines[i])
                    i += 1
                
                processed_lines.append("\\end{align}")
                processed_lines.append(f"\\vspace{{{below_eq_space}}}")
                
            else:
                # Normal line, just add it
                processed_lines.append(line)
                i += 1
        
        # Join everything back together
        content = '\n'.join(processed_lines)
        
        # Format the document template with the current configuration
        formatted_template = self.document_template.format(
            fonts=self.config["fonts"],
            spacing=self.config["spacing"],
            margins=self.config["margins"]
        )
        
        # Insert the content into the formatted template
        return formatted_template.format(content)


class ConfigurationDialog(tk.Toplevel):
    """Dialog window for editing configuration settings."""
    
    def __init__(self, parent, config, callback):
        super().__init__(parent)
        self.title("Edit Configuration")
        self.geometry("600x500")
        self.parent = parent
        self.config = config
        self.callback = callback
        self.result = None
        
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs for different configuration categories
        self.create_fonts_tab()
        self.create_spacing_tab()
        self.create_styling_tab()
        self.create_margins_tab()
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add save and cancel buttons
        save_button = ttk.Button(button_frame, text="Save", command=self.save_config)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Make the dialog modal
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def create_fonts_tab(self):
        """Create the fonts configuration tab."""
        fonts_frame = ttk.Frame(self.notebook)
        self.notebook.add(fonts_frame, text="Fonts")
        
        # Configure grid
        fonts_frame.columnconfigure(1, weight=1)
        
        # Create entry fields for each font setting
        font_settings = self.config["fonts"]
        row = 0
        
        self.font_vars = {}
        for key, value in font_settings.items():
            # Create a user-friendly label
            label_text = key.replace("_", " ").title()
            ttk.Label(fonts_frame, text=f"{label_text}:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
            
            # Create an entry field with the current value
            self.font_vars[key] = tk.StringVar(value=value)
            entry = ttk.Entry(fonts_frame, textvariable=self.font_vars[key])
            entry.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=5)
            
            row += 1
        
        # Add a help text
        help_text = "Font sizes should be specified with units (e.g., 12pt, 14pt, 18pt)"
        ttk.Label(fonts_frame, text=help_text, foreground="gray").grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=15)

    def create_spacing_tab(self):
        """Create the spacing configuration tab."""
        spacing_frame = ttk.Frame(self.notebook)
        self.notebook.add(spacing_frame, text="Spacing")
        
        # Configure grid
        spacing_frame.columnconfigure(1, weight=1)
        
        # Create entry fields for each spacing setting
        spacing_settings = self.config["spacing"]
        row = 0
        
        self.spacing_vars = {}
        for key, value in spacing_settings.items():
            # Create a user-friendly label
            label_text = key.replace("_", " ").title()
            ttk.Label(spacing_frame, text=f"{label_text}:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
            
            # Create an entry field with the current value
            self.spacing_vars[key] = tk.StringVar(value=value)
            entry = ttk.Entry(spacing_frame, textvariable=self.spacing_vars[key])
            entry.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=5)
            
            row += 1
        
        # Add a help text
        help_text = "Line spacing should be a number (e.g., 1.5). \nOther spacing values should include units (e.g., 12pt, 1em)."
        ttk.Label(spacing_frame, text=help_text, foreground="gray").grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=15)

    def create_styling_tab(self):
        """Create the styling configuration tab."""
        styling_frame = ttk.Frame(self.notebook)
        self.notebook.add(styling_frame, text="Styling")
        
        # Configure grid
        styling_frame.columnconfigure(1, weight=1)
        
        # Create entry fields for each styling setting
        styling_settings = self.config["styling"]
        row = 0
        
        self.styling_vars = {}
        for key, value in styling_settings.items():
            # Create a user-friendly label
            label_text = key.replace("_", " ").title()
            ttk.Label(styling_frame, text=f"{label_text}:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
            
            # Create an entry field with the current value
            self.styling_vars[key] = tk.StringVar(value=value)
            entry = ttk.Entry(styling_frame, textvariable=self.styling_vars[key])
            entry.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=5)
            
            row += 1
        
        # Add a help text
        help_text = "Use {0} as a placeholder for text content.\nUse LaTeX commands for formatting (e.g., \\textbf{}, \\large, etc.)."
        ttk.Label(styling_frame, text=help_text, foreground="gray").grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=15)

    def create_margins_tab(self):
        """Create the margins configuration tab."""
        margins_frame = ttk.Frame(self.notebook)
        self.notebook.add(margins_frame, text="Margins")
        
        # Configure grid
        margins_frame.columnconfigure(1, weight=1)
        
        # Create entry fields for each margin setting
        margin_settings = self.config["margins"]
        row = 0
        
        self.margin_vars = {}
        for key, value in margin_settings.items():
            # Create a user-friendly label
            label_text = key.title()
            ttk.Label(margins_frame, text=f"{label_text} Margin:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
            
            # Create an entry field with the current value
            self.margin_vars[key] = tk.StringVar(value=value)
            entry = ttk.Entry(margins_frame, textvariable=self.margin_vars[key])
            entry.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=5)
            
            row += 1
        
        # Add a help text
        help_text = "Margin values should include units (e.g., 0.75in, 2cm, 25mm)."
        ttk.Label(margins_frame, text=help_text, foreground="gray").grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=15)

    def save_config(self):
        """Save the configuration changes."""
        # Update the configuration with values from the entry fields
        for key, var in self.font_vars.items():
            self.config["fonts"][key] = var.get()
            
        for key, var in self.spacing_vars.items():
            self.config["spacing"][key] = var.get()
            
        for key, var in self.styling_vars.items():
            self.config["styling"][key] = var.get()
            
        for key, var in self.margin_vars.items():
            self.config["margins"][key] = var.get()
        
        # Call the callback function with the updated configuration
        self.callback(self.config)
        
        # Close the dialog
        self.destroy()


class ConfigurableProblemEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Problem Editor")
        self.root.geometry("1200x700")
        
        # Set larger font sizes
        self.editor_font_size = 14
        self.editor_font = ('Courier', self.editor_font_size)
        self.ui_font_size = 12
        self.ui_font = ('Arial', self.ui_font_size)
        
        # Configure default font for labels and buttons
        self.root.option_add("*Font", self.ui_font)
        
        # Initialize problem data
        self.problem_data = {
            "title": "",
            "markdown_content": ""
        }
        
        self.current_file = None
        self.temp_dir = Path(tempfile.gettempdir()) / "problem_editor"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration file path (in the same directory as the script)
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editor_config.json")
        
        # Create configurable parser
        self.parser = ConfigurableLatexParser(self.config_file)
        
        # Set zoom to higher default
        self.zoom_var = tk.IntVar(value=200)  # Start with 200% zoom
        
        # Create UI
        self.create_menu()
        self.create_layout()
        
        # Insert initial template
        self.insert_template()
        
        # Store latex content and PDF path
        self.latex_content = None
        self.pdf_path = None

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
        insert_menu.add_command(label="Problem Section", command=self.insert_problem_section)
        insert_menu.add_command(label="Solution Section", command=self.insert_solution_section)
        insert_menu.add_command(label="Question", command=self.insert_question)
        insert_menu.add_separator()
        insert_menu.add_command(label="Equation", command=self.insert_equation)
        insert_menu.add_command(label="Aligned Equations", command=self.insert_align)
        
        menubar.add_cascade(label="Insert", menu=insert_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Show LaTeX Code", command=self.show_latex)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Format menu
        format_menu = tk.Menu(menubar, tearoff=0)
        format_menu.add_command(label="Increase Font Size", command=self.increase_font_size)
        format_menu.add_command(label="Decrease Font Size", command=self.decrease_font_size)
        format_menu.add_separator()
        format_menu.add_command(label="Edit Configuration...", command=self.edit_configuration)
        format_menu.add_command(label="Save Configuration", command=self.save_configuration)
        format_menu.add_command(label="Reset to Default Configuration", command=self.reset_configuration)
        menubar.add_cascade(label="Format", menu=format_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Syntax Help", command=self.show_syntax_help)
        menubar.add_cascade(label="Help", menu=help_menu)
        
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
        ttk.Label(title_frame, text="Problem Title:", font=self.ui_font).pack(side=tk.LEFT)
        self.title_entry = ttk.Entry(title_frame, font=self.ui_font)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Using scrolledtext for the editor
        editor_frame = ttk.LabelFrame(edit_frame, text="Markdown Editor")
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.editor = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, undo=True, font=self.editor_font)
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Status label for feedback
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(edit_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, font=self.ui_font)
        status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Preview button
        preview_button = ttk.Button(edit_frame, text="Update Preview", command=self.update_preview)
        preview_button.pack(pady=5)
        
        # Preview label
        ttk.Label(preview_frame, text="PDF Preview", font=self.ui_font).pack(anchor=tk.W, padx=5, pady=5)
        
        # Preview controls frame
        preview_controls = ttk.Frame(preview_frame)
        preview_controls.pack(fill=tk.X, padx=5)
        
        # Zoom controls
        ttk.Label(preview_controls, text="Zoom:").pack(side=tk.LEFT, padx=5)
        
        zoom_out = ttk.Button(preview_controls, text="-", width=2, 
                             command=self.zoom_out)
        zoom_out.pack(side=tk.LEFT)
        
        self.zoom_label = ttk.Label(preview_controls, textvariable=self.zoom_var, width=4)
        self.zoom_label.pack(side=tk.LEFT)
        ttk.Label(preview_controls, text="%").pack(side=tk.LEFT)
        
        zoom_in = ttk.Button(preview_controls, text="+", width=2, 
                            command=self.zoom_in)
        zoom_in.pack(side=tk.LEFT)
        
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

    def insert_template(self):
        """Insert initial template"""
        template = """#problem
Solve the following equation:

#eq
2x + 3 = 7

#question
What is the value of x?
"""
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", template)

    def insert_problem_section(self):
        """Insert a problem section marker"""
        self.editor.insert(tk.INSERT, "\n#problem\n")

    def insert_solution_section(self):
        """Insert a solution section marker"""
        self.editor.insert(tk.INSERT, "\n#solution\n")

    def insert_question(self):
        """Insert a question marker"""
        self.editor.insert(tk.INSERT, "\n#question\nWhat is the value of...?\n")

    def insert_equation(self):
        """Insert an equation marker"""
        self.editor.insert(tk.INSERT, "\n#eq\n")
        
    def insert_align(self):
        """Insert an aligned equations marker"""
        self.editor.insert(tk.INSERT, "\n#align\nx &= 2y + 1 \\\\\ny &= 3z - 2\n")

    def increase_font_size(self):
        """Increase the font size in the editor"""
        self.editor_font_size += 2
        self.editor.configure(font=('Courier', self.editor_font_size))
        self.status_var.set(f"Font size increased to {self.editor_font_size}")
        
    def decrease_font_size(self):
        """Decrease the font size in the editor"""
        if self.editor_font_size > 8:  # Prevent too small font
            self.editor_font_size -= 2
            self.editor.configure(font=('Courier', self.editor_font_size))
            self.status_var.set(f"Font size decreased to {self.editor_font_size}")

    def edit_configuration(self):
        """Open a dialog to edit configuration settings."""
        def update_config(new_config):
            self.parser.config = new_config
            self.status_var.set("Configuration updated. Update preview to see changes.")
        
        # Create a configuration dialog
        ConfigurationDialog(self.root, self.parser.config, update_config)
    
    def save_configuration(self):
        """Save the current configuration to the config file."""
        if self.parser.save_config(self.config_file):
            self.status_var.set(f"Configuration saved to {self.config_file}")
        else:
            messagebox.showerror("Error", f"Failed to save configuration to {self.config_file}")
    
    def reset_configuration(self):
        """Reset to default configuration."""
        if messagebox.askyesno("Reset Configuration", "Are you sure you want to reset to the default configuration?"):
            # Create a new parser with default configuration
            self.parser = ConfigurableLatexParser()
            self.status_var.set("Configuration reset to defaults. Update preview to see changes.")

    def zoom_in(self):
        """Increase preview zoom level"""
        if self.zoom_var.get() < 300:  # Allow higher zoom levels
            self.zoom_var.set(self.zoom_var.get() + 20)
            if self.pdf_path:
                self.display_pdf(self.pdf_path)
    
    def zoom_out(self):
        """Decrease preview zoom level"""
        if self.zoom_var.get() > 60:
            self.zoom_var.set(self.zoom_var.get() - 20)
            if self.pdf_path:
                self.display_pdf(self.pdf_path)

    def show_syntax_help(self):
        """Show help window with markdown syntax reference"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Markdown Syntax Help")
        help_window.geometry("600x500")
        
        help_text = """
# Markdown Syntax Reference

## Basic Structure
#problem     - Problem section
#solution    - Solution section
#question    - Question text

## Equation Environments
#eq          - Start an equation, put the equation on the next line
#align       - Start an aligned equations environment

## Example:
#problem
Solve the equation:

#eq
2x + 3 = 7

#question
What is x?

#solution
We solve step by step:

#eq
2x = 4

#eq
x = 2

## Configuration
You can customize how elements are rendered through the Format menu:
- Edit Configuration: Modify font sizes, spacing, and formatting
- Save Configuration: Save your settings for future sessions
- Reset Configuration: Return to default settings
"""
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=('Courier', self.editor_font_size))
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_text_widget.insert("1.0", help_text)
        help_text_widget.configure(state="disabled")  # Make read-only
        
        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)

    def show_latex(self):
        """Show the generated LaTeX code in a window with copy functionality"""
        if not self.latex_content:
            # Generate LaTeX if not already generated
            markdown_content = self.editor.get("1.0", tk.END)
            self.latex_content = self.parser.parse(markdown_content)
        
        # Create a new window to display the LaTeX code
        latex_window = tk.Toplevel(self.root)
        latex_window.title("Generated LaTeX Code")
        latex_window.geometry("800x600")
        
        # Create a text widget to display the LaTeX code
        latex_text = scrolledtext.ScrolledText(latex_window, wrap=tk.WORD, font=('Courier', self.editor_font_size))
        latex_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insert the LaTeX code
        latex_text.insert("1.0", self.latex_content)
        
        # Create a button frame
        button_frame = ttk.Frame(latex_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add a copy button
        def copy_latex():
            latex_window.clipboard_clear()
            latex_window.clipboard_append(self.latex_content)
            self.status_var.set("LaTeX code copied to clipboard")
        
        copy_button = ttk.Button(button_frame, text="Copy to Clipboard", command=copy_latex)
        copy_button.pack(side=tk.LEFT, padx=5)
        
        # Add a close button
        close_button = ttk.Button(button_frame, text="Close", command=latex_window.destroy)
        close_button.pack(side=tk.RIGHT, padx=5)

    def update_preview(self):
        """Update the LaTeX preview"""
        try:
            # Update status
            self.status_var.set("Compiling LaTeX...")
            self.root.update_idletasks()  # Force update to show status
            
            # Get markdown content
            markdown_content = self.editor.get("1.0", tk.END)
            
            # Convert to LaTeX
            self.latex_content = self.parser.parse(markdown_content)
            
            # Create a temporary LaTeX file
            tex_file = os.path.join(self.temp_dir, "preview.tex")
            
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(self.latex_content)
            
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
                with open(os.path.join(self.temp_dir, "error_log.txt"), "w") as f:
                    f.write(error_log)
                messagebox.showerror("LaTeX Error", f"Failed to compile LaTeX.\n\nError details saved to {os.path.join(self.temp_dir, 'error_log.txt')}")
                return
            
            # Convert PDF to images and display
            pdf_path = os.path.join(self.temp_dir, "preview.pdf")
            self.pdf_path = pdf_path  # Store for zooming
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
            
            # Calculate DPI based on zoom level - use much higher base DPI
            zoom_level = self.zoom_var.get() / 100.0
            base_dpi = 300  # Higher base DPI for better quality
            effective_dpi = int(base_dpi * zoom_level)
            
            # Convert PDF to images at higher resolution for better readability
            images = convert_from_path(pdf_path, dpi=effective_dpi)
            
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
            
            # Update status with zoom level
            self.status_var.set(f"Preview updated at {self.zoom_var.get()}% zoom")
            
        except Exception as e:
            self.status_var.set(f"Display error: {str(e)}")
            messagebox.showerror("Display Error", str(e))

    def new_problem(self):
        """Create a new problem"""
        self.current_file = None
        self.title_entry.delete(0, tk.END)
        self.insert_template()
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
            self.editor.insert("1.0", problem_data.get("markdown_content", ""))
            
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
            self.problem_data["markdown_content"] = self.editor.get("1.0", tk.END)
            
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
            markdown_content = self.editor.get("1.0", tk.END)
            latex_content = self.parser.parse(markdown_content)
            
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
    app = ConfigurableProblemEditor(root)
    root.mainloop()