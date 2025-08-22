import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from typing import Optional, Callable, Dict, Any

from database.connection import DatabaseConnection
from utils.config_manager import ConfigManager


class ConfigWindow:
    """Database configuration window with connection testing."""
    
    def __init__(self, parent: tk.Tk, config_manager: ConfigManager, 
                 on_config_saved: Optional[Callable] = None):
        """
        Initialize configuration window.
        
        Args:
            parent: Parent window
            config_manager: Configuration manager instance
            on_config_saved: Callback function called when config is saved
        """
        self.parent = parent
        self.config_manager = config_manager
        self.on_config_saved = on_config_saved
        
        self.window: Optional[tk.Toplevel] = None
        self.connection_test_running = False
        
        # Form variables
        self.host_var = tk.StringVar(value="localhost")
        self.port_var = tk.StringVar(value="5432")
        self.database_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        # UI components
        self.test_button: Optional[ttk.Button] = None
        self.save_button: Optional[ttk.Button] = None
        self.status_label: Optional[ttk.Label] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        
        # Entry widgets for focus management
        self.host_entry: Optional[ttk.Entry] = None
        self.port_entry: Optional[ttk.Entry] = None
        self.database_entry: Optional[ttk.Entry] = None
        self.username_entry: Optional[ttk.Entry] = None
        self.password_entry: Optional[ttk.Entry] = None
        
        self._load_existing_config()
    
    def _load_existing_config(self):
        """Load existing configuration if available."""
        try:
            config = self.config_manager.load_config()
            if config:
                self.host_var.set(config.get('host', 'localhost'))
                self.port_var.set(str(config.get('port', 5432)))
                self.database_var.set(config.get('database', ''))
                self.username_var.set(config.get('username', ''))
                self.password_var.set(config.get('password', ''))
        except Exception as e:
            logging.error(f"Error loading config: {e}")
    
    def show(self):
        """Show configuration window."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return
        
        self._create_window()
    
    def _create_window(self):
        """Create and configure the window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("⚙️ Configuración de Base de Datos")
        self.window.geometry("550x500")
        self.window.resizable(False, False)
        self.window.configure(bg='#f0f0f0')
        
        # Center window
        self._center_window()
        
        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._setup_config_theme()
        self._create_widgets()
    
    def _setup_config_theme(self):
        """Setup theme for config window."""
        style = ttk.Style()
        
        # Configure modern entry style
        style.configure('Config.TEntry',
                       fieldbackground='white',
                       borderwidth=1,
                       relief='solid',
                       focuscolor='#2E86AB',
                       font=('Arial', 10))
        
        # Configure label style  
        style.configure('Config.TLabel',
                       background='#f0f0f0',
                       foreground='#2C3E50',
                       font=('Arial', 10, 'bold'))
    
    def _center_window(self):
        """Center window on screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """Create and arrange UI widgets."""
        # Main frame with modern styling
        main_frame = tk.Frame(self.window, bg='#f0f0f0')
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.columnconfigure(1, weight=1)
        
        # Modern title header
        title_container = tk.Frame(main_frame, bg='#2E86AB', relief='flat', bd=0)
        title_container.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 25))
        title_container.columnconfigure(0, weight=1)
        
        title_label = tk.Label(title_container, 
                              text="🔧 Configuración PostgreSQL", 
                              font=("Arial", 16, "bold"),
                              bg='#2E86AB', fg='white',
                              pady=15)
        title_label.grid(row=0, column=0, sticky="ew")
        
        subtitle_label = tk.Label(title_container,
                                 text="Configure la conexión a su base de datos Odoo 17",
                                 font=("Arial", 9),
                                 bg='#2E86AB', fg='#E8E8E8',
                                 pady=10)
        subtitle_label.grid(row=1, column=0, sticky="ew")
        
        # Form fields with modern styling
        form_container = tk.Frame(main_frame, bg='white', relief='flat', bd=1)
        form_container.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        form_container.columnconfigure(1, weight=1)
        
        form_inner = ttk.Frame(form_container, padding="20")
        form_inner.grid(row=0, column=0, sticky="ew")
        form_container.columnconfigure(0, weight=1)
        form_inner.columnconfigure(1, weight=1)
        
        row = 0
        
        # Host with icon
        host_label = ttk.Label(form_inner, text="🌐 Host del Servidor:", 
                              style="Config.TLabel")
        host_label.grid(row=row, column=0, sticky="w", pady=10)
        self.host_entry = ttk.Entry(form_inner, textvariable=self.host_var, 
                                   width=25, style="Config.TEntry")
        self.host_entry.grid(row=row, column=1, sticky="ew", pady=10, padx=(15, 0))
        row += 1
        
        # Port with icon
        port_label = ttk.Label(form_inner, text="🔌 Puerto:", 
                              style="Config.TLabel")
        port_label.grid(row=row, column=0, sticky="w", pady=10)
        self.port_entry = ttk.Entry(form_inner, textvariable=self.port_var, 
                                   width=25, style="Config.TEntry")
        self.port_entry.grid(row=row, column=1, sticky="ew", pady=10, padx=(15, 0))
        row += 1
        
        # Database with icon
        db_label = ttk.Label(form_inner, text="🗄️ Base de Datos:", 
                            style="Config.TLabel")
        db_label.grid(row=row, column=0, sticky="w", pady=10)
        self.database_entry = ttk.Entry(form_inner, textvariable=self.database_var, 
                                       width=25, style="Config.TEntry")
        self.database_entry.grid(row=row, column=1, sticky="ew", pady=10, padx=(15, 0))
        row += 1
        
        # Username with icon
        user_label = ttk.Label(form_inner, text="👤 Usuario:", 
                              style="Config.TLabel")
        user_label.grid(row=row, column=0, sticky="w", pady=10)
        self.username_entry = ttk.Entry(form_inner, textvariable=self.username_var, 
                                       width=25, style="Config.TEntry")
        self.username_entry.grid(row=row, column=1, sticky="ew", pady=10, padx=(15, 0))
        row += 1
        
        # Password with icon
        pass_label = ttk.Label(form_inner, text="🔒 Contraseña:", 
                              style="Config.TLabel")
        pass_label.grid(row=row, column=0, sticky="w", pady=10)
        self.password_entry = ttk.Entry(form_inner, textvariable=self.password_var, 
                                       show="*", width=25, style="Config.TEntry")
        self.password_entry.grid(row=row, column=1, sticky="ew", pady=10, padx=(15, 0))
        row += 1
        
        # Progress bar with modern styling (hidden initially)
        self.progress_container = tk.Frame(main_frame, bg='#f0f0f0')
        self.progress_container.grid(row=2, column=0, columnspan=2, sticky="ew", 
                               pady=15)
        self.progress_container.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(self.progress_container, mode='indeterminate',
                                           style='Modern.Horizontal.TProgressbar')
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        self.progress_container.grid_remove()  # Hide initially
        
        # Status container with modern styling
        status_container = tk.Frame(main_frame, bg='#E8F4FD', relief='flat', bd=1)
        status_container.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        status_container.columnconfigure(0, weight=1)
        
        status_inner = ttk.Frame(status_container, padding="10")
        status_inner.grid(row=0, column=0, sticky="ew")
        
        self.status_label = ttk.Label(status_inner, text="", 
                                     font=("Arial", 9),
                                     foreground="#2E86AB")
        self.status_label.grid(row=0, column=0, sticky="w")
        
        # Modern buttons container
        button_container = tk.Frame(main_frame, bg='white', relief='flat', bd=1)
        button_container.grid(row=4, column=0, columnspan=2, sticky="ew")
        
        button_frame = ttk.Frame(button_container, padding="15")
        button_frame.grid(row=0, column=0, sticky="ew")
        button_container.columnconfigure(0, weight=1)
        
        # Primary action buttons
        self.test_button = ttk.Button(button_frame, text="🔍 Probar Conexión", 
                                     command=self._test_connection,
                                     style="Accent.TButton")
        self.test_button.pack(side="left", padx=(0, 15), ipadx=10, ipady=3)
        
        self.save_button = ttk.Button(button_frame, text="💾 Guardar Configuración", 
                                     command=self._save_config,
                                     style="Success.TButton")
        self.save_button.pack(side="left", padx=(0, 15), ipadx=5, ipady=3)
        
        # Cancel button on the right
        ttk.Button(button_frame, text="❌ Cancelar", 
                  command=self._on_close).pack(side="right")
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Set focus to first empty field
        self._set_initial_focus()
    
    def _set_initial_focus(self):
        """Set focus to the first empty field."""
        try:
            # Focus on the first empty field
            if not self.host_var.get() and self.host_entry:
                self.host_entry.focus_set()
            elif not self.database_var.get() and self.database_entry:
                self.database_entry.focus_set()
            elif not self.username_var.get() and self.username_entry:
                self.username_entry.focus_set()
            elif self.password_entry:
                self.password_entry.focus_set()
            else:
                self.window.focus_set()
        except Exception:
            # If there's any error, just set focus to window
            self.window.focus_set()
    
    def _validate_form(self) -> tuple[bool, str]:
        """
        Validate form inputs.
        
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        # Check required fields
        if not self.host_var.get().strip():
            return False, "Host del servidor es requerido"
        
        if not self.database_var.get().strip():
            return False, "Nombre de la base de datos es requerido"
        
        if not self.username_var.get().strip():
            return False, "Usuario es requerido"
        
        if not self.password_var.get():
            return False, "Contraseña es requerida"
        
        # Validate port
        try:
            port = int(self.port_var.get())
            if port < 1 or port > 65535:
                return False, "Puerto debe estar entre 1 y 65535"
        except ValueError:
            return False, "Puerto debe ser un número válido"
        
        return True, ""
    
    def _get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return {
            'host': self.host_var.get().strip(),
            'port': int(self.port_var.get()),
            'database': self.database_var.get().strip(),
            'username': self.username_var.get().strip(),
            'password': self.password_var.get()
        }
    
    def _test_connection(self):
        """Test database connection in a separate thread."""
        if self.connection_test_running:
            return
        
        # Validate form first
        is_valid, error_msg = self._validate_form()
        if not is_valid:
            messagebox.showerror("Error de Validación", error_msg)
            return
        
        self.connection_test_running = True
        self._set_testing_state(True)
        
        # Run test in separate thread
        thread = threading.Thread(target=self._run_connection_test, daemon=True)
        thread.start()
    
    def _run_connection_test(self):
        """Run connection test in background thread."""
        try:
            config = self._get_config_dict()
            
            # Update UI on main thread
            self.window.after(0, lambda: self._update_status("Conectando...", "blue"))
            
            # Test connection
            db_connection = DatabaseConnection(config)
            success, message = db_connection.test_connection()
            db_connection.close_pool()
            
            # Update UI with result
            color = "green" if success else "red"
            self.window.after(0, lambda: self._update_status(message, color))
            
        except Exception as e:
            error_msg = f"Error durante prueba de conexión: {str(e)}"
            self.window.after(0, lambda: self._update_status(error_msg, "red"))
        
        finally:
            self.window.after(0, lambda: self._set_testing_state(False))
            self.connection_test_running = False
    
    def _set_testing_state(self, testing: bool):
        """Set UI state during connection testing."""
        if testing:
            self.progress_container.grid()
            self.progress_bar.start()
            self.test_button.configure(state="disabled", text="🔄 Probando...")
            self.save_button.configure(state="disabled")
        else:
            self.progress_bar.stop()
            self.progress_container.grid_remove()
            self.test_button.configure(state="normal", text="🔍 Probar Conexión")
            self.save_button.configure(state="normal")
    
    def _update_status(self, message: str, color: str = "black"):
        """Update status label with message and color."""
        self.status_label.configure(text=message, foreground=color)
    
    def _save_config(self):
        """Save configuration to database."""
        # Validate form
        is_valid, error_msg = self._validate_form()
        if not is_valid:
            messagebox.showerror("Error de Validación", error_msg)
            return
        
        try:
            config = self._get_config_dict()
            
            success = self.config_manager.save_config(
                config['host'],
                config['port'],
                config['database'],
                config['username'],
                config['password']
            )
            
            if success:
                messagebox.showinfo("Éxito", "Configuración guardada correctamente")
                
                # Call callback if provided
                if self.on_config_saved:
                    self.on_config_saved()
                
                self._on_close()
            else:
                messagebox.showerror("Error", "No se pudo guardar la configuración")
                
        except Exception as e:
            logging.error(f"Error saving config: {e}")
            messagebox.showerror("Error", f"Error al guardar configuración: {str(e)}")
    
    def _on_close(self):
        """Handle window close event."""
        if self.connection_test_running:
            if messagebox.askyesno("Confirmación", 
                                 "¿Cancelar prueba de conexión en curso?"):
                self.connection_test_running = False
            else:
                return
        
        if self.window:
            self.window.grab_release()
            self.window.destroy()
            self.window = None