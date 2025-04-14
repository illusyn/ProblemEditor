"""
Custom markdown parser for the Math Problem Editor with dynamic templates.
"""

import re
from constants import PROBLEM_TEMPLATE, EQUATION_SLOT, ALIGNED_EQUATIONS_SLOT, QUESTION_SLOT
import constants

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
        
        # Extract font settings from configuration
        base_font_size = config["fonts"]["base_font_size"]  # e.g. "12pt"
        global_scale = float(config["fonts"]["global_scale"])  # e.g. "1.0"
        
        # Calculate effective font size (strip 'pt' and multiply by scale)
        font_size_value = float(base_font_size.replace("pt", ""))
        effective_size = font_size_value * global_scale
        
        # Process the content line by line
        lines = markdown_text.strip().split('\n')
        processed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Problem section
            if line == "#problem":
                processed_lines.append("\\section*{}")  # Empty header
                i += 1
            
            # Add this to your existing parsing logic in the while loop
            # Bullet point item
            elif line.startswith("#bullet"):
                # If this is the first bullet, start an itemize environment
                if not any(l.startswith("\\begin{itemize}") for l in processed_lines[-3:]):
                    processed_lines.append("\\begin{itemize}")
                
                # Extract the bullet content (everything after #bullet)
                bullet_content = line[len("#bullet"):].strip()
                
                # Add the bullet item
                processed_lines.append("\\item " + bullet_content)
                
                # Check if next line is also a bullet
                next_is_bullet = False
                if i+1 < len(lines) and lines[i+1].strip().startswith("#bullet"):
                    next_is_bullet = True
                
                # If next line is not a bullet, close the itemize environment
                if not next_is_bullet:
                    processed_lines.append("\\end{itemize}")
                
                i += 1    
            # Solution section
            elif line == "#solution":
                processed_lines.append("\\section*{Solution}")
                i += 1
                
            # Equation environment - using indent environment
            elif line == "#eq":
                i += 1  # Move to the line with the equation content
                if i < len(lines):
                    equation_content = lines[i].strip()
                    # Use LaTeX indent environment
                    processed_lines.append("\\begin{equation*}")
                    processed_lines.append(equation_content)
                    processed_lines.append("\\end{equation*}")
                i += 1
                
            # Aligned equations environment
            elif line == "#align":
                i += 1  # Move to the first line of aligned equations
                align_content = []
                
                # Collect all lines until next command or end
                while i < len(lines) and not lines[i].strip().startswith('#'):
                    if lines[i].strip():  # Only add non-empty lines
                        align_content.append(lines[i].strip())
                    i += 1
                
                # Use aligned environment
                processed_lines.append("\\begin{align*}")
                processed_lines.append(" \\\\ ".join(align_content))
                processed_lines.append("\\end{align*}")
                
            # Question with no prefix and proper alignment
            elif line == "#question":
                i += 1  # Move to the line with the question content
                if i < len(lines):
                    question_text = lines[i].strip()
                    # Use normal text paragraph without indentation
                    processed_lines.append("\\noindent " + question_text)
                i += 1
                
            # Regular text
            else:
                processed_lines.append(line)
                i += 1
        
        # Join the processed lines
        content = '\n'.join(processed_lines)
        
        # Choose document class based on font size
        if effective_size <= 12:
            doc_class = "article"
        else:
            doc_class = "extarticle"  # Supports larger sizes (>12pt)
        
        # Round effective size to nearest standard size
        standard_sizes = [8, 9, 10, 11, 12, 14, 17, 20]
        closest_size = min(standard_sizes, key=lambda x: abs(x - effective_size))
        
        # Create template with direct font size control
        template = f"""\\documentclass[{closest_size}pt]{{{doc_class}}}
    \\usepackage[fleqn]{{amsmath}}  % Left-aligned equations
    \\usepackage{{amssymb}}
    \\usepackage{{graphicx}}
    \\usepackage{{geometry}}
    \\usepackage{{setspace}}  % For line spacing control

    \\geometry{{
        margin=0.75in
    }}

    % Set left margin for equations
    \\setlength{{\\mathindent}}{{3em}}  % Indent equations by 3em from left margin

    % Remove paragraph indentation for consistency
    \\setlength{{\\parindent}}{{0pt}}

    % Direct font size control at the beginning of the document
    \\begin{{document}}

    % Apply explicit font sizing
    \\fontsize{{{effective_size}pt}}{{1.2\\baselineskip}}\\selectfont

    CONTENT_PLACEHOLDER

    \\end{{document}}"""
        
        # Replace the placeholder with actual content
        document = template.replace("CONTENT_PLACEHOLDER", content)
        
        return document
        
    def create_problem_from_template(self, title, description, equations, question):
        """
        Create a problem using the template hierarchy
        
        Args:
            title (str): Problem title
            description (str): Problem description
            equations (list or str): Equation content
            question (str): Question text
            
        Returns:
            str: Generated problem content
        """
        # Start with the problem template
        problem = PROBLEM_TEMPLATE
        
        # Replace title placeholder
        problem = problem.replace("#TITLE#", title)
        
        # Replace description placeholder
        problem = problem.replace("#DESCRIPTION#", description)
        
        # Process equations
        equations_content = ""
        if isinstance(equations, list):
            for eq in equations:
                equation_slot = EQUATION_SLOT
                equation_slot = equation_slot.replace("#EQUATION_CONTENT#", eq)
                equations_content += equation_slot
        else:
            # Single string assumed to be aligned equations
            aligned_slot = ALIGNED_EQUATIONS_SLOT
            aligned_slot = aligned_slot.replace("#EQUATIONS_CONTENT#", equations)
            equations_content = aligned_slot
        
        # Replace equations placeholder
        problem = problem.replace("#EQUATIONS#", equations_content)
        
        # Replace question placeholder
        question_slot = QUESTION_SLOT
        question_slot = question_slot.replace("#QUESTION_TEXT#", question)
        problem = problem.replace("#QUESTION#", question_slot)
        
        return problem
    
    def generate_from_template(self, template_id, slot_values):
        """
        Generate markdown from a template and slot values
        
        Args:
            template_id (str): The ID of the template to use
            slot_values (dict): Dictionary of slot_id -> value
            
        Returns:
            str: Generated markdown content
        """
        from constants import TEMPLATES
        
        if template_id not in TEMPLATES:
            raise ValueError(f"Unknown template: {template_id}")
        
        template = TEMPLATES[template_id]
        
        # Start with the template text
        result = template["template"]
        
        # Replace slot placeholders with values
        for slot_id, value in slot_values.items():
            if slot_id in template["slots"]:
                result = result.replace(f"#{slot_id.upper()}#", value)
        
        # Handle optional sections
        for slot_id, slot_info in template["slots"].items():
            if not slot_info["required"] and (slot_id not in slot_values or not slot_values[slot_id]):
                # If the slot is optional and empty, remove the wrapped section
                wrap_start = f"#{slot_id.upper()}_WRAP_START#"
                wrap_end = f"#{slot_id.upper()}_WRAP_END#"
                
                # Use regex to handle potential multi-line content
                pattern = f"{wrap_start}.*?{wrap_end}"
                result = re.sub(pattern, "", result, flags=re.DOTALL)
        
        return result