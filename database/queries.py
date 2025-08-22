from typing import Tuple, List
from datetime import datetime, date


class QueryBuilder:
    """SQL query builder for Odoo 17 billing data extraction."""
    
    @staticmethod
    def get_invoices_query() -> str:
        """
        Get the SQL query for extracting invoice data.
        
        Returns:
            Parameterized SQL query string
        """
        return """
        SELECT DISTINCT
            am.name AS numero_factura,
            rp.vat AS numero_identificacion,
            COALESCE(am.invoice_date, am.date) AS fecha_factura,
            aaa.code AS codigo_centro_costo,
            aa.code AS codigo_cuenta,

            -- VALOR UNIFICADO (siempre positivo)
            COALESCE(NULLIF(aml.debit, 0), NULLIF(aml.credit, 0), 0) AS valor,

            -- NATURALEZA DE CUENTA
            CASE 
                WHEN aml.credit > 0 THEN 'C'
                WHEN aml.debit > 0 THEN 'D'
                ELSE 'N'
            END AS naturaleza_cuenta,

            -- N_INTERNACIONAL
            'F' AS n_internacional

        FROM account_move am
            LEFT JOIN res_partner rp ON am.partner_id = rp.id
            LEFT JOIN l10n_latam_identification_type lit ON rp.l10n_latam_identification_type_id = lit.id
            LEFT JOIN account_move_line aml ON am.id = aml.move_id
            LEFT JOIN account_account aa ON aml.account_id = aa.id
            LEFT JOIN account_analytic_account aaa ON am.user_analytic_account_id = aaa.id

        WHERE 
            am.move_type IN ('out_invoice', 'in_invoice', 'out_refund', 'in_refund')
            AND COALESCE(am.invoice_date, am.date) BETWEEN %s AND %s
            AND am.state = 'posted'

        ORDER BY 
            COALESCE(am.invoice_date, am.date) DESC, 
            am.name ASC;
        """
    
    @staticmethod
    def get_partners_query() -> str:
        """
        Get the SQL query for extracting partner (third parties) data.
        
        Returns:
            Parameterized SQL query string
        """
        return """
        SELECT DISTINCT
            -- DATOS BÁSICOS DEL TERCERO
            rp.id AS tercero_id,
            rp.name AS nombre,
            
            -- NOMBRE COMPLETO (para personas naturales)
            CASE 
                WHEN rp.is_company = false AND rp.first_name IS NOT NULL THEN
                    TRIM(CONCAT_WS(' ', rp.first_name, rp.other_names, rp.surname, rp.second_surname))
                ELSE rp.name
            END AS nombre_completo,
            
            -- TIPO DE IDENTIFICACIÓN
            COALESCE(lit.name->>'en_US', 'Sin tipo') AS tipo_identificacion,
            
            -- IDENTIFICACIÓN
            COALESCE(rp.vat, 'Sin identificación') AS identidad,

            CASE 
                WHEN rp.is_company = true THEN 'Empresa'
                WHEN rp.is_company = false THEN 'Persona'
                ELSE 'No definido'
            END AS tipo_empresa,
            
            -- CONTACTO
            COALESCE(rp.email_normalized, '') AS mail,
            COALESCE(rp.phone, '') AS movil,
            
            -- DIRECCIÓN
            CONCAT_WS(', ', 
                NULLIF(TRIM(rp.street), ''), 
                NULLIF(TRIM(rp.street2), ''),
                NULLIF(TRIM(rp.city), '')
            ) AS direccion

        FROM res_partner rp
            LEFT JOIN l10n_latam_identification_type lit ON rp.l10n_latam_identification_type_id = lit.id
            
            -- JOIN PARA FILTRAR SOLO TERCEROS QUE HAN PARTICIPADO EN FACTURACIÓN
            INNER JOIN account_move am ON rp.id = am.partner_id

        WHERE 
            -- FILTRO: SOLO TERCEROS CON FACTURAS O NOTAS DE CRÉDITO
            am.move_type IN ('out_invoice', 'in_invoice', 'out_refund', 'in_refund')
            
            -- SOLO DOCUMENTOS CONTABILIZADOS
            AND am.state = 'posted'
            
            -- FILTRO POR FECHAS
            AND COALESCE(am.invoice_date, am.date) BETWEEN %s AND %s
            
            -- SOLO TERCEROS ACTIVOS
            AND rp.active = true

        ORDER BY 
            rp.name ASC;
        """
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """
        Validate date format (YYYY-MM-DD).
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid format, False otherwise
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, str]:
        """
        Validate date range.
        
        Args:
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        # Validate date formats
        if not QueryBuilder.validate_date_format(start_date):
            return False, "Invalid start date format. Use YYYY-MM-DD"
        
        if not QueryBuilder.validate_date_format(end_date):
            return False, "Invalid end date format. Use YYYY-MM-DD"
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Check if start date is not after end date
            if start > end:
                return False, "Start date cannot be after end date"
            
            # Check if dates are not too far in the future
            today = date.today()
            if start > today or end > today:
                return False, "Dates cannot be in the future"
            
            # Optional: Check if date range is not too large (e.g., more than 1 year)
            if (end - start).days > 365:
                return False, "Date range cannot exceed 365 days"
            
            return True, "Valid date range"
            
        except ValueError as e:
            return False, f"Date validation error: {str(e)}"
    
    @staticmethod
    def prepare_query_params(start_date: str, end_date: str = None) -> Tuple[str, str]:
        """
        Prepare query parameters for single date or date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), if None uses start_date
            
        Returns:
            Tuple of (formatted_start_date, formatted_end_date)
        """
        if end_date is None:
            end_date = start_date
        
        return start_date, end_date
    
    @staticmethod
    def get_test_connection_query() -> str:
        """
        Get a simple query to test database connection.
        
        Returns:
            Simple test query
        """
        return "SELECT version(), current_database(), current_user, now();"
    
    @staticmethod
    def get_table_existence_query() -> str:
        """
        Get query to check if required Odoo tables exist.
        
        Returns:
            Query to check table existence
        """
        return """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN (
            'account_move', 
            'res_partner', 
            'account_move_line', 
            'account_account', 
            'account_analytic_account',
            'l10n_latam_identification_type'
        )
        ORDER BY table_name;
        """
    
    @staticmethod
    def get_record_count_query(table_name: str) -> str:
        """
        Get query to count records in a specific table.
        
        Args:
            table_name: Name of the table to count
            
        Returns:
            Count query for the specified table
        """
        # Validate table name to prevent SQL injection
        allowed_tables = [
            'account_move', 
            'res_partner', 
            'account_move_line', 
            'account_account'
        ]
        
        if table_name not in allowed_tables:
            raise ValueError(f"Table name '{table_name}' not allowed")
        
        return f"SELECT COUNT(*) FROM {table_name};"