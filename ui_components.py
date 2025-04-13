"""
UI components for the Math Problem Editor.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from constants import HELP_TEXT

class ConfigDialog(tk.Toplevel):
    """Dialog for editing configuration"""
    
    def __init__(self, parent, config_manager, callback=None):
        """
        Initialize the configuration dialog
        
        Args:
            parent: Parent window
            config_manager: Configuration manager instance
            callback: Callback function for when configuration is updated
        """
        super().__init__(parent)
        self.title("Edit Configuration")
        self.geometry("600x500")
        self.minsize(500, 400)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Store references
        self.config_manager = config_manager
        self.config = config_manager.config.copy()  # Work on a copy
        self.callback = callback
        
        # Create components
        self.create_widgets()
        
        # Center the dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
    def create_widgets(self):
        """Create the dialog widgets"""
        # Create tab control
        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=1, fill="both", padx=5, pady=5)
        
        # Create tabs
        self.create_fonts_tab()
        self.create_spacing_tab()
        self.create_styling_tab()
        self.create_margins_tab()
        self.create_custom_cmds_tab()
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ok_button = ttk.Button(button_frame, text="OK", command=self.on_ok)
        ok_button.pack(side="right", padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="right", padx=5)
        
        apply_button = ttk.Button(button_frame, text="Apply", command=self.on_apply)
        apply_button.pack(side="right", padx=5)
    
    def create_fonts_tab(self):
        """Create the fonts configuration tab"""
        fonts_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(fonts_frame, text="Fonts")
        
        # Create a scrollable frame
        canvas = tk.Canvas(fonts_frame, borderwidth=0)
        scrollbar = ttk.Scrollbar(fonts_frame, orient="vertical", command=canvas.yview)
        inner_frame = ttk.Frame(canvas)
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create window inside canvas
        canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        inner_frame.bind("<Configure>", configure_scroll_region)
        
        def resize_canvas_window(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", resize_canvas_window)
        
        # Base font size
        row = 0
        ttk.Label(inner_frame, text="Base Font Size:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        base_size_var = tk.StringVar(value=self.config["fonts"]["base_font_size"])
        base_size_combo = ttk.Combobox(inner_frame, textvariable=base_size_var, width=10)
        base_size_combo["values"] = ("6pt", "8pt", "10pt", "12pt", "14pt", "17pt", "20pt")
        base_size_combo.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        def update_base_size(*args):
            self.config["fonts"]["base_font_size"] = base_size_var.get()
        
        base_size_var.trace("w", update_base_size)
        
        # Global scale
        row += 1
        ttk.Label(inner_frame, text="Global Scale:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        global_scale_var = tk.DoubleVar(value=float(self.config["fonts"]["global_scale"]))
        global_scale = ttk.Scale(inner_frame, from_=0.5, to=1.5, variable=global_scale_var, length=200)
        global_scale.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        scale_label = ttk.Label(inner_frame, text=f"{global_scale_var.get():.1f}")
        scale_label.grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        
        def update_global_scale(*args):
            self.config["fonts"]["global_scale"] = f"{global_scale_var.get():.1f}"
            scale_label.config(text=f"{global_scale_var.get():.1f}")
        
        global_scale_var.trace("w", update_global_scale)
        
        # Problem header scale
        row += 1
        ttk.Label(inner_frame, text="Problem Header Scale:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        header_scale_var = tk.DoubleVar(value=float(self.config["fonts"]["problem_header_scale"]))
        header_scale = ttk.Scale(inner_frame, from_=1.0, to=2.0, variable=header_scale_var, length=200)
        header_scale.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        header_label = ttk.Label(inner_frame, text=f"{header_scale_var.get():.1f}")
        header_label.grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        
        def update_header_scale(*args):
            self.config["fonts"]["problem_header_scale"] = f"{header_scale_var.get():.1f}"
            header_label.config(text=f"{header_scale_var.get():.1f}")
        
        header_scale_var.trace("w", update_header_scale)
        
        # Question scale
        row += 1
        ttk.Label(inner_frame, text="Question Scale:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        question_scale_var = tk.DoubleVar(value=float(self.config["fonts"]["question_scale"]))
        question_scale = ttk.Scale(inner_frame, from_=1.0, to=2.0, variable=question_scale_var, length=200)
        question_scale.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        question_label = ttk.Label(inner_frame, text=f"{question_scale_var.get():.1f}")
        question_label.grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        
        def update_question_scale(*args):
            self.config["fonts"]["question_scale"] = f"{question_scale_var.get():.1f}"
            question_label.config(text=f"{question_scale_var.get():.1f}")
        
        question_scale_var.trace("w", update_question_scale)
        
        # Equation scale
        row += 1
        ttk.Label(inner_frame, text="Equation Scale:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        equation_scale_var = tk.DoubleVar(value=float(self.config["fonts"]["equation_scale"]))
        equation_scale = ttk.Scale(inner_frame, from_=1.0, to=2.0, variable=equation_scale_var, length=200)
        equation_scale.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        equation_label = ttk.Label(inner_frame, text=f"{equation_scale_var.get():.1f}")
        equation_label.grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        
        def update_equation_scale(*args):
            self.config["fonts"]["equation_scale"] = f"{equation_scale_var.get():.1f}"
            equation_label.config(text=f"{equation_scale_var.get():.1f}")
        
        equation_scale_var.trace("w", update_equation_scale)
        
        # Help text
        row += 1
        help_text = "Adjust font sizes and scaling factors for different elements.\n" \
                    "Base size affects the overall text size, while scale factors affect relative sizes."
        ttk.Label(inner_frame, text=help_text, foreground="gray").grid(
            row=row, column=0, columnspan=3, sticky=tk.W, padx=10, pady=15)
    
    def create_spacing_tab(self):
        """Create the spacing configuration tab"""
        spacing_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(spacing_frame, text="Spacing")
        
        # Line spacing
        row = 0
        ttk.Label(spacing_frame, text="Line Spacing:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        line_spacing_var = tk.StringVar(value=self.config["spacing"]["line_spacing"])
        line_spacing_entry = ttk.Entry(spacing_frame, textvariable=line_spacing_var, width=10)
        line_spacing_entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        def update_line_spacing(*args):
            self.config["spacing"]["line_spacing"] = line_spacing_var.get()
        
        line_spacing_var.trace("w", update_line_spacing)
        
        # Spacing above equation
        row += 1
        ttk.Label(spacing_frame, text="Above Equation:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        above_eq_var = tk.StringVar(value=self.config["spacing"]["above_equation"])
        above_eq_entry = ttk.Entry(spacing_frame, textvariable=above_eq_var, width=10)
        above_eq_entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        def update_above_eq(*args):
            self.config["spacing"]["above_equation"] = above_eq_var.get()
        
        above_eq_var.trace("w", update_above_eq)
        
        # Spacing below equation
        row += 1
        ttk.Label(spacing_frame, text="Below Equation:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        below_eq_var = tk.StringVar(value=self.config["spacing"]["below_equation"])
        below_eq_entry = ttk.Entry(spacing_frame, textvariable=below_eq_var, width=10)
        below_eq_entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        def update_below_eq(*args):
            self.config["spacing"]["below_equation"] = below_eq_var.get()
        
        below_eq_var.trace("w", update_below_eq)
        
        # Paragraph spacing
        row += 1
        ttk.Label(spacing_frame, text="Paragraph Spacing:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        para_spacing_var = tk.StringVar(value=self.config["spacing"]["paragraph_spacing"])
        para_spacing_entry = ttk.Entry(spacing_frame, textvariable=para_spacing_var, width=10)
        para_spacing_entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        def update_para_spacing(*args):
            self.config["spacing"]["paragraph_spacing"] = para_spacing_var.get()
        
        para_spacing_var.trace("w", update_para_spacing)
        
        # Help text
        row += 1
        help_text = "Enter spacing values in points (pt) or other LaTeX units.\n" \
                    "Examples: 12pt, 0.5in, 1em"
        ttk.Label(spacing_frame, text=help_text, foreground="gray").grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=15)
    
    def create_styling_tab(self):
        """Create the styling configuration tab"""
        styling_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(styling_frame, text="Styling")
        
        # Question format
        row = 0
        ttk.Label(styling_frame, text="Question Format:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        question_format_var = tk.StringVar(value=self.config["styling"]["question_format"])
        question_format_entry = ttk.Entry(styling_frame, textvariable=question_format_var, width=40)
        question_format_entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        def update_question_format(*args):
            self.config["styling"]["question_format"] = question_format_var.get()
        
        question_format_var.trace("w", update_question_format)
        
        # Problem format
        row += 1
        ttk.Label(styling_frame, text="Problem Format:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        problem_format_var = tk.StringVar(value=self.config["styling"]["problem_format"])
        problem_format_entry = ttk.Entry(styling_frame, textvariable=problem_format_var, width=40)
        problem_format_entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        def update_problem_format(*args):
            self.config["styling"]["problem_format"] = problem_format_var.get()
        
        problem_format_var.trace("w", update_problem_format)
        
        # Help text
        row += 1
        help_text = "Use #TEXT# as a placeholder for content.\n" \
                    "Leave just '#TEXT#' to show questions without any prefix.\n" \
                    "Use LaTeX commands for formatting (e.g., \\textbf{}, \\large, etc.)."
        ttk.Label(styling_frame, text=help_text, foreground="gray").grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=15)
    
    def create_margins_tab(self):
        """Create the margins configuration tab"""
        margins_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(margins_frame, text="Margins")
        
        # Top margin
        row = 0
        ttk.Label(margins_frame, text="Top Margin:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        top_margin_var = tk.StringVar(value=self.config["margins"]["top"])
        top_margin_entry = ttk.Entry(margins_frame, textvariable=top_margin_var, width=10)
        top_margin_entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        def update_top_margin(*args):
            self.config["margins"]["top"] = top_margin_var.get()
        
        top_margin_var.trace("w", update_top_margin)
        
        # Right margin
        row += 1
        ttk.Label(margins_frame, text="Right Margin:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        right_margin_var = tk.StringVar(value=self.config["margins"]["right"])
        right_margin_entry = ttk.Entry(margins_frame, textvariable=right_margin_var, width=10)
        right_margin_entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        def update_right_margin(*args):
            self.config["margins"]["right"] = right_margin_var.get()
        
        right_margin_var.trace("w", update_right_margin)
        
        # Bottom margin
        row += 1
        ttk.Label(margins_frame, text="Bottom Margin:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        bottom_margin_var = tk.StringVar(value=self.config["margins"]["bottom"])
        bottom_margin_entry = ttk.Entry(margins_frame, textvariable=bottom_margin_var, width=10)
        bottom_margin_entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        def update_bottom_margin(*args):
            self.config["margins"]["bottom"] = bottom_margin_var.get()
        
        bottom_margin_var.trace("w", update_bottom_margin)
        
        # Left margin
        row += 1
        ttk.Label(margins_frame, text="Left Margin:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        
        left_margin_var = tk.StringVar(value=self.config["margins"]["left"])
        left_margin_entry = ttk.Entry(margins_frame, textvariable=left_margin_var, width=10)
        left_margin_entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        
        def update_left_margin(*args):
            self.config["margins"]["left"] = left_margin_var.get()
        
        left_margin_var.trace("w", update_left_margin)
        
        # Help text
        row += 1
        help_text = "Enter margin values in LaTeX units.\n" \
                    "Examples: 0.5in, 1cm, 20pt"
        ttk.Label(margins_frame, text=help_text, foreground="gray").grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=15)
    
    def create_custom_cmds_tab(self):
        """Create the custom commands configuration tab"""
        cmds_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(cmds_frame, text="Custom Commands")
        
        # Create a scrollable frame
        canvas = tk.Canvas(cmds_frame, borderwidth=0)
        scrollbar = ttk.Scrollbar(cmds_frame, orient="vertical", command=canvas.yview)
        inner_frame = ttk.Frame(canvas)
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create window inside canvas
        canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        inner_frame.bind("<Configure>", configure_scroll_region)
        
        def resize_canvas_window(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", resize_canvas_window)
        
        # Header
        row = 0
        ttk.Label(inner_frame, text="Command").grid(row=row, column=0, padx=10, pady=5)
        ttk.Label(inner_frame, text="LaTeX Replacement").grid(row=row, column=1, padx=10, pady=5)
        
        # Custom commands
        row += 1
        entries = []
        for cmd, replacement in self.config["custom_commands"].items():
            ttk.Label(inner_frame, text=cmd).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
            
            var = tk.StringVar(value=replacement)
            entry = ttk.Entry(inner_frame, textvariable=var, width=40)
            entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
            
            # Create a closure to keep the correct command
            def make_update_func(command):
                def update_command(*args):
                    self.config["custom_commands"][command] = var.get()
                return update_command
            
            var.trace("w", make_update_func(cmd))
            entries.append((cmd, var))
            row += 1
        
        # Help text
        help_text = "Define custom LaTeX replacements for markdown commands.\n" \
                    "Use #TEXT# as a placeholder for content that follows the command."
        ttk.Label(inner_frame, text=help_text, foreground="gray").grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=15)
    
    def on_apply(self):
        """Apply the configuration changes"""
        # Update the config manager with the new config
        self.config_manager.config = self.config.copy()
        
        # If a callback is defined, call it
        if self.callback:
            self.callback(self.config)
    
    def on_ok(self):
        """Apply changes and close dialog"""
        self.on_apply()
        self.destroy()

class LaTeXCodeViewer(tk.Toplevel):
    """Dialog for viewing LaTeX code"""
    
    def __init__(self, parent, latex_content):
        """
        Initialize the LaTeX code viewer
        
        Args:
            parent: Parent window
            latex_content (str): LaTeX code to display
        """
        super().__init__(parent)
        self.title("LaTeX Code")
        self.geometry("800x600")
        self.minsize(600, 400)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Store content
        self.latex_content = latex_content
        
        # Create components
        self.create_widgets()
        
        # Center the dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        """Create the dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Text widget
        text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Courier", 12))
        text_widget.pack(fill="both", expand=True)
        
        # Insert LaTeX content
        text_widget.insert("1.0", self.latex_content)
        text_widget.configure(state="disabled")  # Make read-only
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Copy button
        copy_button = ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_button.pack(side="left", padx=5)
        
        # Close button
        close_button = ttk.Button(button_frame, text="Close", command=self.destroy)
        close_button.pack(side="right", padx=5)
    
    def copy_to_clipboard(self):
        """Copy LaTeX content to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(self.latex_content)
        
        # Show confirmation
        label = ttk.Label(self, text="Copied to clipboard!", foreground="green")
        label.pack(pady=5)
        
        # Auto-hide the label after 2 seconds
        label.after(2000, label.destroy)

class HelpWindow(tk.Toplevel):
    """Window for showing markdown syntax help"""
    
    def __init__(self, parent):
        """
        Initialize the help window
        
        Args:
            parent: Parent window
        """
        super().__init__(parent)
        self.title("Markdown Syntax Help")
        self.geometry("700x500")
        self.minsize(600, 400)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create components
        self.create_widgets()
        
        # Center the dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        """Create the dialog widgets"""
        # Help text widget
        help_text_widget = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Courier", 12))
        help_text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Insert help text
        help_text_widget.insert("1.0", HELP_TEXT)
        help_text_widget.configure(state="disabled")  # Make read-only
        
        # Close button
        close_button = ttk.Button(self, text="Close", command=self.destroy)
        close_button.pack(pady=10)

class TemplateDialog(tk.Toplevel):
    """Dialog for creating a problem from template"""
    
    def __init__(self, parent, markdown_parser):
        """
        Initialize the template dialog
        
        Args:
            parent: Parent window
            markdown_parser: Markdown parser instance
        """
        super().__init__(parent)
        self.title("Create from Template")
        self.geometry("600x500")
        self.minsize(500, 400)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Store references
        self.markdown_parser = markdown_parser
        self.result = None  # Will store the result
        
        # Create components
        self.create_widgets()
        
        # Center the dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        """Create the dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        row = 0
        ttk.Label(main_frame, text="Title:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=40)
        title_entry.grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Description
        row += 1
        ttk.Label(main_frame, text="Description:").grid(row=row, column=0, sticky=tk.NW, padx=5, pady=5)
        
        self.description_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=40, height=5)
        self.description_text.grid(row=row, column=1, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        # Equations
        row += 1
        ttk.Label(main_frame, text="Equations:").grid(row=row, column=0, sticky=tk.NW, padx=5, pady=5)
        
        self.equations_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=40, height=5)
        self.equations_text.grid(row=row, column=1, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        # Question
        row += 1
        ttk.Label(main_frame, text="Question:").grid(row=row, column=0, sticky=tk.NW, padx=5, pady=5)
        
        self.question_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=40, height=3)
        self.question_text.grid(row=row, column=1, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        # Configure grid rows and columns
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        create_button = ttk.Button(button_frame, text="Create", command=self.on_create)
        create_button.pack(side="right", padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="right", padx=5)
    
    def on_create(self):
        """Create the problem from template"""
        # Get values
        title = self.title_var.get()
        description = self.description_text.get("1.0", tk.END).strip()
        equations = self.equations_text.get("1.0", tk.END).strip()
        question = self.question_text.get("1.0", tk.END).strip()
        
        # Validate
        if not title:
            tk.messagebox.showerror("Error", "Title is required")
            return
        
        if not question:
            tk.messagebox.showerror("Error", "Question is required")
            return
        
        # Create problem from template
        try:
            self.result = self.markdown_parser.create_problem_from_template(
                title, description, equations, question)
            self.destroy()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to create problem: {str(e)}")