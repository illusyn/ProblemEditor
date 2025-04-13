"""
Constants and default settings for the Math Problem Editor.
"""

# Default configuration settings
DEFAULT_CONFIG = {
    "fonts": {
        "base_font_size": "12pt",  # Changed to standard supported size
        "global_scale": "0.8",     # Global scaling factor (0.5 to 1.0)
        "problem_header_scale": "1.2",  # This will be a scale factor (e.g., 1.2 = 20% larger than base)
        "question_scale": "1.0",  # No scaling by default
        "equation_scale": "1.0"  # No scaling by default
    },
    "spacing": {
        "line_spacing": "1.5",
        "above_equation": "12pt",
        "below_equation": "12pt",
        "paragraph_spacing": "6pt"
    },
    "styling": {
        "question_format": "#TEXT#",  # Removed "Question:" prefix
        "problem_format": "\\section*{#TEXT#}"
    },
    "margins": {
        "top": "0.75in",
        "right": "0.75in",
        "bottom": "0.75in",
        "left": "0.75in"
    },
    "custom_commands": {
        "#problem": "\\problemheader{}",  # Empty brackets to remove "Problem" text
        "#solution": "\\problemheader{Solution}",
        "#question": "\\questiontext{#TEXT#}",
        "#eq": "\\begin{equation}\n#TEXT#\n\\end{equation}",
        "#align": "\\begin{align}\n#TEXT#\n\\end{align}"
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

# Function to generate LaTeX template based on font configuration
# The following changes need to be made to your LaTeX template in constants.py:


def generate_latex_template(config):
    # Use the extarticle class which supports smaller font sizes
    template = """\\documentclass[6pt]{extarticle}  % extarticle supports smaller sizes like 6pt
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{graphicx}
\\usepackage{geometry}
\\usepackage{setspace}

% Configure margins - make them smaller to help shrink content
\\geometry{
    top=#TOP#,
    right=#RIGHT#,
    bottom=#BOTTOM#,
    left=#LEFT#
}

% Line spacing
\\setstretch{#LINESPACING#}

% Remove section numbering
\\setcounter{secnumdepth}{0}

% Custom commands with explicit tiny sizing
\\newcommand{\\problemheader}[1]{\\tiny\\textbf{#1}}
\\newcommand{\\questiontext}[1]{\\tiny #1}

% Start with tiny text
\\begin{document}
\\tiny

#CONTENT#

\\end{document}
"""
    return template



# Get the current LaTeX template based on default configuration
LATEX_TEMPLATE = generate_latex_template(DEFAULT_CONFIG)

# Template for a problem with slots
PROBLEM_TEMPLATE = r"""
\problemheader{#TITLE#}

#DESCRIPTION#

#EQUATIONS#

#QUESTION#
"""

# Template for a single equation slot
EQUATION_SLOT = r"""
\begin{equation}
#EQUATION_CONTENT#
\end{equation}
"""

# Template for aligned equations slot
ALIGNED_EQUATIONS_SLOT = r"""
\begin{align}
#EQUATIONS_CONTENT#
\end{align}
"""

# Template for question slot
QUESTION_SLOT = r"""
\vspace{1em}
\questiontext{#QUESTION_TEXT#}
"""

# Template definitions for various problem types
TEMPLATES = {
    "basic_problem": {
        "name": "Basic Problem",
        "description": "A simple problem with one equation and a question",
        "template": """#problem
#DESCRIPTION#

#eq
#EQUATION#

#question
#QUESTION#
""",
        "slots": {
            "description": {
                "name": "Description",
                "required": True,
                "default": "Solve the following equation:"
            },
            "equation": {
                "name": "Equation",
                "required": True,
                "default": "2x + 3 = 7"
            },
            "question": {
                "name": "Question",
                "required": True,
                "default": "What is the value of x?"
            }
        }
    },
    "two_equation_problem": {
        "name": "Two Equation Problem",
        "description": "A problem with two equations and a question",
        "template": """#problem
#DESCRIPTION#

#eq
#EQUATION1#

#eq
#EQUATION2#

#question
#QUESTION#
""",
        "slots": {
            "description": {
                "name": "Description",
                "required": True,
                "default": "Solve the system of equations:"
            },
            "equation1": {
                "name": "First Equation",
                "required": True,
                "default": "3x + 2y = 12"
            },
            "equation2": {
                "name": "Second Equation",
                "required": True,
                "default": "x - y = 1"
            },
            "question": {
                "name": "Question",
                "required": True,
                "default": "Find the values of x and y."
            }
        }
    },
    "image_problem": {
        "name": "Problem with Image",
        "description": "A problem with an image and a question",
        "template": """#problem
#DESCRIPTION#

[Insert figure reference here]

#ADDITIONAL_TEXT_WRAP_START#
#ADDITIONAL_TEXT#
#ADDITIONAL_TEXT_WRAP_END#

#question
#QUESTION#
""",
        "slots": {
            "description": {
                "name": "Description",
                "required": True,
                "default": "Consider the triangle shown in the figure:"
            },
            "additional_text": {
                "name": "Additional Text",
                "required": False,
                "default": ""
            },
            "question": {
                "name": "Question",
                "required": True,
                "default": "Calculate the area of the triangle."
            }
        }
    },
    "multi_part_problem": {
        "name": "Multi-Part Problem",
        "description": "A problem with multiple parts",
        "template": """#problem
#DESCRIPTION#

#eq
#EQUATION#

#question
#QUESTION_PART_A#

#PART_B_WRAP_START#
#question
#QUESTION_PART_B#
#PART_B_WRAP_END#

#PART_C_WRAP_START#
#question
#QUESTION_PART_C#
#PART_C_WRAP_END#
""",
        "slots": {
            "description": {
                "name": "Description",
                "required": True,
                "default": "Consider the following equation:"
            },
            "equation": {
                "name": "Equation",
                "required": True,
                "default": "f(x) = x^2 - 4x + 3"
            },
            "question_part_a": {
                "name": "Question Part A",
                "required": True,
                "default": "Find the zeros of f(x)."
            },
            "question_part_b": {
                "name": "Question Part B",
                "required": False,
                "default": "Find the minimum value of f(x)."
            },
            "question_part_c": {
                "name": "Question Part C",
                "required": False,
                "default": "Sketch the graph of f(x)."
            }
        }
    }
}

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
- Custom Commands: Define what markdown commands like #problem do

## Custom Commands
You can define your own custom markdown commands in the Custom Commands tab 
of the configuration dialog. For example, you could create:
#example   - For example problems
#note      - For notes or hints
#theorem   - For mathematical theorems

Use #TEXT# as a placeholder for content that follows the command.
"""