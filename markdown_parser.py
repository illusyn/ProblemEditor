"""
Custom markdown parser for the Math Problem Editor.
"""

import re
from constants import LATEX_TEMPLATE

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
        
        # Process the content
        content = markdown_text.strip()
        
        # Process sections
        problem_format = config["styling"]["problem_format"]
        content = content.replace("#problem\n", 
                                 problem_format.replace("#TEXT#", "Problem") + "\n")
        content = content.replace("#solution\n", 
                                 problem_format.replace("#TEXT#", "Solution") + "\n")
        
        # Process question - using direct formatting instead of a custom command
        question_pattern = r'#question\s*(.*?)(?=\n#|\n\s*$|\s*$)'
        question_format = config["styling"]["question_format"]
        
        def question_replace(match):
            question_text = match.group(1).strip()
            return question_format.replace("#TEXT#", question_text)
            
        content = re.sub(question_pattern, question_replace, content, flags=re.DOTALL)
        
        # Process equations with configurable spacing
        above_eq_space = config["spacing"]["above_equation"]
        below_eq_space = config["spacing"]["below_equation"]
        
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
        
        # Replace placeholders in the document template
        document = LATEX_TEMPLATE
        document = document.replace("#TOP#", config["margins"]["top"])
        document = document.replace("#RIGHT#", config["margins"]["right"])
        document = document.replace("#BOTTOM#", config["margins"]["bottom"])
        document = document.replace("#LEFT#", config["margins"]["left"])
        document = document.replace("#LINESPACING#", config["spacing"]["line_spacing"])
        document = document.replace("#CONTENT#", content)
        
        return document