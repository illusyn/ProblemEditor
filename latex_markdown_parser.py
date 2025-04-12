import re

class LatexMarkdownParser:
    """
    Parser for custom markdown syntax specifically designed for math problems.
    Converts simplified markdown to proper LaTeX.
    """
    
    def __init__(self):
        # Define basic templates
        self.document_template = r"""\documentclass[12pt]{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}

\begin{document}

%s

\end{document}
"""

    def parse(self, markdown_text):
        """Convert custom markdown to LaTeX"""
        # Process the content
        content = markdown_text.strip()
        
        # Apply transformations
        content = self._process_problem_sections(content)
        content = self._process_equations(content)
        content = self._process_parts(content)
        content = self._process_figures(content)
        
        # Wrap in document template if not already a complete document
        if "\\documentclass" not in content:
            content = self.document_template % content
            
        return content
    
    def _process_problem_sections(self, content):
        """Process #problem, #solution sections"""
        # Replace #problem with section header
        content = re.sub(r'#problem\s*\n', r'\\section*{Problem}\n', content)
        
        # Replace #solution with section header
        content = re.sub(r'#solution\s*\n', r'\\section*{Solution}\n', content)
        
        # Replace #question with bolded text
        content = re.sub(r'#question\s*(.*?)(?=\n#|\n\s*$|\s*$)', r'\\textbf{Question:} \1', content, flags=re.DOTALL)
        
        return content
    
    def _process_equations(self, content):
        """Process equation markers with more careful handling"""
        # Process #eq - single equation
        def eq_replace(match):
            eq_content = match.group(1).strip()
            # Remove trailing whitespace and ensure there's no empty lines
            eq_content = re.sub(r'\n\s*\n', '\n', eq_content)
            return f"\\begin{{equation}}\n{eq_content}\n\\end{{equation}}"
            
        content = re.sub(r'#eq\s*(.*?)(?=\n#|\n\s*$|\s*$)', 
                         eq_replace, 
                         content, flags=re.DOTALL)
        
        # Process #align - aligned equations
        def align_replace(match):
            align_content = match.group(1).strip()
            # Remove trailing whitespace and ensure there's no empty lines
            align_content = re.sub(r'\n\s*\n', '\n', align_content)
            return f"\\begin{{align}}\n{align_content}\n\\end{{align}}"
            
        content = re.sub(r'#align\s*(.*?)(?=\n#|\n\s*$|\s*$)', 
                         align_replace, 
                         content, flags=re.DOTALL)
        
        # Inline math: #$...$
        content = re.sub(r'#\$(.*?)\$', r'$\1$', content)
        
        return content
    
    def _process_parts(self, content):
        """Process multi-part problems"""
        # Part markers: #part(a), #part(b), etc.
        content = re.sub(r'#part\(([a-z])\)\s*(.*?)(?=\n#part|\n#|\n\s*$|\s*$)', 
                         r'\\textbf{(\1)} \2', 
                         content, flags=re.DOTALL)
        
        return content
    
    def _process_figures(self, content):
        """Process figure insertions"""
        # Figure: #figure[filename.png][caption]
        def figure_replace(match):
            filename = match.group(1)
            caption = match.group(2) if match.group(2) else ""
            
            return f"""\\begin{{figure}}[h]
\\centering
\\includegraphics[width=0.7\\textwidth]{{{filename}}}
\\caption{{{caption}}}
\\end{{figure}}"""
            
        content = re.sub(r'#figure\[(.*?)\](?:\[(.*?)\])?', 
                         figure_replace, 
                         content)
        
        return content


# Example of usage
if __name__ == "__main__":
    parser = LatexMarkdownParser()
    
    # Example markdown
    markdown = """#problem
Find the solution to the following quadratic equation:

#eq
ax^2 + bx + c = 0

#question
If a = 1, b = -3, and c = 2, what are the values of x?

#solution
Using the quadratic formula:

#eq
x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}

Substituting the values:

#eq
x = \\frac{3 \\pm \\sqrt{9 - 8}}{2} = \\frac{3 \\pm \\sqrt{1}}{2} = \\frac{3 \\pm 1}{2}

Therefore, x = 2 or x = 1.
"""
    
    late