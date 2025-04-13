"""
Constants and default settings for the Math Problem Editor.
"""

# Default configuration settings
DEFAULT_CONFIG = {
    "fonts": {
        "base_font_size": "8pt",  # Smaller default size
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
    # Extract base font size from configuration
    base_font_size = config["fonts"]["base_font_size"]
    
    # Only allow valid font sizes
    valid_sizes = ["6pt", "7pt", "8pt", "9pt", "10pt", "11pt", "12pt", "14pt", "17pt", "20pt"]
    if base_font_size not in valid_sizes:
        base_font_size = "12pt"  # Default to larger font
    
    # Get global scaling factor
    global_scale = float(config["fonts"].get("global_scale", "1.0"))
    
    # Calculate relative sizes based on scale factors
    header_scale = float(config["fonts"]["problem_header_scale"])
    question_scale = float(config["fonts"]["question_scale"])
    equation_scale = float(config["fonts"]["equation_scale"])
    
    # Create LaTeX commands for relative sizes with global scaling
    # Note: Removed "Problem" text from the problemheader command
    header_cmd = "\\newcommand{\\problemheader}[1]{\\normalsize\\textbf{#1}}"
    if header_scale > 1.1 and global_scale > 0.8:
        header_cmd = "\\newcommand{\\problemheader}[1]{\\large\\textbf{#1}}"
    if header_scale > 1.3 and global_scale > 0.9:
        header_cmd = "\\newcommand{\\problemheader}[1]{\\Large\\textbf{#1}}"
    
    # Modified question command to remove "Question:" text completely
    question_cmd = "\\newcommand{\\questiontext}[1]{#1}"
    if question_scale > 1.1 and global_scale > 0.9:
        question_cmd = "\\newcommand{\\questiontext}[1]{\\large #1}"
    
    # Generate the template with appropriate base size
    template = f"""\\documentclass[{base_font_size}]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{geometry}}
\\usepackage{{setspace}}

% Configure margins
\\geometry{{
    top=#TOP#,
    right=#RIGHT#,
    bottom=#BOTTOM#,
    left=#LEFT#
}}

% Line spacing
\\setstretch{{#LINESPACING#}}

% Remove section numbering
\\setcounter{{secnumdepth}}{{0}}

% CENTER ALL EQUATIONS by default
\\renewenvironment{{equation}}{{
    \\begin{{equation}}
    \\centering
}}{{
    \\end{{equation}}
}}

% Enhanced equation display
\\everymath{{\\displaystyle}}

% Custom commands for sizes
{header_cmd}
{question_cmd}

% Apply global scaling to the entire document
\\begin{{document}}

\\{'small' if global_scale < 0.8 else 'normalsize'}

#CONTENT#

\\end{{document}}
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