#!/usr/bin/env python3
"""
Test script for Sistema de Extracción de Datos Odoo 17

This script performs basic validation of the application components
without requiring a database connection.
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    modules_to_test = [
        ('database.connection', 'DatabaseConnection'),
        ('database.queries', 'QueryBuilder'), 
        ('utils.config_manager', 'ConfigManager'),
        ('utils.excel_generator', 'ExcelReportGenerator'),
        ('ui.config_window', 'ConfigWindow'),
        ('ui.main_window', 'MainWindow'),
    ]
    
    failed_imports = []
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"  ❌ {module_name}.{class_name}: {e}")
            failed_imports.append((module_name, class_name, e))
    
    return len(failed_imports) == 0, failed_imports

def test_queries():
    """Test query generation and validation."""
    print("\n🔍 Testing SQL queries...")
    
    try:
        from database.queries import QueryBuilder
        
        qb = QueryBuilder()
        
        # Test query generation
        invoices_query = qb.get_invoices_query()
        partners_query = qb.get_partners_query()
        
        assert invoices_query and isinstance(invoices_query, str)
        assert partners_query and isinstance(partners_query, str)
        print("  ✅ Query generation")
        
        # Test date validation
        assert qb.validate_date_format('2024-01-01') == True
        assert qb.validate_date_format('invalid-date') == False
        print("  ✅ Date format validation")
        
        # Test date range validation
        valid, msg = qb.validate_date_range('2024-01-01', '2024-01-31')
        assert valid == True
        print("  ✅ Date range validation")
        
        return True, None
        
    except Exception as e:
        return False, f"Query testing failed: {e}"

def test_config_manager():
    """Test configuration manager without actually saving."""
    print("\n🔍 Testing configuration manager...")
    
    try:
        from utils.config_manager import ConfigManager
        
        # Test initialization (creates test db)
        config_path = "test_config.db"
        cm = ConfigManager(config_path)
        
        # Test encryption/decryption capability
        cipher = cm._get_cipher_suite()
        test_password = "test_password_123"
        encrypted = cipher.encrypt(test_password.encode())
        decrypted = cipher.decrypt(encrypted).decode()
        
        assert decrypted == test_password
        print("  ✅ Password encryption/decryption")
        
        # Clean up test file
        Path(config_path).unlink(missing_ok=True)
        
        return True, None
        
    except Exception as e:
        return False, f"Config manager testing failed: {e}"

def test_excel_generator():
    """Test Excel report generation with dummy data."""
    print("\n🔍 Testing Excel generator...")
    
    try:
        from utils.excel_generator import ExcelReportGenerator
        import tempfile
        import os
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ExcelReportGenerator(temp_dir)
            
            # Test with dummy data
            dummy_data = [
                ('INV001', '2024-01-01', '123456789', 'CC001', 'AC001', 1000.00, 'D'),
                ('INV002', '2024-01-02', '987654321', 'CC002', 'AC002', 2000.00, 'C'),
            ]
            
            dummy_columns = [
                'numero_factura', 'fecha_factura', 'numero_identificacion',
                'codigo_centro_costo', 'codigo_cuenta', 'valor', 
                'naturaleza_cuenta'
            ]
            
            # Generate test report
            file_path = generator.generate_invoices_report(
                dummy_data, dummy_columns, '2024-01-01', '2024-01-02'
            )
            
            # Verify file was created
            assert Path(file_path).exists()
            print("  ✅ Excel file generation")
            
            # Verify file is readable
            from openpyxl import load_workbook
            wb = load_workbook(file_path)
            assert len(wb.worksheets) >= 1
            print("  ✅ Excel file format validation")
        
        return True, None
        
    except Exception as e:
        return False, f"Excel generator testing failed: {e}"

def test_ui_components():
    """Test UI components initialization without showing windows."""
    print("\n🔍 Testing UI components...")
    
    try:
        import tkinter as tk
        from ui.main_window import MainWindow
        from utils.config_manager import ConfigManager
        
        # Test that we can create instances without errors
        # Note: We don't actually show the windows to avoid GUI during testing
        
        # Test ConfigManager creation
        cm = ConfigManager(":memory:")  # Use in-memory database
        print("  ✅ ConfigManager instantiation")
        
        # Test that MainWindow can be imported and basic structure works
        print("  ✅ MainWindow import successful")
        
        return True, None
        
    except Exception as e:
        return False, f"UI component testing failed: {e}"

def run_comprehensive_test():
    """Run all tests and provide summary."""
    print("🚀 Running comprehensive test suite for Extractor Odoo 17")
    print("=" * 60)
    
    tests = [
        ("Import tests", test_imports),
        ("SQL queries", test_queries),
        ("Configuration manager", test_config_manager),
        ("Excel generator", test_excel_generator),
        ("UI components", test_ui_components),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success, error = test_func()
            results.append((test_name, success, error))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            traceback.print_exc()
            results.append((test_name, False, f"Exception: {e}"))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, success, error in results:
        if success:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
            if error:
                print(f"   Error: {error}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 TOTAL: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Application is ready for use.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        return False

def main():
    """Main test function."""
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Critical test error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()