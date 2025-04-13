"""
Main editor implementation for the Math Problem Editor.
"""

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
from error_logger import ErrorLogger
from ui_components import ConfigDialog, LaTeXCodeViewer, HelpWindow
from constants import DEFAULT_TEMPLATE, TEMPLATES
import constants

class MathProblemEditor:
    """Main editor class for the Math Problem Editor application"""
    
    def __init__(self, root, config_manager, markdown_parser):
        """
        Initialize the editor
        
        Args:
            root (tk.Tk): Root window
            config_manager (ConfigManager): Configuration manager instance
            markdown_parser (MarkdownParser): Markdown parser instance
        """
        self.root = root
        self.root.title("Math Problem Editor")
        self.root.geometry("1200x700")
        
        # Store references to manager classes
        self.config_manager = config_manager
        self.markdown_parser = markdown_parser
        
        # Initialize error logger
        self.error_logger = ErrorLogger()
        
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
        
        # Initialize with the default zoom of 100% instead of 200%
        self.zoom_var = tk.IntVar(value=100)
        
        # Status variable
        self.status_var = tk.StringVar(value="Ready")
        
        # Create UI
        self.create_menu()
        self.create_layout()
        
        # Insert initial template
        self.insert_template()
        
        # After a short delay, position the sash to make the preview wider
        self.root.after(100, self.position_sash)
    
    def position_sash(self):
        """Position the divider between editor and preview"""
        try:
            window_width = self.root.winfo_width()
            if window_width > 100:
                # Position sash at 1/3 of the window width
                self.main_paned.sashpos(0, window_width // 3)
        except Exception as e:
            print(f"Error positioning sash: {e}")
    
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
        
        # Templates menu
        templates_menu = tk.Menu(menubar, tearoff=0)
        templates_menu.add_command(label="Basic Problem", command=self.insert_template)
        templates_menu.add_command(label="Two Equation Problem", command=self.insert_two_equation_template)
        templates_menu.add_command(label="Problem with Image", command=self.insert_image_template)
        templates_menu.add_separator()
        templates_menu.add_command(label="Create from Template...", command=self.create_from_template)
        
        # Add template types dynamically from constants
        if hasattr(constants, 'TEMPLATES') and constants.TEMPLATES:
            templates_menu.add_separator()
            for template_id, template in constants.TEMPLATES.items():
                if template_id not in ["one_equation", "two_equations", "text_image"]:  # Skip the ones we already added
                    templates_menu.add_command(
                        label=template["name"],
                        command=lambda tid=template_id: self.create_from_specific_template(tid)
                    )
        
        menubar.add_cascade(label="Templates", menu=templates_menu)
        
        # Insert menu
        insert_menu = tk.Menu(menubar, tearoff=0)
        insert_menu.add_command(label="Problem Section", command=self.insert_problem_section)
        insert_menu.add_command(label="Solution Section", command=self.insert_solution_section)
        insert_menu.add_command(label="Question", command=self.insert_question)
        insert_menu.add_separator()
        insert_menu.add_command(label="Equation", command=self.insert_equation)
        insert_menu.add_command(label="Aligned Equations", command=self.insert_aligned)
        
        menubar.add_cascade(label="Insert", menu=insert_menu)
        
        # Format menu
        format_menu = tk.Menu(menubar, tearoff=0)
        format_menu.add_command(label="Increase Font Size", command=self.increase_font_size)
        format_menu.add_command(label="Decrease Font Size", command=self.decrease_font_size)
        format_menu.add_separator()
        format_menu.add_command(label="Edit Configuration...", command=self.edit_configuration)
        format_menu.add_command(label="Save Configuration", command=self.save_configuration)
        format_menu.add_command(label="Reset to Default Configuration", command=self.reset_configuration)
        menubar.add_cascade(label="Format", menu=format_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Show LaTeX Code", command=self.show_latex_code)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Syntax Help", command=self.show_syntax_help)
        help_menu.add_command(label="Template Help", command=self.show_template_help)
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
        main_paned.add(preview_frame, weight=3)
        
        # Store the main_paned reference as an instance variable so we can access it later
        self.main_paned = main_paned
        
        # Title field
        title_frame = ttk.Frame(edit_frame)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_frame, text="Problem Title:", font=self.ui_font).pack(side=tk.LEFT)
        self.title_entry = ttk.Entry(title_frame, font=self.ui_font)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Using scrolledtext for the editor
        editor_frame = ttk.LabelFrame(edit_frame, text="Markdown Editor")
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.editor = scrolledtext.ScrolledText(
            editor_frame, wrap=tk.WORD, undo=True, font=self.editor_font)
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Status label for feedback
        status_label = ttk.Label(
            edit_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, font=self.ui_font)
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
        
        zoom_out = ttk.Button(preview_controls, text="-", width=2, command=self.zoom_out)
        zoom_out.pack(side=tk.LEFT)
        
        self.zoom_label = ttk.Label(preview_controls, textvariable=self.zoom_var, width=4)
        self.zoom_label.pack(side=tk.LEFT)
        ttk.Label(preview_controls, text="%").pack(side=tk.LEFT)
        
        zoom_in = ttk.Button(preview_controls, text="+", width=2, command=self.zoom_in)
        zoom_in.pack(side=tk.LEFT)
        
        # Preview scrollable area
        preview_canvas_frame = ttk.Frame(preview_frame)
        preview_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a canvas with scrollbar for preview
        self.preview_canvas = tk.Canvas(preview_canvas_frame, background="white")
        preview_scrollbar = ttk.Scrollbar(
            preview_canvas_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preview_canvas.configure(yscrollcommand=preview_scrollbar.set)
        
        # Frame inside canvas for preview content
        self.preview_frame = ttk.Frame(self.preview_canvas)
        self.preview_canvas.configure(background="white")
        self.canvas_window = self.preview_canvas.create_window(
            (0, 0), window=self.preview_frame, anchor=tk.NW)
        
        # Configure canvas when frame size changes
        self.preview_frame.bind("<Configure>", self.on_frame_configure)
        self.preview_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Store a reference to preview images to prevent garbage collection
        self.preview_images = []
        self.pdf_path = None  # Store the path to PDF for zooming
    
    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Adjust the width of the frame to fill the canvas"""
        canvas_width = event.width
        self.preview_canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def insert_template(self):
        """Insert initial template"""
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", DEFAULT_TEMPLATE)
    
    def insert_two_equation_template(self):
        """Insert a two equation problem template"""
        template = """#problem
Solve the system of equations:

#eq
3x + 2y = 12

#eq
x - y = 1

#question
Find the values of x and y.
"""
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", template)
    
    def insert_image_template(self):
        """Insert a problem with image template"""
        template = """#problem
Consider the triangle shown in the figure:

[Insert figure reference here]

#question
Calculate the area of the triangle.
"""
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", template)
    
    def create_from_template(self):
        """Create a problem from template dialog"""
        from template_dialog import TemplateDialog
        dialog = TemplateDialog(self.root, self.markdown_parser)
        self.root.wait_window(dialog)
        
        # If template was created, insert it
        if dialog.result:
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", dialog.result)
            self.status_var.set("Template inserted")
    
    def create_from_specific_template(self, template_id):
        """
        Create a problem from a specific template
        
        Args:
            template_id (str): Template identifier
        """
        from template_dialog import TemplateDialog
        
        dialog = TemplateDialog(self.root, self.markdown_parser)
        
        # Pre-select the template
        for i, template_name in enumerate(dialog.template_combo["values"]):
            if template_name == TEMPLATES[template_id]["name"]:
                dialog.template_combo.current(i)
                dialog.on_template_selected(None)
                break
        
        self.root.wait_window(dialog)
        
        # If template was created, insert it
        if dialog.result:
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", dialog.result)
            self.status_var.set(f"Template '{TEMPLATES[template_id]['name']}' inserted")
    
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
    
    def insert_aligned(self):
        """Insert an aligned equations marker"""
        self.editor.insert(tk.INSERT, "\n#align\n")
    
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
    
    def zoom_in(self):
        """Increase preview zoom level and regenerate preview"""
        if self.zoom_var.get() < 300:  # Limit maximum zoom to 300%
            # Use larger increments (25%) for more noticeable zoom changes
            self.zoom_var.set(self.zoom_var.get() + 25)
            # Force update of preview if PDF exists
            if self.pdf_path:
                # Actually regenerate the display at new zoom level
                self.display_pdf(self.pdf_path)
                self.status_var.set(f"Zoom: {self.zoom_var.get()}%")
    
    def zoom_out(self):
        """Decrease preview zoom level and regenerate preview"""
        if self.zoom_var.get() > 25:  # Prevent too small zoom
            # Use larger increments (25%) for more noticeable zoom changes
            self.zoom_var.set(self.zoom_var.get() - 25)
            # Force update of preview if PDF exists
            if self.pdf_path:
                # Actually regenerate the display at new zoom level
                self.display_pdf(self.pdf_path)
                self.status_var.set(f"Zoom: {self.zoom_var.get()}%")
    
    def edit_configuration(self):
        """Open the configuration dialog"""
        def config_callback(updated_config):
            """Handle updated configuration"""
            # Update preview to reflect changes
            self.update_preview()
        
        dialog = ConfigDialog(self.root, self.config_manager, config_callback)
        self.root.wait_window(dialog)
    
    def save_configuration(self):
        """Save the current configuration"""
        if self.config_manager.save_config():
            self.status_var.set("Configuration saved successfully")
        else:
            self.status_var.set("Failed to save configuration")
            messagebox.showerror("Error", "Failed to save configuration")
    
    def reset_configuration(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Reset Configuration", 
                              "Are you sure you want to reset all configuration to default values?"):
            if self.config_manager.reset_to_defaults():
                self.status_var.set("Configuration reset to defaults")
                # Update preview to reflect changes
                self.update_preview()
            else:
                self.status_var.set("Failed to reset configuration")
                messagebox.showerror("Error", "Failed to reset configuration")
    
    def show_latex_code(self):
        """Show the generated LaTeX code"""
        try:
            # Get current markdown content
            markdown_content = self.editor.get("1.0", tk.END)
            
            # Generate LaTeX
            latex_content = self.markdown_parser.parse(markdown_content)
            
            # Show the LaTeX code in a dialog
            latex_viewer = LaTeXCodeViewer(self.root, latex_content)
            self.root.wait_window(latex_viewer)
            
        except Exception as e:
            self.status_var.set(f"Error generating LaTeX: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate LaTeX: {str(e)}")
    
    def show_syntax_help(self):
        """Show help window with markdown syntax reference"""
        help_window = HelpWindow(self.root)
        self.root.wait_window(help_window)
    
    def show_template_help(self):
        """Show help about templates and slots"""
        help_text = """
# Template System Help

## Templates and Slots
The template system uses "slots" that you can fill with content. Each template has specific slots for:
- Introduction text
- Equations
- Questions
- Multiple choice options
- And more...

## Available Templates
- One Equation: Basic problem with a single equation
- Two Equations: Problem with a system of two equations
- Text with Image: Problem that includes an image reference
- Separated Question: Clear separation between given information and question
- Multi-part Question: Problem with multiple subquestions (a), (b), (c)
- Multiple Choice: Problem with multiple-choice answer options

## Creating from Templates
1. Select Templates → Create from Template
2. Choose a template type
3. Fill in the required slots
4. Click Preview to see the generated problem
5. Click Create to insert the problem into the editor

## Tips
- Required slots must be filled before creating the template
- Optional slots can be left empty
- You can preview the generated markdown before creating it
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Template System Help")
        help_window.geometry("600x500")
        
        help_frame = ttk.Frame(help_window, padding="10")
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        help_text_widget = scrolledtext.ScrolledText(help_frame, wrap=tk.WORD, font=('Arial', 12))
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_text_widget.insert("1.0", help_text)
        help_text_widget.configure(state="disabled")  # Make read-only
        
        close_button = ttk.Button(help_frame, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)
    
    def handle_latex_error(self, result, error_source="compile"):
        """
        Handle LaTeX compilation errors
        
        Args:
            result: Result from subprocess.run
            error_source (str): Source of the error (e.g., 'compile', 'preview')
            
        Returns:
            str: Path to the error log file
        """
        # Get error content
        error_log = result.stdout + "\n" + result.stderr
        
        # Log the error
        additional_info = f"Source: {error_source}\nReturn Code: {result.returncode}"
        log_file_path = self.error_logger.log_error("LaTeX", error_log, additional_info)
        
        # Update status
        self.status_var.set(f"LaTeX {error_source} failed")
        
        # Show error message
        messagebox.showerror(
            "LaTeX Error", 
            f"Failed to {error_source} LaTeX.\n\nError details saved to {log_file_path}"
        )
        
        return log_file_path
    
    def update_preview(self):
        """Update the LaTeX preview"""
        try:
            # Update status
            self.status_var.set("Compiling LaTeX...")
            self.root.update_idletasks()  # Force update to show status
            
            # Get markdown content
            markdown_content = self.editor.get("1.0", tk.END)
            
            # Convert to LaTeX
            latex_content = self.markdown_parser.parse(markdown_content)
            
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
                self.handle_latex_error(result, "compilation")
                return
            
            # Convert PDF to images and display
            pdf_path = os.path.join(self.temp_dir, "preview.pdf")
            self.pdf_path = pdf_path  # Store for zooming
            self.display_pdf(pdf_path)
            self.status_var.set(f"Preview updated (Zoom: {self.zoom_var.get()}%)")
            
        except Exception as e:
            self.status_var.set(f"Preview error: {str(e)}")
            messagebox.showerror("Error", f"Preview error: {str(e)}")
    
    def display_pdf(self, pdf_path):
        """
        Convert and display PDF preview
        
        Args:
            pdf_path (str): Path to the PDF file
        """
        try:
            # Clear previous preview
            for widget in self.preview_frame.winfo_children():
                widget.destroy()
            self.preview_images = []  # Clear image references
            
            # Increase PIL's maximum image pixels to avoid warnings
            Image.MAX_IMAGE_PIXELS = 1000000000  # 1 billion pixels
            
            # Calculate DPI based on zoom level
            zoom_level = self.zoom_var.get() / 100.0
            base_dpi = 300  # Higher base DPI for better clarity
            effective_dpi = int(base_dpi * zoom_level)
            
            # Limit the effective DPI to prevent memory issues
            max_dpi = 900
            if effective_dpi > max_dpi:
                self.status_var.set(f"Limiting DPI to {max_dpi} for performance reasons")
                effective_dpi = max_dpi
            
            # Make sure user knows processing is happening
            self.status_var.set(f"Rendering preview at {self.zoom_var.get()}% zoom...")
            self.root.update_idletasks()  # Update UI to show status
                
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=effective_dpi)
            
            # Display each page directly without resizing
            for i, img in enumerate(images):
                # Convert to PhotoImage with proper scaling
                photo = ImageTk.PhotoImage(img)
                self.preview_images.append(photo)  # Keep reference
                
                # Create label to display image
                img_label = ttk.Label(self.preview_frame, image=photo)
                img_label.pack(pady=10)
                
                # Add separator between pages
                if i < len(images) - 1:
                    ttk.Separator(self.preview_frame, orient=tk.HORIZONTAL).pack(
                        fill=tk.X, padx=20, pady=5)
        
            # Update canvas scroll region
            self.preview_canvas.update_idletasks()
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
            # Update status
            self.status_var.set(f"Preview updated (Zoom: {self.zoom_var.get()}%)")
            
        except Exception as e:
            self.status_var.set(f"Display error: {str(e)}")
            messagebox.showerror("Display Error", str(e))
    
    def new_problem(self):
        """Create a new problem"""
        if self.check_unsaved_changes():
            self.current_file = None
            self.title_entry.delete(0, tk.END)
            self.insert_template()
            self.status_var.set("New problem created")
    
    def check_unsaved_changes(self):
        """
        Check if there are unsaved changes and prompt the user
        
        Returns:
            bool: True if it's safe to proceed, False if the operation should be cancelled
        """
        if self.current_file:
            try:
                with open(self.current_file, 'r', encoding='utf-8') as file:
                    saved_data = json.load(file)
                
                # Check if content has changed
                current_title = self.title_entry.get()
                current_content = self.editor.get("1.0", tk.END)
                
                if (current_title != saved_data.get("title", "") or 
                    current_content != saved_data.get("markdown_content", "")):
                    # Prompt user about unsaved changes
                    answer = messagebox.askyesnocancel(
                        "Unsaved Changes", 
                        "There are unsaved changes. Would you like to save them?")
                    
                    if answer is None:  # Cancel
                        return False
                    elif answer:  # Yes, save
                        return self.save_problem()
                    else:  # No, don't save
                        return True
            except:
                pass
        
        return True
    
    def open_problem(self):
        """Open a problem file"""
        if not self.check_unsaved_changes():
            return
            
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
        """
        Save the current problem
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self.current_file:
            return self.save_problem_as()
            
        return self._save_to_file(self.current_file)
    
    def save_problem_as(self):
        """
        Save the problem to a new file
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        file_path = filedialog.asksaveasfilename(
            title="Save Problem As",
            defaultextension=".prob",
            filetypes=[("Problem files", "*.prob"), ("All files", "*.*")]
        )
        
        if not file_path:
            return False
            
        return self._save_to_file(file_path)
    
    def _save_to_file(self, file_path):
        """
        Save problem data to file
        
        Args:
            file_path (str): Path to save to
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
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
            latex_content = self.markdown_parser.parse(markdown_content)
            
            # Compile LaTeX to PDF
            self.status_var.set("Exporting to PDF...")
            tex_file = os.path.join(self.temp_dir, "export.tex")
            
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(latex_content)
            
            current_dir = os.getcwd()
            os.chdir(self.temp_dir)
            
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "export.tex"],
                capture_output=True,
                text=True
            )
            
            os.chdir(current_dir)
            
            if result.returncode != 0:
                self.handle_latex_error(result, "export")
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
        """
        Open a file with the default application
        
        Args:
            file_path (str): Path to the file to open
        """
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