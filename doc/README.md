# Math Problem Editor

A LaTeX-based editor for creating math problems with configurable formatting.

## Features

- Custom markdown syntax for easy problem creation
- Live LaTeX preview
- Configurable formatting options (fonts, spacing, margins)
- Export to PDF
- Save and load problems

## Requirements

- Python 3.x
- tkinter (included with most Python installations)
- PIL/Pillow (`pip install Pillow`)
- pdf2image (`pip install pdf2image`)
- A LaTeX distribution (TeX Live, MiKTeX, etc.)
- Poppler (needed by pdf2image to process PDFs)

## Installation

1. Clone or download this repository
2. Install required packages:
   ```
   pip install Pillow pdf2image
   ```
3. Ensure you have a LaTeX distribution installed (MiKTeX, TeX Live, etc.)
4. Ensure Poppler is installed (required by pdf2image)

## Usage

Run the application with:

```
python main.py
```

### Markdown Syntax

The editor uses a simple markdown-like syntax:

- `#problem` - Starts a problem section
- `#solution` - Starts a solution section
- `#question` - Defines a question (e.g., "What is the value of x?")
- `#eq` - Inserts an equation environment
- `#align` - Inserts an aligned equations environment

Example:

```
#problem
Solve the following equation:

#eq
2x + 3 = 7

#question
What is the value of x?

#solution
Subtract 3 from both sides:

#eq
2x = 4

Divide by 2:

#eq
x = 2
```

### Configuration

The editor allows you to customize various formatting options:

- Font sizes for different elements
- Spacing between equations and paragraphs
- Page margins
- Styling for questions and section headers

Configuration settings are stored in `editor_config.json`.

## Project Structure

- `main.py` - Entry point for the application
- `constants.py` - Default settings and constants
- `config_manager.py` - Configuration handling
- `markdown_parser.py` - Custom markdown parsing
- `ui_components.py` - Reusable UI dialogs and widgets
- `problem_editor.py` - Main editor class
- `editor_config.json` - Configuration file
- `__init__.py` - Package definition

## License

This project is licensed under the MIT License - see the LICENSE file for details.
