#!/usr/bin/env python3
"""
Test simple sin dependencias externas
"""

import tkinter as tk
from tkinter import ttk
import sys

def test_simple_ui():
    """Test simple de la UI sin dependencias externas."""
    
    root = tk.Tk()
    root.title("📊 Test Interfaz Moderna")
    root.geometry("600x400")
    root.configure(bg='#f0f0f0')
    
    # Setup theme
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure modern button
    style.configure('Accent.TButton',
                   background='#2E86AB',
                   foreground='white',
                   focuscolor='none',
                   borderwidth=0,
                   font=('Arial', 10, 'bold'))
    
    # Main frame
    main_frame = tk.Frame(root, bg='#f0f0f0')
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Modern header
    header = tk.Frame(main_frame, bg='#2E86AB', height=80)
    header.pack(fill='x', pady=(0, 20))
    
    title = tk.Label(header, 
                    text="📊 Sistema de Extracción de Datos", 
                    font=("Arial", 16, "bold"),
                    bg='#2E86AB', fg='white')
    title.pack(expand=True)
    
    # Content area
    content = tk.Frame(main_frame, bg='white', relief='flat', bd=1)
    content.pack(fill='both', expand=True, pady=(0, 20))
    
    # Test label
    test_label = tk.Label(content,
                         text="✅ Interfaz moderna funcionando correctamente!",
                         font=("Arial", 12),
                         bg='white', fg='#2E86AB')
    test_label.pack(pady=30)
    
    # Test button
    test_button = ttk.Button(content,
                            text="🚀 Botón de Prueba",
                            style="Accent.TButton",
                            command=lambda: print("¡Botón funcionando!"))
    test_button.pack(pady=10)
    
    # Status
    status = tk.Frame(main_frame, bg='#E8F4FD', height=40)
    status.pack(fill='x')
    
    status_label = tk.Label(status,
                           text="✅ Prueba de interfaz exitosa",
                           font=("Arial", 10),
                           bg='#E8F4FD', fg='#2E86AB')
    status_label.pack(pady=8)
    
    print("🎉 Interfaz moderna cargada correctamente")
    root.mainloop()

if __name__ == "__main__":
    print("🧪 Probando interfaz moderna...")
    try:
        test_simple_ui()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)