"""
Custom markdown parser for the Math Problem Editor with improved template support.
"""

import re
from constants import TEMPLATES, generate_latex_template

class MarkdownParser:
    """Converts custom markdown to LaTeX with configurable formatting"""
    
    def __init__(self, config_manager):
        """
        Initialize the markdown parser
        
        Args:
            config_manager (ConfigManager): Configuration manager instance
        """
        self.config_manager = config_manager
    
    def parse(self, markdown_text):
        """
        Convert markdown to LaTeX using current configuration
        
        Args:
            markdown_text (str): Markdown content to convert
            
        Returns:
            str: Generated LaTeX document
        """
        # Get configuration values
        config = self.config_manager.config
        
        # Generate a LaTeX template based on current configuration
        latex_template = generate_latex_template(config)
        
        # Process markdown to convert to LaTeX - line by line approach
        lines = markdown_text.strip().split('\n')
        latex_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Handle problem section
            if line == "#problem":
                latex_lines.append("\\problemheader{}")
                i += 1
                continue
            
            # Handle solution section
            elif line == "#solution":
                latex_lines.append("\\problemheader{Solution}")
                i += 1
                continue
            
            # Handle equation
            elif line == "#eq":
                # Add spacing above equation
                latex_lines.append("\\vspace{" + config["spacing"]["above_equation"] + "}")
                
                # Begin equation environment
                latex_lines.append("\\begin{equation}")
                
                # Move to the next line (which should contain the equation)
                i += 1
                if i < len(lines) and not lines[i].strip().startswith('#'):
                    # Add the equation content
                    latex_lines.append(lines[i].strip())
                
                # End equation environment
                latex_lines.append("\\end{equation}")
                
                # Add spacing below equation
                latex_lines.append("\\vspace{" + config["spacing"]["below_equation"] + "}")
                
                i += 1
                continue
            
            # Handle align environment
            elif line == "#align":
                # Add spacing above align
                latex_lines.append("\\vspace{" + config["spacing"]["above_equation"] + "}")
                
                # Begin align environment
                latex_lines.append("\\begin{align}")
                
                # Collect align content lines
                align_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('#'):
                    if lines[i].strip():  # Only add non-empty lines
                        align_lines.append(lines[i].strip())
                    i += 1
                
                # Add align content with line breaks
                if align_lines:
                    latex_lines.append(" \\\\ ".join(align_lines))
                
                # End align environment
                latex_lines.append("\\end{align}")
                
                # Add spacing below align
                latex_lines.append("\\vspace{" + config["spacing"]["below_equation"] + "}")
                
                continue  # Don't increment i since we already moved to the next marker
            
            # Handle question without "Question:" prefix
            elif line == "#question":
                # Get question text
                i += 1
                if i < len(lines):
                    question_text = lines[i].strip()
                    
                    # Format according to configuration
                    question_format = config["styling"]["question_format"]
                    formatted_question = question_format.replace("#TEXT#", question_text)
                    
                    # Add to LaTeX lines
                    latex_lines.append("\\vspace{1em}")  # Add some space before question
                    latex_lines.append(formatted_question)
                
                i += 1
                continue
            
            # Regular text - just add it
            else:
                latex_lines.append(line)
                i += 1
        
        # Combine all LaTeX lines
        content = '\n'.join(latex_lines)
        
        # Replace placeholders in the document template
        document = latex_template
        document = document.replace("#TOP#", config["margins"]["top"])
        document = document.replace("#RIGHT#", config["margins"]["right"])
        document = document.replace("#BOTTOM#", config["margins"]["bottom"])
        document = document.replace("#LEFT#", config["margins"]["left"])
        document = document.replace("#LINESPACING#", config["spacing"]["line_spacing"])
        document = document.replace("#CONTENT#", content)
        
        return document
    
    def create_problem_from_template(self, template_id, slot_values):
        """
        Create a problem using a template and values
        
        Args:
            template_id (str): Template identifier
            slot_values (dict): Values for template slots
            
        Returns:
            str: Generated problem markdown
        """
        if template_id not in TEMPLATES:
            return "Error: Template not found"
        
        template = TEMPLATES[template_id]
        markdown_template = template["markdown_template"]
        
        # Replace each placeholder with its value
        for slot in template["slots"]:
            slot_id = slot["id"]
            value = slot_values.get(slot_id, "")
            
            # Handle empty optional slots
            if not value and "optional" in slot and slot["optional"]:
                # Remove optional sections
                wrap_start = f"#{slot_id.upper()}_WRAP_START#"
                wrap_end = f"#{slot_id.upper()}_WRAP_END#"
                
                if wrap_start in markdown_template and wrap_end in markdown_template:
                    pattern = f"{wrap_start}.*?{wrap_end}"
                    markdown_template = re.sub(pattern, "", markdown_template, flags=re.DOTALL)
            else:
                # Replace the placeholder
                placeholder = f"#{slot_id.upper()}#"
                markdown_template = markdown_template.replace(placeholder, value)
                
                # Remove any wrapper markers
                wrap_start = f"#{slot_id.upper()}_WRAP_START#"
                wrap_end = f"#{slot_id.upper()}_WRAP_END#"
                markdown_template = markdown_template.replace(wrap_start, "")
                markdown_template = markdown_template.replace(wrap_end, "")
        
        return markdown_template