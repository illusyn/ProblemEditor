"""
Constants and default settings for the Math Problem Editor.
"""

# Default configuration settings
DEFAULT_CONFIG = {
    "fonts": {
        "base_font_size": "12pt",  # Default base size
        "global_scale": "1.0",     # Global scaling factor (0.5 to 1.0)
        "problem_header_scale": "1.2",  # Scale factor for headers
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
        "question_format": "#TEXT#",  # No "Question:" prefix
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
def generate_latex_template(config):
    # Extract base font size from configuration
    base_font_size = config["fonts"]["base_font_size"]
    
    # Only allow valid font sizes
    valid_sizes = ["8pt", "9pt", "10pt", "11pt", "12pt", "14pt", "17pt", "20pt"]
    if base_font_size not in valid_sizes:
        base_font_size = "12pt"  # Default if invalid
    
    # Get global scaling factor
    global_scale = float(config["fonts"].get("global_scale", "1.0"))
    
    # Calculate relative sizes based on scale factors
    header_scale = float(config["fonts"]["problem_header_scale"])
    question_scale = float(config["fonts"]["question_scale"])
    equation_scale = float(config["fonts"]["equation_scale"])
    
    # Create LaTeX commands for relative sizes with global scaling
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

% Ensure equations are in display style for better readability
\\everymath{{\\displaystyle}}

% Custom commands for sizes
{header_cmd}
{question_cmd}

\\begin{{document}}

\\fontsize{{18}}{{22}}\\selectfont

#CONTENT#

\\end{{document}}
"""
    return template

# Get the current LaTeX template based on default configuration
LATEX_TEMPLATE = generate_latex_template(DEFAULT_CONFIG)

# Template Hierarchy System

# Template Types
TEMPLATE_TYPES = {
    "one_equation": "One Equation Problem",
    "two_equations": "Two Equation Problem", 
    "text_image": "Problem with Image",
    "separated_question": "Separated Question",
    "multi_part": "Multi-part Question",
    "multi_choice": "Multiple Choice"
}

# Slot Types
SLOT_TYPES = {
    "text": "Text Block",
    "equation": "Equation",
    "aligned_equations": "Aligned Equations",
    "question": "Question",
    "image": "Image",
    "multi_choice": "Multiple Choice"
}

# Template Definitions
TEMPLATES = {
    "one_equation": {
        "name": "One Equation Problem",
        "description": "A basic problem with a single equation to solve",
        "slots": [
            {"id": "intro", "type": "text", "name": "Introduction", "required": True},
            {"id": "equation", "type": "equation", "name": "Equation", "required": True},
            {"id": "question", "type": "question", "name": "Question", "required": True}
        ],
        "markdown_template": """#problem
#INTRO#

#eq
#EQUATION#

#question
#QUESTION#
"""
    },
    "two_equations": {
        "name": "Two Equation Problem",
        "description": "A problem with a system of two equations to solve",
        "slots": [
            {"id": "intro", "type": "text", "name": "Introduction", "required": True},
            {"id": "equation1", "type": "equation", "name": "First Equation", "required": True},
            {"id": "equation2", "type": "equation", "name": "Second Equation", "required": True},
            {"id": "question", "type": "question", "name": "Question", "required": True}
        ],
        "markdown_template": """#problem
#INTRO#

#eq
#EQUATION1#

#eq
#EQUATION2#

#question
#QUESTION#
"""
    },
    "text_image": {
        "name": "Problem with Image",
        "description": "A problem that includes an image reference, useful for geometric problems",
        "slots": [
            {"id": "intro", "type": "text", "name": "Introduction", "required": True},
            {"id": "image", "type": "image", "name": "Image Reference", "required": False},
            {"id": "question", "type": "question", "name": "Question", "required": True}
        ],
        "markdown_template": """#problem
#INTRO#

[#IMAGE#]

#question
#QUESTION#
"""
    },
    "separated_question": {
        "name": "Separated Question",
        "description": "A problem with a clear separation between the given information and the question",
        "slots": [
            {"id": "given", "type": "text", "name": "Given Information", "required": True},
            {"id": "equation", "type": "equation", "name": "Equation", "optional": True},
            {"id": "question", "type": "question", "name": "Question", "required": True}
        ],
        "markdown_template": """#problem
Given:
#GIVEN#

#eq
#EQUATION#

#question
#QUESTION#
"""
    },
    "multi_part": {
        "name": "Multi-part Question",
        "description": "A problem with multiple sub-questions",
        "slots": [
            {"id": "intro", "type": "text", "name": "Introduction", "required": True},
            {"id": "equation", "type": "equation", "name": "Equation", "optional": True},
            {"id": "part_a", "type": "question", "name": "Part (a)", "required": True},
            {"id": "part_b", "type": "question", "name": "Part (b)", "required": True},
            {"id": "part_c", "type": "question", "name": "Part (c)", "optional": True}
        ],
        "markdown_template": """#problem
#INTRO#

#eq
#EQUATION#

#question
(a) #PART_A#

(b) #PART_B#

#PART_C_WRAP_START#(c) #PART_C##PART_C_WRAP_END#
"""
    },
    "multi_choice": {
        "name": "Multiple Choice",
        "description": "A problem with multiple choice answer options",
        "slots": [
            {"id": "intro", "type": "text", "name": "Introduction", "required": True},
            {"id": "equation", "type": "equation", "name": "Equation", "optional": True},
            {"id": "question", "type": "question", "name": "Question", "required": True},
            {"id": "option_a", "type": "text", "name": "Option A", "required": True},
            {"id": "option_b", "type": "text", "name": "Option B", "required": True},
            {"id": "option_c", "type": "text", "name": "Option C", "required": True},
            {"id": "option_d", "type": "text", "name": "Option D", "required": True},
            {"id": "option_e", "type": "text", "name": "Option E", "optional": True}
        ],
        "markdown_template": """#problem
#INTRO#

#eq
#EQUATION#

#question
#QUESTION#

(A) #OPTION_A#
(B) #OPTION_B#
(C) #OPTION_C#
(D) #OPTION_D#
#OPTION_E_WRAP_START#(E) #OPTION_E##OPTION_E_WRAP_END#
"""
    }
}

# Help text for markdown syntax
HELP_TEXT = """
# Markdown Syntax Reference

## Basic Structure
#problem     - Problem section
#solution    - Solution section
#question    - Question text (no "Question:" prefix)

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
"""