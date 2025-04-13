"""
Configuration management for the Math Problem Editor.
"""

import os
import json
from constants import DEFAULT_CONFIG

class ConfigManager:
    """Manages the application configuration"""
    
    def __init__(self, config_file=None):
        """
        Initialize the configuration manager
        
        Args:
            config_file (str, optional): Path to the configuration file. Defaults to None.
        """
        self.config = DEFAULT_CONFIG.copy()
        self.config_file = config_file
        
        if self.config_file and os.path.exists(self.config_file):
            self.load_config()
    
    def load_config(self):
        """
        Load configuration from file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                
            # Update configuration with user values
            for category in user_config:
                if category in self.config:
                    self.config[category].update(user_config[category])
                    
            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def save_config(self):
        """
        Save configuration to file
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.config_file:
            return False
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def reset_to_defaults(self):
        """
        Reset configuration to default values
        
        Returns:
            bool: True if successful
        """
        self.config = DEFAULT_CONFIG.copy()
        return True