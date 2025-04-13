"""
Error logging module for the Math Problem Editor.
"""

import os
import datetime

class ErrorLogger:
    """Handles logging of errors for the Math Problem Editor"""
    
    def __init__(self, base_dir=None):
        """
        Initialize the error logger
        
        Args:
            base_dir (str, optional): Base directory for log files. 
                                     If None, will use the project directory.
        """
        # If no base directory is provided, use the project directory
        if base_dir is None:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.base_dir = base_dir
            
        # Create logs directory if it doesn't exist
        self.logs_dir = os.path.join(self.base_dir, "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def log_error(self, error_type, error_content, additional_info=None):
        """
        Log an error to a file
        
        Args:
            error_type (str): Type of error (e.g., 'LaTeX', 'Parsing')
            error_content (str): Error message or log content
            additional_info (str, optional): Additional information about the error
            
        Returns:
            str: Path to the log file
        """
        # Create a timestamp for the log file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a log file name
        log_file_name = f"{error_type.lower()}_error_{timestamp}.log"
        log_file_path = os.path.join(self.logs_dir, log_file_name)
        
        # Write the error to the log file
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write(f"=== {error_type} Error ===\n")
            f.write(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if additional_info:
                f.write(f"Additional Information:\n{additional_info}\n\n")
                
            f.write(f"Error Content:\n{error_content}\n")
        
        return log_file_path