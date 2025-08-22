import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import threading
from datetime import datetime, date
import logging
import os
from typing import Optional

from database.connection import DatabaseConnection
from database.queries import QueryBuilder
from utils.config_manager import ConfigManager
from utils.excel_generator import ExcelReportGenerator
from ui.config_window import ConfigWindow


class MainWindow:
    """Main application window for report generation."""
    
    def __init__(self):
        """Initialize main window."""
        self.root = tk.Tk()
        self.config_manager = ConfigManager()
        self.query_builder = QueryBuilder()
        
        # UI State
        self.date_mode = tk.StringVar(value="single")  # "single" or "range"
        self.output_directory = tk.StringVar(value=os.path.expanduser("~/Desktop"))
        
        # Progress tracking
        self.operation_running = False
        self.current_operation = ""
        
        # UI Components
        self.start_date_entry: Optional[DateEntry] = None
        self.end_date_entry: Optional[DateEntry] = None
        self.generate_button: Optional[ttk.Button] = None
        self.config_button: Optional[ttk.Button] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.status_label: Optional[ttk.Label] = None
        self.log_text: Optional[tk.Text] = None
        
        self._setup_logging()
        self._create_window()
        self._check_initial_config()
    
    def _setup_modern_theme(self):
        """Setup modern theme and colors."""
        style = ttk.Style()
        
        # Configure modern colors
        colors = {
            'primary': '#2E86AB',      # Blue
            'secondary': '#A23B72',    # Purple
            'success': '#F18F01',      # Orange
            'bg_light': '#F5F5F5',     # Light gray
            'bg_medium': '#E8E8E8',    # Medium gray
            'text_dark': '#2C3E50',    # Dark blue-gray
            'accent': '#E74C3C'        # Red accent
        }
        
        # Configure ttk styles
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Accent.TButton',
                       background=colors['primary'],
                       foreground='white',
                       focuscolor='none',
                       borderwidth=0,
                       font=('Arial', 10, 'bold'))
        
        style.map('Accent.TButton',
                 background=[('active', colors['secondary']),
                           ('pressed', colors['secondary'])])
        
        style.configure('Success.TButton',
                       background=colors['success'],
                       foreground='white',
                       focuscolor='none',
                       borderwidth=0,
                       font=('Arial', 9))
        
        # Configure labelframe styles
        style.configure('Card.TLabelframe',
                       background=colors['bg_light'],
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Card.TLabelframe.Label',
                       background=colors['bg_light'],
                       foreground=colors['text_dark'],
                       font=('Arial', 10, 'bold'))
        
        # Configure entry styles
        style.configure('Modern.TEntry',
                       fieldbackground='white',
                       borderwidth=1,
                       relief='solid',
                       focuscolor=colors['primary'])
        
        # Configure combobox styles
        style.configure('Modern.TCombobox',
                       fieldbackground='white',
                       borderwidth=1,
                       arrowcolor=colors['primary'])
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('extractor.log'),
                logging.StreamHandler()
            ]
        )
    
    def _create_window(self):
        """Create and configure main window."""
        self.root.title("📊 Extractor de Datos Odoo 17")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Modern styling
        self.root.configure(bg='#f0f0f0')
        
        # Configure modern theme
        self._setup_modern_theme()
        
        # Center window
        self._center_window()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self._create_widgets()
        self._setup_menu()
        
        # Handle close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _center_window(self):
        """Center window on screen."""
        self.root.update_idletasks()
        width = 900
        height = 700
        
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """Create and arrange UI widgets."""
        # Main container with modern background
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)  # Log area expands
        
        # Modern title header with gradient-like effect
        title_frame = tk.Frame(main_frame, bg='#2E86AB', relief='flat', bd=0)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        title_frame.columnconfigure(0, weight=1)
        
        # Main title with icon
        title_label = tk.Label(title_frame, 
                              text="📊 Sistema de Extracción de Datos", 
                              font=("Arial", 18, "bold"),
                              bg='#2E86AB', fg='white',
                              pady=15)
        title_label.grid(row=0, column=0, sticky="ew")
        
        # Subtitle
        subtitle_label = tk.Label(title_frame,
                                 text="Odoo 17 - PostgreSQL • Reportes Excel",
                                 font=("Arial", 10),
                                 bg='#2E86AB', fg='#E8E8E8')
        subtitle_label.grid(row=1, column=0, sticky="ew", pady=10)
        
        # Date selection frame with modern styling
        date_frame = ttk.LabelFrame(main_frame, text="📅 Selección de Fechas", 
                                   padding="15", style="Card.TLabelframe")
        date_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        date_frame.columnconfigure(1, weight=1)
        
        # Date mode selection with modern radio buttons
        mode_frame = ttk.Frame(date_frame)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Create custom style for radio buttons
        style = ttk.Style()
        style.configure('Modern.TRadiobutton',
                       background='#F5F5F5',
                       focuscolor='none',
                       font=('Arial', 10))
        
        single_radio = ttk.Radiobutton(mode_frame, text="🗓️ Fecha específica", 
                                      variable=self.date_mode, value="single",
                                      command=self._on_date_mode_change,
                                      style='Modern.TRadiobutton')
        single_radio.pack(side="left", padx=(0, 30))
        
        range_radio = ttk.Radiobutton(mode_frame, text="📊 Rango de fechas", 
                                     variable=self.date_mode, value="range",
                                     command=self._on_date_mode_change,
                                     style='Modern.TRadiobutton')
        range_radio.pack(side="left")
        
        # Date inputs with modern styling
        start_label = ttk.Label(date_frame, text="Fecha inicio:", 
                               font=("Arial", 10, "bold"))
        start_label.grid(row=1, column=0, sticky="w", pady=8)
        
        self.start_date_entry = DateEntry(date_frame, width=15, 
                                         background='#2E86AB',
                                         foreground='white', 
                                         borderwidth=1,
                                         date_pattern='yyyy-mm-dd',
                                         maxdate=date.today(),
                                         font=('Arial', 10))
        self.start_date_entry.grid(row=1, column=1, sticky="w", pady=8, padx=(15, 0))
        
        end_label = ttk.Label(date_frame, text="Fecha fin:", 
                             font=("Arial", 10, "bold"))
        end_label.grid(row=2, column=0, sticky="w", pady=8)
        
        self.end_date_entry = DateEntry(date_frame, width=15,
                                       background='#2E86AB',
                                       foreground='white', 
                                       borderwidth=1,
                                       date_pattern='yyyy-mm-dd',
                                       maxdate=date.today(),
                                       font=('Arial', 10))
        self.end_date_entry.grid(row=2, column=1, sticky="w", pady=8, padx=(15, 0))
        
        # Initially disable end date
        self.end_date_entry.configure(state="disabled")
        
        # Output directory frame with modern styling
        output_frame = ttk.LabelFrame(main_frame, text="📁 Carpeta de Destino", 
                                     padding="15", style="Card.TLabelframe")
        output_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        output_frame.columnconfigure(0, weight=1)
        
        output_dir_frame = ttk.Frame(output_frame)
        output_dir_frame.grid(row=0, column=0, sticky="ew")
        output_dir_frame.columnconfigure(0, weight=1)
        
        output_entry = ttk.Entry(output_dir_frame, 
                               textvariable=self.output_directory, 
                               state="readonly",
                               style="Modern.TEntry",
                               font=("Arial", 10))
        output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        browse_button = ttk.Button(output_dir_frame, text="🗂️ Examinar...", 
                                  command=self._select_output_directory,
                                  style="Success.TButton")
        browse_button.grid(row=0, column=1)
        
        # Modern control buttons with card-like container
        control_container = tk.Frame(main_frame, bg='white', relief='flat', bd=1)
        control_container.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        
        control_frame = ttk.Frame(control_container, padding="15")
        control_frame.grid(row=0, column=0, sticky="ew")
        control_container.columnconfigure(0, weight=1)
        control_frame.columnconfigure(2, weight=1)  # Spacer column
        
        # Primary action button with icon
        self.generate_button = ttk.Button(control_frame, 
                                         text="🚀 Generar Reportes", 
                                         command=self._generate_reports, 
                                         style="Accent.TButton")
        self.generate_button.grid(row=0, column=0, padx=(0, 15), ipadx=10, ipady=5)
        
        # Secondary buttons
        self.config_button = ttk.Button(control_frame, 
                                       text="⚙️ Configurar BD", 
                                       command=self._show_config,
                                       style="Success.TButton")
        self.config_button.grid(row=0, column=1, padx=(0, 15))
        
        # Utility buttons on the right
        util_frame = ttk.Frame(control_frame)
        util_frame.grid(row=0, column=3, sticky="e")
        
        ttk.Button(util_frame, text="🧹 Limpiar Log", 
                  command=self._clear_log).pack(side="left", padx=(0, 10))
        
        ttk.Button(util_frame, text="❌ Salir", 
                  command=self._on_close).pack(side="left")
        
        # Modern progress bar with custom style
        progress_container = tk.Frame(main_frame, bg='#f0f0f0')
        progress_container.grid(row=4, column=0, sticky="ew", pady=10)
        progress_container.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_container, mode='indeterminate',
                                           style='Modern.Horizontal.TProgressbar')
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        
        # Configure progress bar style
        style = ttk.Style()
        style.configure('Modern.Horizontal.TProgressbar',
                       background='#2E86AB',
                       troughcolor='#E8E8E8',
                       borderwidth=0,
                       lightcolor='#2E86AB',
                       darkcolor='#2E86AB')
        
        # Status container with modern styling
        status_container = tk.Frame(main_frame, bg='#E8F4FD', relief='flat', bd=1)
        status_container.grid(row=5, column=0, sticky="ew", pady=(0, 15))
        
        status_inner = ttk.Frame(status_container, padding="10")
        status_inner.grid(row=0, column=0, sticky="ew")
        status_container.columnconfigure(0, weight=1)
        
        # Status with icon
        status_icon = ttk.Label(status_inner, text="✅", font=("Arial", 12))
        status_icon.grid(row=0, column=0, padx=(0, 10))
        
        self.status_label = ttk.Label(status_inner, text="Listo para generar reportes", 
                                     font=("Arial", 10, "bold"),
                                     foreground="#2E86AB")
        self.status_label.grid(row=0, column=1, sticky="w")
        
        # Modern log area with enhanced styling
        log_frame = ttk.LabelFrame(main_frame, text="📋 Registro de Actividades", 
                                  padding="10", style="Card.TLabelframe")
        log_frame.grid(row=6, column=0, sticky="nsew", pady=(0, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Text widget with modern styling
        text_container = tk.Frame(log_frame, bg='white', relief='flat', bd=1)
        text_container.grid(row=0, column=0, sticky="nsew")
        text_container.columnconfigure(0, weight=1)
        text_container.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(text_container, 
                               height=10, 
                               wrap=tk.WORD,
                               font=("Consolas", 9),
                               bg='#FAFAFA',
                               fg='#2C3E50',
                               relief='flat',
                               bd=0,
                               selectbackground='#2E86AB',
                               selectforeground='white',
                               insertbackground='#2E86AB')
        
        # Modern scrollbar
        scrollbar = ttk.Scrollbar(text_container, orient="vertical", 
                                 command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self._log("🎉 Aplicación iniciada correctamente")
    
    def _setup_menu(self):
        """Setup application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Configurar Base de Datos", command=self._show_config)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self._on_close)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self._show_about)
    
    def _on_date_mode_change(self):
        """Handle date mode change (single vs range)."""
        if self.date_mode.get() == "single":
            self.end_date_entry.configure(state="disabled")
        else:
            self.end_date_entry.configure(state="normal")
    
    def _select_output_directory(self):
        """Open directory selection dialog."""
        directory = filedialog.askdirectory(
            title="Seleccionar carpeta de destino",
            initialdir=self.output_directory.get()
        )
        if directory:
            self.output_directory.set(directory)
    
    def _check_initial_config(self):
        """Check if database configuration exists."""
        if not self.config_manager.config_exists():
            self._log("No se encontró configuración de base de datos")
            self._update_status("Configuración requerida", "orange")
            
            # Ask user if they want to configure now
            if messagebox.askyesno("Configuración Requerida", 
                                 "No se encontró configuración de base de datos.\n"
                                 "¿Desea configurarla ahora?"):
                self._show_config()
        else:
            self._update_status("Configuración cargada", "green")
            self._log("Configuración de base de datos cargada")
    
    def _show_config(self):
        """Show database configuration window."""
        config_window = ConfigWindow(
            self.root, 
            self.config_manager,
            self._on_config_saved
        )
        config_window.show()
    
    def _on_config_saved(self):
        """Callback when configuration is saved."""
        self._update_status("Configuración actualizada", "green")
        self._log("Configuración de base de datos actualizada")
    
    def _validate_inputs(self) -> tuple[bool, str]:
        """
        Validate user inputs before generating reports.
        
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        # Check if config exists
        if not self.config_manager.config_exists():
            return False, "Debe configurar la base de datos primero"
        
        # Validate dates
        start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
        
        if self.date_mode.get() == "range":
            end_date = self.end_date_entry.get_date().strftime('%Y-%m-%d')
            is_valid, message = self.query_builder.validate_date_range(start_date, end_date)
            if not is_valid:
                return False, message
        else:
            # Single date validation
            if not self.query_builder.validate_date_format(start_date):
                return False, "Formato de fecha inválido"
        
        # Check output directory
        output_dir = self.output_directory.get()
        if not os.path.exists(output_dir):
            return False, "La carpeta de destino no existe"
        
        if not os.access(output_dir, os.W_OK):
            return False, "Sin permisos de escritura en la carpeta de destino"
        
        return True, ""
    
    def _generate_reports(self):
        """Generate reports in a separate thread."""
        if self.operation_running:
            return
        
        # Validate inputs
        is_valid, error_msg = self._validate_inputs()
        if not is_valid:
            messagebox.showerror("Error de Validación", error_msg)
            return
        
        self.operation_running = True
        self._set_operation_state(True, "Generando reportes...")
        
        # Run in separate thread
        thread = threading.Thread(target=self._run_report_generation, daemon=True)
        thread.start()
    
    def _run_report_generation(self):
        """Run report generation in background thread."""
        try:
            # Prepare dates
            start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
            end_date = (self.end_date_entry.get_date().strftime('%Y-%m-%d') 
                       if self.date_mode.get() == "range" else start_date)
            
            self.root.after(0, lambda: self._log(f"Iniciando extracción para período: {start_date} - {end_date}"))
            
            # Load configuration
            config = self.config_manager.load_config()
            if not config:
                raise Exception("No se pudo cargar la configuración")
            
            # Test connection
            self.root.after(0, lambda: self._update_status("Conectando a base de datos...", "blue"))
            db_connection = DatabaseConnection(config)
            
            success, message = db_connection.test_connection()
            if not success:
                raise Exception(f"Error de conexión: {message}")
            
            self.root.after(0, lambda: self._log("Conexión establecida correctamente"))
            
            # Execute queries
            self.root.after(0, lambda: self._update_status("Extrayendo datos de facturas...", "blue"))
            
            # Get invoices data
            invoices_query = self.query_builder.get_invoices_query()
            invoices_data, invoices_columns = db_connection.execute_query(
                invoices_query, (start_date, end_date)
            )
            
            self.root.after(0, lambda: self._log(f"Facturas encontradas: {len(invoices_data)}"))
            
            # Get partners data
            self.root.after(0, lambda: self._update_status("Extrayendo datos de terceros...", "blue"))
            
            partners_query = self.query_builder.get_partners_query()
            partners_data, partners_columns = db_connection.execute_query(
                partners_query, (start_date, end_date)
            )
            
            self.root.after(0, lambda: self._log(f"Terceros encontrados: {len(partners_data)}"))
            
            # Close database connection
            db_connection.close_pool()
            
            # Check if we have data
            if not invoices_data and not partners_data:
                raise Exception("No se encontraron datos para el período seleccionado")
            
            # Generate Excel reports
            self.root.after(0, lambda: self._update_status("Generando archivos Excel...", "blue"))
            
            excel_generator = ExcelReportGenerator(self.output_directory.get())
            generated_files = []
            
            # Generate invoices report
            if invoices_data:
                invoices_file = excel_generator.generate_invoices_report(
                    invoices_data, invoices_columns, start_date, end_date
                )
                generated_files.append(invoices_file)
                self.root.after(0, lambda: self._log(f"Reporte de facturas generado: {os.path.basename(invoices_file)}"))
            
            # Generate partners report  
            if partners_data:
                partners_file = excel_generator.generate_partners_report(
                    partners_data, partners_columns, start_date, end_date
                )
                generated_files.append(partners_file)
                self.root.after(0, lambda: self._log(f"Reporte de terceros generado: {os.path.basename(partners_file)}"))
            
            # Save query history
            total_records = len(invoices_data) + len(partners_data)
            execution_time = 0  # Would need to track actual time
            self.config_manager.save_query_history(start_date, end_date, total_records, execution_time)
            
            # Success
            self.root.after(0, lambda: self._update_status("Reportes generados exitosamente", "green"))
            self.root.after(0, lambda: self._log(f"Proceso completado. Archivos generados: {len(generated_files)}"))
            
            # Show success message
            success_msg = f"Reportes generados exitosamente:\n\n"
            for file_path in generated_files:
                success_msg += f"• {os.path.basename(file_path)}\n"
            success_msg += f"\nUbicación: {self.output_directory.get()}"
            
            self.root.after(0, lambda: messagebox.showinfo("Éxito", success_msg))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._log(f"ERROR: {error_msg}"))
            self.root.after(0, lambda: self._update_status(f"Error: {error_msg[:50]}...", "red"))
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        finally:
            self.operation_running = False
            self.root.after(0, lambda: self._set_operation_state(False))
    
    def _set_operation_state(self, running: bool, status_text: str = ""):
        """Set UI state during long operations."""
        if running:
            self.progress_bar.start()
            self.generate_button.configure(state="disabled")
            self.config_button.configure(state="disabled")
            if status_text:
                self._update_status(status_text, "blue")
        else:
            self.progress_bar.stop()
            self.generate_button.configure(state="normal")
            self.config_button.configure(state="normal")
            if not status_text:
                self._update_status("Listo", "green")
    
    def _update_status(self, message: str, color: str = "black"):
        """Update status label."""
        self.status_label.configure(text=message, foreground=color)
    
    def _log(self, message: str):
        """Add message to log area."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
        # Log to file as well
        logging.info(message)
    
    def _clear_log(self):
        """Clear log text area."""
        self.log_text.delete(1.0, tk.END)
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
Sistema de Extracción de Datos de Facturación Odoo 17

Versión: 1.0
Desarrollado con Python y tkinter

Características:
• Conexión a base de datos PostgreSQL
• Extracción de datos de facturas y terceros  
• Generación de reportes Excel
• Interfaz gráfica intuitiva

© 2024
        """
        messagebox.showinfo("Acerca de", about_text.strip())
    
    def _on_close(self):
        """Handle application close."""
        if self.operation_running:
            if not messagebox.askyesno("Confirmación", 
                                     "¿Cancelar operación en curso y salir?"):
                return
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the application main loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._log("Aplicación interrumpida por el usuario")
        except Exception as e:
            logging.error(f"Error crítico en la aplicación: {e}")
            messagebox.showerror("Error Crítico", f"Error inesperado: {e}")
        finally:
            logging.info("Aplicación finalizada")