"""
Constants and default settings for the Math Problem Editor.
"""

# Default configuration settings
DEFAULT_CONFIG = {
    "fonts": {
        "main_text_size": "12pt",
        "problem_header_size": "14pt",
        "question_size": "12pt",
        "equation_size": "12pt"
    },
    "spacing": {
        "line_spacing": "1.5",
        "above_equation": "6pt",
        "below_equation": "6pt",
        "paragraph_spacing": "6pt"
    },
    "styling": {
        "question_format": "\\textbf{Question:} #TEXT#",
        "problem_format": "\\section*{#TEXT#}"
    },
    "margins": {
        "top": "0.75in",
        "right": "0.75in",
        "bottom": "0.75in",
        "left": "0.75in"
    }
}

# Default problem template
DEFAULT_TEMPLATE = """#problem
Solve the following equation:

#eq
2x + 3 = 7

#question
What is the value of x?
"""

# Updated LaTeX template with proper formatting and no section numbering
LATEX_TEMPLATE = r"""\documentclass[12pt]{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{geometry}

% Configure margins
\geometry{margin=0.75in}

% Remove section numbering completely
\setcounter{secnumdepth}{0}

% Ensure displaystyle for equations
\everymath{\displaystyle}

\begin{document}

#CONTENT#

\end{document}
"""

# Help text for markdown syntax
HELP_TEXT = """
# Markdown Syntax Reference

## Basic Structure
#problem     - Problem section
#solution    - Solution section
#question    - Question text

## Equation Environments
#eq          - Start an equation, put the equation on the next line
#align       - Start an aligned equations environment

## Example:
#problem
Solve the equation:

#eq
2x + 3 = 7

#question
What is x?

#solution
We solve step by step:

#eq
2x = 4

#eq
x = 2

## Configuration
You can customize how elements are rendered through the Format menu:
- Edit Configuration: Modify font sizes, spacing, and formatting
- Save Configuration: Save your settings for future sessions
- Reset Configuration: Return to default settings
"""