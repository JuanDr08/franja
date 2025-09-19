# Sistema de Extracción de Datos de Facturación Odoo 17

Una aplicación de escritorio desarrollada en Python con tkinter para extraer datos de facturación y terceros desde una base de datos PostgreSQL de Odoo 17 y generar reportes en Excel.

## 🚀 Características

- **Interfaz gráfica intuitiva** con tkinter
- **Conexión segura** a PostgreSQL con manejo de pools de conexión
- **Configuración persistente** con encriptación de contraseñas
- **Extracción de datos** de facturas y terceros con queries optimizadas
- **Generación de reportes Excel** con formato profesional
- **Validación de fechas** y manejo robusto de errores
- **Empaquetado como ejecutable** independiente (.exe)

## 📋 Requisitos del Sistema

### Requisitos Mínimos
- **Sistema Operativo:** Windows 10+, macOS 10.14+, Linux Ubuntu 18.04+
- **RAM:** Mínimo 4GB
- **Espacio en disco:** 100MB libres
- **Python:** 3.8+ (para desarrollo)
- **PostgreSQL:** Acceso a base de datos Odoo 17

### Dependencias de Python
```
psycopg2-binary==2.9.9
pandas==2.2.2
openpyxl==3.1.2
tkcalendar==1.6.1
cryptography==41.0.7
pyinstaller==6.3.0
```

## 🛠️ Instalación y Configuración

### Para Usuarios (Ejecutable)
1. Descargue el archivo ejecutable desde la carpeta `dist/`
2. Ejecute `ExtractorOdoo17.exe` (Windows) o el equivalente en su SO
3. Configure la conexión a la base de datos en la primera ejecución

### Para Desarrolladores

1. **Clonar el repositorio:**
```bash
git clone <repository-url>
cd franjaApp
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Ejecutar aplicación:**
```bash
python main.py
```

## 🏗️ Estructura del Proyecto

```
franjaApp/
├── main.py                 # Punto de entrada principal
├── requirements.txt        # Dependencias Python
├── build.spec             # Configuración PyInstaller  
├── build.py               # Script de construcción
├── README.md              # Documentación
├── database/
│   ├── connection.py      # Manejo de conexiones PostgreSQL
│   └── queries.py         # Queries SQL y validaciones
├── ui/
│   ├── main_window.py     # Ventana principal
│   └── config_window.py   # Ventana de configuración
└── utils/
    ├── config_manager.py  # Gestión de configuración SQLite
    └── excel_generator.py # Generación de reportes Excel
```

## 💻 Uso de la Aplicación

### Primera Configuración

1. Al abrir la aplicación por primera vez, haga clic en **"Configurar BD"**
2. Ingrese los datos de conexión:
   - **Host:** Dirección IP o nombre del servidor PostgreSQL
   - **Puerto:** Puerto de conexión (por defecto 5432)
   - **Base de datos:** Nombre de la base de datos Odoo
   - **Usuario:** Usuario de PostgreSQL
   - **Contraseña:** Contraseña del usuario

3. Haga clic en **"Probar Conexión"** para verificar la conectividad
4. Si la prueba es exitosa, haga clic en **"Guardar Configuración"**

### Generar Reportes

1. **Seleccionar fechas:**
   - **Fecha específica:** Para datos de un solo día
   - **Rango de fechas:** Para un período específico

2. **Configurar destino:**
   - Haga clic en **"Examinar..."** para seleccionar carpeta de destino
   - Por defecto usa el Escritorio del usuario

3. **Generar:**
   - Haga clic en **"Generar Reportes"**
   - Espere a que termine el procesamiento
   - Los archivos Excel se crearán automáticamente

### Archivos Generados

- **`facturas_[fecha].xlsx`** - Datos de facturación con campos:
  - número_factura, fecha_factura, numero_identificacion
  - codigo_centro_costo, codigo_cuenta, valor
  - naturaleza_cuenta

- **`terceros_[fecha].xlsx`** - Datos de terceros con campos:
  - nombre, tipo_identificacion, identidad
  - tipo_empresa, mail, movil, direccion

## 🔧 Construcción del Ejecutable

### Automática (Recomendado)
```bash
python build.py
```

### Manual con PyInstaller
```bash
# Limpiar builds anteriores
rm -rf build dist

