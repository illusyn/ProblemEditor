"""
Main entry point for the Math Problem Editor application.
"""

import os
import tkinter as tk
from pathlib import Path

from config_manager import ConfigManager
from markdown_parser import MarkdownParser
from problem_editor import MathProblemEditor

def main():
    """Main entry point for the application"""
    # Create the root window
    root = tk.Tk()
    
    # Configuration file path (in the same directory as the script)
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editor_config.json")
    
    # Initialize configuration manager
    config_manager = ConfigManager(config_file)
    
    # Initialize markdown parser
    markdown_parser = MarkdownParser(config_manager)
    
    # Create main application window
    app = MathProblemEditor(root, config_manager, markdown_parser)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()