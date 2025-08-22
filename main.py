#!/usr/bin/env python3
"""
Sistema de Extracción de Datos de Facturación Odoo 17

Aplicación de escritorio para extraer datos de facturación y terceros
desde una base de datos PostgreSQL de Odoo 17 y generar reportes en Excel.

Author: Sistema Extractor Odoo 17
Version: 1.0
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from ui.main_window import MainWindow
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def setup_logging():
    """Setup application logging."""
    log_file = project_root / "extractor.log"
    
    # Create logs directory if it doesn't exist
    log_file.parent.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("="*50)
    logger.info("Sistema de Extracción de Datos Odoo 17 - Iniciando")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Project root: {project_root}")
    logger.info("="*50)


def check_dependencies():
    """Check if all required dependencies are available."""
    required_modules = [
        'tkinter',
        'psycopg2',
        'pandas', 
        'openpyxl',
        'tkcalendar',
        'cryptography'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'tkinter':
                import tkinter
            elif module == 'psycopg2':
                import psycopg2
            elif module == 'pandas':
                import pandas
            elif module == 'openpyxl':
                import openpyxl
            elif module == 'tkcalendar':
                import tkcalendar
            elif module == 'cryptography':
                import cryptography
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"Missing required modules: {', '.join(missing_modules)}\n"
        error_msg += "Please install them using:\n"
        error_msg += "pip install -r requirements.txt"
        
        # Try to show GUI error if tkinter is available
        try:
            import tkinter
            from tkinter import messagebox
            root = tkinter.Tk()
            root.withdraw()  # Hide main window
            messagebox.showerror("Missing Dependencies", error_msg)
            root.destroy()
        except:
            print(error_msg)
        
        return False
    
    return True


def main():
    """Main entry point."""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Check dependencies
        if not check_dependencies():
            logger.error("Missing required dependencies")
            sys.exit(1)
        
        logger.info("All dependencies available")
        
        # Create and run main application
        logger.info("Creating main window")
        app = MainWindow()
        
        logger.info("Starting application main loop")
        app.run()
        
        logger.info("Application finished normally")
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        
        # Try to show GUI error
        try:
            import tkinter
            from tkinter import messagebox
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror("Error Crítico", f"Error inesperado:\n{str(e)}")
            root.destroy()
        except:
            print(f"Critical error: {e}")
        
        sys.exit(1)


if __name__ == "__main__":
    main()