# Generar ejecutable
pyinstaller build.spec --clean --noconfirm

# O usar comando directo
pyinstaller main.py --name ExtractorOdoo17 --onefile --windowed
```

El ejecutable se generará en la carpeta `dist/`

## 🗃️ Base de Datos

### Configuración Local (SQLite)
La aplicación usa SQLite para almacenar:
- Configuración de conexión (con contraseñas encriptadas)
- Historial de consultas ejecutadas

Archivo: `config.db` (creado automáticamente)

### Tablas de Odoo Requeridas
La aplicación consulta las siguientes tablas de Odoo 17:
- `account_move` - Facturas y documentos contables
- `res_partner` - Terceros/Partners  
- `account_move_line` - Líneas de movimientos contables
- `account_account` - Plan de cuentas
- `account_analytic_account` - Centros de costo
- `l10n_latam_identification_type` - Tipos de identificación

## 🔒 Seguridad

- **Contraseñas encriptadas** usando cryptography con PBKDF2
- **Queries parametrizadas** para prevenir SQL injection
- **Validación de entradas** en todos los formularios
- **Manejo seguro de errores** sin exposición de datos sensibles

## 📊 Rendimiento

- **Pool de conexiones** para optimizar acceso a BD
- **Timeouts configurables** para evitar bloqueos
- **Procesamiento en threads** para mantener UI responsiva
- **Validación de datos** antes de generar reportes

## 🐛 Solución de Problemas

### Errores Comunes

**Error de conexión a base de datos:**
- Verificar credenciales y conectividad de red
- Confirmar que PostgreSQL acepta conexiones externas
- Revisar firewall y configuración de `pg_hba.conf`

**Archivo Excel no se puede generar:**
- Verificar permisos de escritura en carpeta destino
- Cerrar archivos Excel abiertos con el mismo nombre
- Verificar espacio disponible en disco

**Aplicación no inicia:**
- Revisar archivo `extractor.log` para detalles
- Verificar que todas las dependencias estén instaladas
- En sistemas Linux, verificar permisos de ejecución

### Logs
Los logs se guardan en:
- **Desarrollo:** `extractor.log` en directorio de la aplicación
- **Ejecutable:** Junto al archivo ejecutable

## 🔄 Actualizaciones y Mantenimiento

### Actualizar Dependencias
```bash
pip install --upgrade -r requirements.txt
```

### Regenerar Ejecutable
```bash
python build.py
```

### Backup de Configuración
Respaldar el archivo `config.db` para preservar configuraciones

## 📝 Notas de Desarrollo

### Buenas Prácticas Implementadas
- Separación de responsabilidades por módulos
- Manejo de errores con logging detallado
- Interfaz de usuario responsiva con threads
- Configuración centralizada y persistente
- Validación exhaustiva de datos de entrada

### Arquitectura
- **Modelo-Vista:** Separación entre lógica de negocio y UI
- **Inyección de dependencias:** ConfigManager pasado a componentes
- **Patrón Observer:** Callbacks para comunicación entre ventanas
- **Context Managers:** Manejo automático de recursos de BD

## 📄 Licencia

Este proyecto está desarrollado para uso interno de la organización.

## 👥 Soporte

Para soporte técnico o reportar problemas:
1. Revisar este README y los logs de la aplicación
2. Verificar la configuración de red y base de datos  
3. Contactar al equipo de desarrollo con detalles específicos del error

---

**Versión:** 1.0  
**Última actualización:** 2024  
**Tecnologías:** Python 3.8+, tkinter, PostgreSQL, SQLite, Excel