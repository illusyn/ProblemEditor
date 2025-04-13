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
        
        # Generate a LaTeX template based on current configuration
        latex_template = constants.generate_latex_template(config)
        
        # Process the markdown line by line - using the approach from the test script
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
            
            # Handle equation with centering
            elif line == "#eq":
                # Add spacing above equation
                latex_lines.append("\\vspace{" + config["spacing"]["above_equation"] + "}")
                
                # Begin centered equation
                latex_lines.append("\\begin{center}")
                latex_lines.append("\\begin{equation}")
                
                # Move to the next line (which should contain the equation)
                i += 1
                if i < len(lines):
                    # Add the equation content
                    latex_lines.append(lines[i].strip())
                
                # End equation and center
                latex_lines.append("\\end{equation}")
                latex_lines.append("\\end{center}")
                
                # Add spacing below equation
                latex_lines.append("\\vspace{" + config["spacing"]["below_equation"] + "}")
                
                i += 1
                continue
            
            # Handle align environment with centering
            elif line == "#align":
                # Add spacing above align
                latex_lines.append("\\vspace{" + config["spacing"]["above_equation"] + "}")
                
                # Begin centered align environment
                latex_lines.append("\\begin{center}")
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
                latex_lines.append("\\end{center}")
                
                # Add spacing below align
                latex_lines.append("\\vspace{" + config["spacing"]["below_equation"] + "}")
                
                continue  # Don't increment i since we already moved to the next marker
            
            # Handle question with no "Question:" prefix
            elif line == "#question":
                # Get the question text
                i += 1
                if i < len(lines):
                    question_text = lines[i].strip()
                    
                    # Format according to configuration but with no "Question:" prefix
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
    
    def create_problem_from_template(self, title, description, equations, question):
        """
        Create a problem using the template hierarchy
        
        Args:
            title (str): Problem title
            description (str): Problem description
            equations (list): List of equation content
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
        
        # Process equations - can be a list of individual equations or aligned equations
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