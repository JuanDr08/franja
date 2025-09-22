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
            am.sequence_prefix AS prefijo,
            am.sequence_number AS consecutivo,
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
            END AS naturaleza_cuenta

        FROM account_move am
            LEFT JOIN res_partner rp ON am.partner_id = rp.id
            LEFT JOIN l10n_latam_identification_type lit ON rp.l10n_latam_identification_type_id = lit.id
            LEFT JOIN account_move_line aml ON am.id = aml.move_id
            LEFT JOIN account_account aa ON aml.account_id = aa.id
            LEFT JOIN account_analytic_account aaa ON am.user_analytic_account_id = aaa.id

        WHERE 
            am.move_type IN ('out_invoice', 'in_invoice')
            AND COALESCE(am.invoice_date, am.date) BETWEEN %s AND %s
            AND am.state = 'posted'

            AND NOT (
                aa.code IS NULL 
                AND (aml.debit IS NULL OR aml.debit = 0) 
                AND (aml.credit IS NULL OR aml.credit = 0)
            )

        ORDER BY 
            COALESCE(am.invoice_date, am.date) DESC;
        """
    
    @staticmethod
    def get_partners_query() -> str:
        """
        Get the SQL query for extracting partner (third parties) data based on creation date.
        
        Returns:
            Parameterized SQL query string
        """
        return """
        SELECT DISTINCT
            rp.name AS nombre_completo,
            CASE 
                WHEN rp.is_company = true THEN 'Empresa'
                WHEN rp.is_company = false THEN 'Persona'
                ELSE 'No definido'
            END AS tipo_empresa,
            CASE 
                WHEN rp.is_company = true THEN '1'
                WHEN rp.is_company = false THEN '0'
                ELSE 'No definido'
            END AS naturaleza,
            CONCAT_WS(', ', 
                NULLIF(TRIM(rp.street), ''), 
                NULLIF(TRIM(rp.street2), ''),
                NULLIF(TRIM(rp.city), '')
            ) AS direccion,
            COALESCE(rp.email_edi, '') AS email,
            
            -- TIPO DE IDENTIFICACIÓN
            COALESCE(lit.name->>'en_US', 'Sin tipo') AS tipo_identificacion,
            
            -- IDENTIFICACIÓN (CON LÓGICA DE GUIÓN)
            CASE 
                WHEN rp.is_company = true 
                    AND rp.vat IS NOT NULL 
                    AND LENGTH(TRIM(rp.vat)) > 1 
                    AND SUBSTRING(TRIM(rp.vat), LENGTH(TRIM(rp.vat)) - 1, 1) = '-' THEN 
                    LEFT(TRIM(rp.vat), LENGTH(TRIM(rp.vat)) - 2)  -- Quita los dos últimos caracteres (guión + dígito)
                ELSE COALESCE(rp.vat, 'Sin identificación')  -- Mantiene completo si no cumple condiciones
            END AS identidad,
            
            -- DÍGITO DE VERIFICACIÓN (CON LÓGICA DE GUIÓN)
            CASE 
                WHEN rp.is_company = true 
                    AND rp.vat IS NOT NULL 
                    AND LENGTH(TRIM(rp.vat)) > 1 
                    AND SUBSTRING(TRIM(rp.vat), LENGTH(TRIM(rp.vat)) - 1, 1) = '-' THEN 
                    RIGHT(TRIM(rp.vat), 1)  -- Extrae el último dígito
                ELSE '0'  -- Por defecto 0 si no cumple condiciones
            END AS dv,
            
            -- CLASE
            CASE 
                WHEN rp.is_company = true THEN 'A'  -- Empresa = A
                ELSE 'C'  -- Persona = C
            END AS clase,
            
            -- CONTACTO
            COALESCE(rp.phone, '') AS movil,
            'CLIENTES' AS CARTERA
            
        FROM res_partner rp
            LEFT JOIN l10n_latam_identification_type lit ON rp.l10n_latam_identification_type_id = lit.id
            
            -- JOIN PARA FILTRAR SOLO TERCEROS QUE HAN PARTICIPADO EN FACTURACIÓN
            INNER JOIN account_move am ON rp.id = am.partner_id

        WHERE 
            -- FILTRO: SOLO TERCEROS CON FACTURAS O NOTAS DE CRÉDITO
            am.move_type IN ('out_invoice', 'in_invoice', 'out_refund', 'in_refund')
            
            -- SOLO DOCUMENTOS CONTABILIZADOS
            AND am.state = 'posted'
            
            -- FILTRO POR FECHA DE CREACIÓN DEL TERCERO
            AND rp.create_date::date BETWEEN %s AND %s
            
            -- SOLO TERCEROS ACTIVOS
            AND rp.active = true

        ORDER BY 
            rp.name ASC;
        """
    
    @staticmethod
    def get_credit_notes_query() -> str:
        """
        Get the SQL query for extracting credit notes data.
        
        Returns:
            Parameterized SQL query string
        """
        return """
        SELECT DISTINCT
            am.sequence_prefix AS prefijo,
            am.sequence_number AS consecutivo,
            rp.vat AS numero_identificacion,
            COALESCE(am.invoice_date, am.date) AS fecha_factura,
            aaa.code AS codigo_centro_costo,
            
            -- CODIGO CUENTA con lógica especial para notas de crédito
            CASE 
                WHEN aa.code IN ('41353801', '41353802', '41353803') THEN
                    REPLACE(aa.code, '35', '75')  -- Cambia 41353801 -> 41753801, etc.
                ELSE aa.code
            END AS codigo_cuenta,
            
            -- VALOR UNIFICADO (siempre positivo)
            COALESCE(NULLIF(aml.debit, 0), NULLIF(aml.credit, 0), 0) AS valor,
            
            -- NATURALEZA DE CUENTA
            CASE 
                WHEN aml.credit > 0 THEN 'C'
                WHEN aml.debit > 0 THEN 'D'
                ELSE 'N'
            END AS naturaleza_cuenta,
            
            -- REFERENCIA A FACTURA ORIGINAL
            CASE 
                WHEN am.invoice_origin IS NOT NULL AND TRIM(am.invoice_origin) != '' AND fo.sequence_prefix IS NOT NULL
                THEN fo.sequence_prefix  -- Prefijo de la factura original encontrada
                ELSE COALESCE(am.ref, am.invoice_origin, '')  -- Fallback si no se encuentra
            END AS prefijo_factura_original,
            
            -- CONSECUTIVO DE FACTURA ORIGINAL
            CASE 
                WHEN am.invoice_origin IS NOT NULL AND TRIM(am.invoice_origin) != '' AND fo.sequence_number IS NOT NULL
                THEN fo.sequence_number  -- Consecutivo de la factura original encontrada
                ELSE NULL  -- NULL si no se encuentra la factura
            END AS consecutivo_factura_original,
            
            -- N. VENDEDOR (campo constante)
            '900099819' AS n_vendedor

        FROM account_move am
            LEFT JOIN res_partner rp ON am.partner_id = rp.id
            LEFT JOIN l10n_latam_identification_type lit ON rp.l10n_latam_identification_type_id = lit.id
            LEFT JOIN account_move_line aml ON am.id = aml.move_id
            LEFT JOIN account_account aa ON aml.account_id = aa.id
            LEFT JOIN account_analytic_account aaa ON am.user_analytic_account_id = aaa.id
            
            -- JOIN con factura original usando invoice_origin
            LEFT JOIN account_move fo ON am.invoice_origin = fo.invoice_origin
                                       AND fo.move_type IN ('out_invoice', 'in_invoice')
                                       AND fo.state = 'posted'

        WHERE 
            am.move_type IN ('out_refund', 'in_refund')
            AND COALESCE(am.invoice_date, am.date) BETWEEN %s AND %s
            AND am.state = 'posted'

            AND NOT (
                aa.code IS NULL 
                AND (aml.debit IS NULL OR aml.debit = 0) 
                AND (aml.credit IS NULL OR aml.credit = 0)
            )

        ORDER BY 
            COALESCE(am.invoice_date, am.date) DESC;
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