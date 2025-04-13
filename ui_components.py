"""
UI components for the Math Problem Editor.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from constants import HELP_TEXT

class ConfigDialog(tk.Toplevel):
    """Dialog for editing configuration settings"""
    
    def __init__(self, parent, config_manager, callback):
        """
        Initialize the configuration dialog
        
        Args:
            parent (tk.Tk): Parent window
            config_manager (ConfigManager): Configuration manager instance
            callback (function): Callback function to run when configuration is updated
        """
        super().__init__(parent)
        self.title("Edit Configuration")
        self.geometry("600x500")
        self.config_manager = config_manager
        self.callback = callback
        
        # Create a notebook for tabbed interface
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
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
    
    def create_fonts_tab(self):
        """Create the fonts configuration tab"""
        fonts_frame = ttk.Frame(self.notebook)
        self.notebook.add(fonts_frame, text="Fonts")
        
        # Configure grid
        fonts_frame.columnconfigure(1, weight=1)
        
        # Create entry fields for each font setting
        font_settings = self.config_manager.config["fonts"]
        row = 0
        
        self.font_vars = {}
        for key, value in font_settings.items():
            # Create a user-friendly label
            label_text = key.replace("_", " ").title()
            ttk.Label(fonts_frame, text=f"{label_text}:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
            
            # Create entry field with current value
            self.font_vars[key] = tk.StringVar(value=value)
            entry = ttk.Entry(fonts_frame, textvariable=self.font_vars[key])
            entry.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=5)
            
            row += 1
        
        # Add help text
        help_text = "Font sizes should be specified with units (e.g., 12pt, 14pt, 18pt)"
        ttk.Label(fonts_frame, text=help_text, foreground="gray").grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=15)
    
    def create_spacing_tab(self):
        """Create the spacing configuration tab"""
        spacing_frame = ttk.Frame(self.notebook)
        self.notebook.add(spacing_frame, text="Spacing")
        
        # Configure grid
        spacing_frame.columnconfigure(1, weight=1)
        
        # Create entry fields for each spacing setting
        spacing_settings = self.config_manager.config["spacing"]
        row = 0
        
        self.spacing_vars = {}
        for key, value in spacing_settings.items():
            # Create a user-friendly label
            label_text = key.replace("_", " ").title()
            ttk.Label(spacing_frame, text=f"{label_text}:").grid(
                row=row, column=0, sticky=tk.W, padx=10, pady=5)
            
            # Create entry field with current value
            self.spacing_vars[key] = tk.StringVar(value=value)
            entry = ttk.Entry(spacing_frame, textvariable=self.spacing_vars[key])
            entry.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=5)
            
            row += 1
        
        # Add help text
        help_text = "Line spacing should be a number (e.g., 1.5). \nOther spacing values should include units (e.g., 12pt, 1em)."
        ttk.Label(spacing_frame, text=help_text, foreground="gray").grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=15)
    
    def create_styling_tab(self):
        """Create the styling configuration tab"""
        styling_frame = ttk.Frame(self.notebook)
        self.notebook.add(styling_frame, text="Styling")
        
        # Configure grid
        styling_frame.columnconfigure(1, weight=1)
        
        # Create entry fields for each styling setting
        styling_settings = self.config_manager.config["styling"]
        row = 0
        
        self.styling_vars = {}
        for key, value in styling_settings.items():
            # Create a user-friendly label
            label_text = key.replace("_", " ").title()
            ttk.Label(styling_frame, text=f"{label_text}:").grid(
                row=row, column=0, sticky=tk.W, padx=10, pady=5)
            
            # Create entry field with current value
            self.styling_vars[key] = tk.StringVar(value=value)
            entry = ttk.Entry(styling_frame, textvariable=self.styling_vars[key])
            entry.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=5)
            
            row += 1
        
        # Add help text
        help_text = "Use #TEXT# as a placeholder for content.\nUse LaTeX commands for formatting (e.g., \\textbf{}, \\large, etc.)."
        ttk.Label(styling_frame, text=help_text, foreground="gray").grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=15)
    
    def create_margins_tab(self):
        """Create the margins configuration tab"""
        margins_frame = ttk.Frame(self.notebook)
        self.notebook.add(margins_frame, text="Margins")
        
        # Configure grid
        margins_frame.columnconfigure(1, weight=1)
        
        # Create entry fields for each margin setting
        margin_settings = self.config_manager.config["margins"]
        row = 0
        
        self.margin_vars = {}
        for key, value in margin_settings.items():
            # Create a user-friendly label
            label_text = key.title()
            ttk.Label(margins_frame, text=f"{label_text} Margin:").grid(
                row=row, column=0, sticky=tk.W, padx=10, pady=5)
            
            # Create entry field with current value
            self.margin_vars[key] = tk.StringVar(value=value)
            entry = ttk.Entry(margins_frame, textvariable=self.margin_vars[key])
            entry.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=5)
            
            row += 1
        
        # Add help text
        help_text = "Margin values should include units (e.g., 0.75in, 2cm, 25mm)."
        ttk.Label(margins_frame, text=help_text, foreground="gray").grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=15)
    
    def save_config(self):
        """Save configuration changes"""
        # Update configuration with values from entry fields
        for key, var in self.font_vars.items():
            self.config_manager.config["fonts"][key] = var.get()
            
        for key, var in self.spacing_vars.items():
            self.config_manager.config["spacing"][key] = var.get()
            
        for key, var in self.styling_vars.items():
            self.config_manager.config["styling"][key] = var.get()
            
        for key, var in self.margin_vars.items():
            self.config_manager.config["margins"][key] = var.get()
        
        # Call callback function with updated configuration
        self.callback(self.config_manager.config)
        
        # Close dialog
        self.destroy()


class LaTeXCodeViewer(tk.Toplevel):
    """Dialog to display and copy LaTeX code"""
    
    def __init__(self, parent, latex_content):
        """
        Initialize the LaTeX code viewer
        
        Args:
            parent (tk.Tk): Parent window
            latex_content (str): LaTeX content to display
        """
        super().__init__(parent)
        self.title("Generated LaTeX Code")
        self.geometry("800x600")
        self.latex_content = latex_content
        
        # Create text widget to display LaTeX code
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Text widget for LaTeX code
        self.text_widget = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, font=('Courier', 12))
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insert LaTeX code
        self.text_widget.insert("1.0", self.latex_content)
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Copy button
        copy_button = ttk.Button(
            button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_button.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_button = ttk.Button(
            button_frame, text="Close", command=self.destroy)
        close_button.pack(side=tk.RIGHT, padx=5)
    
    def copy_to_clipboard(self):
        """Copy LaTeX code to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(self.latex_content)


class HelpWindow(tk.Toplevel):
    """Dialog to display help information"""
    
    def __init__(self, parent):
        """
        Initialize the help window
        
        Args:
            parent (tk.Tk): Parent window
        """
        super().__init__(parent)
        self.title("Markdown Syntax Help")
        self.geometry("600x500")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create help dialog widgets"""
        # Text widget for help content
        self.text_widget = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, font=('Courier', 12))
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_widget.insert("1.0", HELP_TEXT)
        self.text_widget.configure(state="disabled")  # Make read-only
        
        # Close button
        close_button = ttk.Button(self, text="Close", command=self.destroy)
        close_button.pack(pady=10)