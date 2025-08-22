import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging


class ConfigManager:
    """Manages application configuration using SQLite with encrypted passwords."""
    
    def __init__(self, config_path: str = "config.db"):
        self.config_path = config_path
        self.salt = b'franjaapp_salt_key_123'  # In production, use random salt per installation
        self._init_database()
        
    def _get_cipher_suite(self):
        """Generate cipher suite for password encryption."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"franjaapp_master_key"))
        return Fernet(key)
    
    def _init_database(self):
        """Initialize SQLite database with config table."""
        try:
            conn = sqlite3.connect(self.config_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    database TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY,
                    date_start TEXT NOT NULL,
                    date_end TEXT NOT NULL,
                    records_found INTEGER,
                    execution_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
            raise
    
    def save_config(self, host: str, port: int, database: str, 
                   username: str, password: str) -> bool:
        """Save database configuration with encrypted password."""
        try:
            cipher_suite = self._get_cipher_suite()
            encrypted_password = cipher_suite.encrypt(password.encode()).decode()
            
            conn = sqlite3.connect(self.config_path)
            cursor = conn.cursor()
            
            # Check if config exists
            cursor.execute("SELECT id FROM config LIMIT 1")
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute("""
                    UPDATE config SET 
                    host = ?, port = ?, database = ?, 
                    username = ?, password = ?,
                    updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (host, port, database, username, encrypted_password, exists[0]))
            else:
                cursor.execute("""
                    INSERT INTO config (host, port, database, username, password)
                    VALUES (?, ?, ?, ?, ?)
                """, (host, port, database, username, encrypted_password))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Error saving config: {e}")
            return False
    
    def load_config(self) -> dict:
        """Load database configuration and decrypt password."""
        try:
            conn = sqlite3.connect(self.config_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT host, port, database, username, password 
                FROM config ORDER BY updated_at DESC LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                host, port, database, username, encrypted_password = result
                
                cipher_suite = self._get_cipher_suite()
                decrypted_password = cipher_suite.decrypt(
                    encrypted_password.encode()
                ).decode()
                
                return {
                    'host': host,
                    'port': port,
                    'database': database,
                    'username': username,
                    'password': decrypted_password
                }
            
            return {}
            
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}
    
    def config_exists(self) -> bool:
        """Check if configuration exists."""
        try:
            conn = sqlite3.connect(self.config_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM config")
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except:
            return False
    
    def save_query_history(self, date_start: str, date_end: str, 
                          records_found: int, execution_time: float):
        """Save query execution history."""
        try:
            conn = sqlite3.connect(self.config_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO query_history 
                (date_start, date_end, records_found, execution_time)
                VALUES (?, ?, ?, ?)
            """, (date_start, date_end, records_found, execution_time))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error saving query history: {e}")
    
    def get_query_history(self, limit: int = 10) -> list:
        """Get recent query history."""
        try:
            conn = sqlite3.connect(self.config_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT date_start, date_end, records_found, execution_time, created_at
                FROM query_history 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'date_start': row[0],
                    'date_end': row[1], 
                    'records_found': row[2],
                    'execution_time': row[3],
                    'created_at': row[4]
                }
                for row in results
            ]
            
        except Exception as e:
            logging.error(f"Error loading query history: {e}")
            return []