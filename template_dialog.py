"""
Template dialog UI component for the Math Problem Editor.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re
from constants import TEMPLATES, SLOT_TYPES

class TemplateDialog(tk.Toplevel):
    """Dialog for creating problems from templates with slots"""
    
    def __init__(self, parent, markdown_parser):
        """
        Initialize the template dialog
        
        Args:
            parent: Parent window
            markdown_parser: The markdown parser instance for generating content
        """
        super().__init__(parent)
        self.title("Create from Template")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Store references
        self.parent = parent
        self.markdown_parser = markdown_parser
        
        # Initialize result
        self.result = None
        
        # Create UI
        self.create_widgets()
        
        # Center the dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
        # Focus the dialog
        self.focus_set()
    
    def create_widgets(self):
        """Create the dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Template selection
        template_frame = ttk.LabelFrame(main_frame, text="Select Template", padding="10")
        template_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Template combobox
        self.template_var = tk.StringVar()
        templates = list(TEMPLATES.keys())
        template_names = [TEMPLATES[t]["name"] for t in templates]
        
        template_label = ttk.Label(template_frame, text="Template Type:")
        template_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.template_combo = ttk.Combobox(
            template_frame, textvariable=self.template_var, values=template_names, state="readonly")
        self.template_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        self.template_combo.current(0)  # Select first template by default
        self.template_combo.bind("<<ComboboxSelected>>", self.on_template_selected)
        
        # Template description
        self.desc_var = tk.StringVar()
        desc_label = ttk.Label(template_frame, textvariable=self.desc_var, wraplength=600, justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=10)
        
        # Create a scrollable frame for slots
        self.canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        # Configure slots frame inside canvas for scrolling
        self.slots_frame = ttk.LabelFrame(self.canvas, text="Fill Template Slots", padding="10")
        
        # Configure canvas to scroll
        self.slots_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.slots_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Ensure canvas window resizes with canvas
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        # Preview button
        preview_button = ttk.Button(main_frame, text="Preview", command=self.preview_template)
        preview_button.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.RIGHT, padx=5, pady=10)
        
        create_button = ttk.Button(button_frame, text="Create", command=self.create_template)
        create_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Initialize with the first template
        self.slot_widgets = []
        self.on_template_selected(None)
    
    def on_canvas_resize(self, event):
        """Resize the canvas window when canvas changes size"""
        width = event.width
        self.canvas.itemconfig(self.canvas_window, width=width)
    
    def on_template_selected(self, event):
        """
        Handle template selection
        
        Args:
            event: ComboboxSelected event
        """
        # Get selected template name
        template_name = self.template_combo.get()
        
        # Find template id from name
        template_id = None
        for tid, template in TEMPLATES.items():
            if template["name"] == template_name:
                template_id = tid
                break
        
        if not template_id:
            return
        
        # Update description
        template = TEMPLATES[template_id]
        self.desc_var.set(template["description"])
        
        # Clear existing slot widgets
        for widget in self.slot_widgets:
            widget.destroy()
        self.slot_widgets = []
        
        # Create new slot widgets based on template
        self.create_slot_widgets(template_id, template)
    
    def create_slot_widgets(self, template_id, template):
        """
        Create widgets for each slot in the template
        
        Args:
            template_id: Template identifier
            template: Template definition
        """
        # Store references
        self.current_template_id = template_id
        self.current_template = template
        
        # Create widgets for each slot
        for i, slot in enumerate(template["slots"]):
            # Frame for this slot
            slot_frame = ttk.LabelFrame(
                self.slots_frame, 
                text=f"{slot['name']} ({'Optional' if 'optional' in slot and slot['optional'] else 'Required'})"
            )
            slot_frame.pack(fill=tk.X, padx=5, pady=5)
            self.slot_widgets.append(slot_frame)
            
            # Widget depends on slot type
            if slot["type"] == "text":
                label = ttk.Label(slot_frame, text=f"{slot['name']}:")
                label.pack(anchor=tk.W, padx=5, pady=5)
                
                text_box = scrolledtext.ScrolledText(slot_frame, wrap=tk.WORD, height=3)
                text_box.pack(fill=tk.X, padx=5, pady=5)
                
                # Store reference
                slot_frame.widget = text_box
                
            elif slot["type"] == "equation":
                label = ttk.Label(slot_frame, text=f"{slot['name']}:")
                label.pack(anchor=tk.W, padx=5, pady=5)
                
                eq_box = ttk.Entry(slot_frame, width=50)
                eq_box.pack(fill=tk.X, padx=5, pady=5)
                
                # Help text
                help_label = ttk.Label(
                    slot_frame, 
                    text="Enter the equation without LaTeX delimiters.\nExample: 2x + 3 = 7", 
                    foreground="gray"
                )
                help_label.pack(anchor=tk.W, padx=5, pady=2)
                
                # Store reference
                slot_frame.widget = eq_box
                
            elif slot["type"] == "aligned_equations":
                label = ttk.Label(slot_frame, text=f"{slot['name']}:")
                label.pack(anchor=tk.W, padx=5, pady=5)
                
                eq_box = scrolledtext.ScrolledText(slot_frame, wrap=tk.WORD, height=3)
                eq_box.pack(fill=tk.X, padx=5, pady=5)
                
                # Help text
                help_label = ttk.Label(
                    slot_frame, 
                    text="Enter aligned equations, one per line.\nExample: x + y &= 5 \\\\ x - y &= 3", 
                    foreground="gray"
                )
                help_label.pack(anchor=tk.W, padx=5, pady=2)
                
                # Store reference
                slot_frame.widget = eq_box
                
            elif slot["type"] == "question":
                label = ttk.Label(slot_frame, text=f"{slot['name']}:")
                label.pack(anchor=tk.W, padx=5, pady=5)
                
                q_box = ttk.Entry(slot_frame, width=50)
                q_box.pack(fill=tk.X, padx=5, pady=5)
                
                # Store reference
                slot_frame.widget = q_box
                
            elif slot["type"] == "image":
                label = ttk.Label(slot_frame, text=f"{slot['name']}:")
                label.pack(anchor=tk.W, padx=5, pady=5)
                
                img_box = ttk.Entry(slot_frame, width=50)
                img_box.pack(fill=tk.X, padx=5, pady=5)
                
                # Help text
                help_label = ttk.Label(
                    slot_frame, 
                    text="Enter a reference or placeholder for the image.", 
                    foreground="gray"
                )
                help_label.pack(anchor=tk.W, padx=5, pady=2)
                
                # Store reference
                slot_frame.widget = img_box
                
            elif slot["type"] == "multi_choice":
                label = ttk.Label(slot_frame, text=f"{slot['name']}:")
                label.pack(anchor=tk.W, padx=5, pady=5)
                
                options_frame = ttk.Frame(slot_frame)
                options_frame.pack(fill=tk.X, padx=5, pady=5)
                
                # Create entries for each option
                option_entries = []
                for j in range(5):  # A through E
                    option_frame = ttk.Frame(options_frame)
                    option_frame.pack(fill=tk.X, pady=2)
                    
                    option_label = ttk.Label(option_frame, text=f"Option {chr(65+j)}:")
                    option_label.pack(side=tk.LEFT, padx=5)
                    
                    option_entry = ttk.Entry(option_frame, width=40)
                    option_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
                    
                    option_entries.append(option_entry)
                
                # Store references
                slot_frame.widget = option_entries
        
        # Update canvas scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def get_slot_values(self):
        """
        Get the values from all slot widgets
        
        Returns:
            dict: Dictionary mapping slot ids to their values
            str: Error message if validation fails, None otherwise
        """
        values = {}
        
        # Iterate through slots and corresponding widgets
        for i, slot in enumerate(self.current_template["slots"]):
            slot_id = slot["id"]
            widget_frame = self.slot_widgets[i]
            widget = widget_frame.widget
            
            # Get value based on widget type
            if slot["type"] in ["text", "aligned_equations"]:
                # Text box
                value = widget.get("1.0", tk.END).strip()
            elif slot["type"] in ["equation", "question", "image"]:
                # Entry
                value = widget.get().strip()
            elif slot["type"] == "multi_choice":
                # Multiple entries
                value = [entry.get().strip() for entry in widget]
            else:
                value = ""
            
            # Check required fields
            if "required" in slot and slot["required"] and not value:
                return None, f"The {slot['name']} field is required."
            
            values[slot_id] = value
        
        return values, None
    
    def preview_template(self):
        """Show a preview of the generated markdown"""
        # Get values from slots
        values, error = self.get_slot_values()
        if error:
            messagebox.showerror("Required Field Missing", error)
            return
        
        # Generate markdown
        markdown = self.generate_markdown(values)
        
        # Show preview
        preview_window = tk.Toplevel(self)
        preview_window.title("Template Preview")
        preview_window.geometry("600x400")
        
        preview_frame = ttk.Frame(preview_window, padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD)
        preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        preview_text.insert("1.0", markdown)
        preview_text.config(state=tk.DISABLED)
        
        close_button = ttk.Button(preview_frame, text="Close", command=preview_window.destroy)
        close_button.pack(pady=10)
    
    def generate_markdown(self, values):
        """
        Generate markdown from template and slot values
        
        Args:
            values: Dictionary of slot values
            
        Returns:
            str: The generated markdown
        """
        # Start with the template
        template = self.current_template["markdown_template"]
        
        # Replace each placeholder with its value
        for slot_id, value in values.items():
            placeholder = f"#{slot_id.upper()}#"
            
            # Special handling for optional parts with wrappers
            wrap_start = f"#{slot_id.upper()}_WRAP_START#"
            wrap_end = f"#{slot_id.upper()}_WRAP_END#"
            
            if wrap_start in template and wrap_end in template:
                # If the value is empty, remove the wrapped section
                if not value:
                    pattern = f"{wrap_start}.*?{wrap_end}"
                    template = re.sub(pattern, "", template, flags=re.DOTALL)
                else:
                    # Otherwise, replace the placeholders
                    template = template.replace(wrap_start, "")
                    template = template.replace(wrap_end, "")
                    template = template.replace(placeholder, value)
            else:
                # Regular replacement
                template = template.replace(placeholder, value if value else "")
        
        return template
    
    def create_template(self):
        """Create the template and close the dialog"""
        # Get values from slots
        values, error = self.get_slot_values()
        if error:
            messagebox.showerror("Required Field Missing", error)
            return
        
        # Generate markdown
        self.result = self.generate_markdown(values)
        
        # Close dialog
        self.destroy()
    
    def cancel(self):
        """Cancel and close the dialog"""
        self.result = None
        self.destroy()