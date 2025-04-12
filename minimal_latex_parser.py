import re

class SimpleLatexParser:
    """
    A minimal parser that converts simple markdown to LaTeX with focus on
    generating valid equation environments.
    """
    
    def __init__(self):
        self.document_template = r"""\documentclass[12pt]{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}

\begin{document}

%s

\end{document}
"""

    def parse(self, markdown_text):
        """Convert markdown to minimal LaTeX focusing on valid equation syntax"""
        # Process the content
        content = markdown_text.strip()
        
        # Process sections
        content = content.replace("#problem\n", "\\section*{Problem}\n")
        content = content.replace("#solution\n", "\\section*{Solution}\n")
        
        # Process question
        question_pattern = r'#question\s*(.*?)(?=\n#|\n\s*$|\s*$)'
        content = re.sub(question_pattern, r'\\textbf{Question:} \1', content, flags=re.DOTALL)
        
        # Very simple equation handling - no complex patterns
        lines = content.split('\n')
        processed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.strip() == "#eq":
                # Found an equation marker, collect equation lines
                processed_lines.append("\\begin{equation}")
                i += 1  # Move to next line
                
                # Collect all lines until we find another marker or end
                while i < len(lines) and not lines[i].strip().startswith('#'):
                    if lines[i].strip():  # Only add non-empty lines
                        processed_lines.append(lines[i])
                    i += 1
                
                processed_lines.append("\\end{equation}")
                
            elif line.strip() == "#align":
                # Similar handling for align environment
                processed_lines.append("\\begin{align}")
                i += 1
                
                while i < len(lines) and not lines[i].strip().startswith('#'):
                    if lines[i].strip():  # Only add non-empty lines
                        processed_lines.append(lines[i])
                    i += 1
                
                processed_lines.append("\\end{align}")
                
            else:
                # Normal line, just add it
                processed_lines.append(line)
                i += 1
        
        # Join everything back together
        content = '\n'.join(processed_lines)
        
        # Wrap in document template
        return self.document_template % content


# Test the parser
if __name__ == "__main__":
    parser = SimpleLatexParser()
    
    # Test markdown
    test_markdown = """#problem
Solve the equation:

#eq
2x + 3 = 7

#question
What is x?

#solution
Subtract 3 from both sides:

#eq
2x = 4

Divide by 2:

#eq
x = 2
"""
    
    latex = parser.parse(test_markdown)
    print(latex)