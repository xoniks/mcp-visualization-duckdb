"""
Secure credential management for Databricks integration
"""

import logging
import getpass
from typing import Optional, Dict, Any
from pathlib import Path
import keyring
from cryptography.fernet import Fernet
import base64
import os

logger = logging.getLogger(__name__)


class DatabricksCredentialManager:
    """Manages Databricks credentials securely"""
    
    def __init__(self):
        self.service_name = "mcp-visualization-databricks"
        self.config_dir = Path.home() / ".mcp-visualization"
        self.config_dir.mkdir(exist_ok=True)
        
    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key for local storage"""
        key_file = self.config_dir / ".key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Make key file readable only by user
            key_file.chmod(0o600)
            return key
    
    def store_credentials(self, server_hostname: str, http_path: str, token: str, 
                         use_keyring: bool = True) -> bool:
        """Store Databricks credentials securely"""
        try:
            config = {
                "server_hostname": server_hostname,
                "http_path": http_path,
                "token": token
            }
            
            if use_keyring:
                # Try to use system keyring first
                try:
                    import json
                    keyring.set_password(self.service_name, "config", json.dumps(config))
                    logger.info("Credentials stored in system keyring")
                    return True
                except Exception as e:
                    logger.warning(f"System keyring failed: {e}, falling back to encrypted file")
            
            # Fallback to encrypted file storage
            key = self._get_encryption_key()
            fernet = Fernet(key)
            
            import json
            encrypted_config = fernet.encrypt(json.dumps(config).encode())
            
            config_file = self.config_dir / "databricks_config.enc"
            with open(config_file, 'wb') as f:
                f.write(encrypted_config)
            
            config_file.chmod(0o600)
            logger.info("Credentials stored in encrypted file")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store credentials: {e}")
            return False
    
    def load_credentials(self) -> Optional[Dict[str, str]]:
        """Load Databricks credentials"""
        try:
            # Try system keyring first
            try:
                import json
                config_str = keyring.get_password(self.service_name, "config")
                if config_str:
                    config = json.loads(config_str)
                    logger.info("Credentials loaded from system keyring")
                    return config
            except Exception as e:
                logger.debug(f"Keyring load failed: {e}")
            
            # Try encrypted file
            config_file = self.config_dir / "databricks_config.enc"
            if config_file.exists():
                key = self._get_encryption_key()
                fernet = Fernet(key)
                
                with open(config_file, 'rb') as f:
                    encrypted_config = f.read()
                
                import json
                decrypted_config = fernet.decrypt(encrypted_config)
                config = json.loads(decrypted_config.decode())
                logger.info("Credentials loaded from encrypted file")
                return config
            
            logger.warning("No stored credentials found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return None
    
    def delete_credentials(self) -> bool:
        """Delete stored credentials"""
        try:
            success = True
            
            # Delete from keyring
            try:
                keyring.delete_password(self.service_name, "config")
            except Exception as e:
                logger.debug(f"Keyring delete failed: {e}")
                success = False
            
            # Delete encrypted file
            config_file = self.config_dir / "databricks_config.enc"
            if config_file.exists():
                config_file.unlink()
            
            logger.info("Credentials deleted")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete credentials: {e}")
            return False
    
    def test_connection(self, server_hostname: str, http_path: str, token: str) -> bool:
        """Test Databricks connection with provided credentials"""
        try:
            from databricks import sql
            
            logger.info("Testing Databricks connection...")
            
            with sql.connect(
                server_hostname=server_hostname,
                http_path=http_path,
                access_token=token,
                catalog="main",  # Default catalog
                schema="default"  # Default schema
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1 as test")
                    result = cursor.fetchone()
                    
            logger.info("Databricks connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Databricks connection test failed: {e}")
            return False
    
    def prompt_for_credentials(self, interactive: bool = True) -> Optional[Dict[str, str]]:
        """Interactively prompt for Databricks credentials"""
        if not interactive:
            return None
            
        try:
            print("\nDatabricks Configuration")
            print("=" * 30)
            
            server_hostname = input("Server hostname (e.g., your-workspace.cloud.databricks.com): ").strip()
            if not server_hostname:
                print("Server hostname is required")
                return None
            
            http_path = input("HTTP path (e.g., /sql/1.0/warehouses/abc123): ").strip()
            if not http_path:
                print("HTTP path is required")
                return None
            
            print("\nAccess Token:")
            print("You can get this from your Databricks workspace:")
            print("User Settings > Developer > Access Tokens > Generate New Token")
            token = getpass.getpass("Enter access token (hidden): ").strip()
            if not token:
                print("Access token is required")
                return None
            
            # Test connection
            print("\nTesting connection...")
            try:
                if self.test_connection(server_hostname, http_path, token):
                    print("Connection successful!")
                    return {
                        "server_hostname": server_hostname,
                        "http_path": http_path,
                        "token": token
                    }
                else:
                    print("Connection failed. Please check your credentials.")
                    return None
            except Exception as test_error:
                print(f"Connection test failed with error: {test_error}")
                print(f"Error type: {type(test_error).__name__}")
                import traceback
                print("Full error details:")
                traceback.print_exc()
                return None
                
        except KeyboardInterrupt:
            print("\nCancelled by user")
            return None
        except Exception as e:
            print(f"Error during credential setup: {e}")
            return None
    
    def get_connection_string(self) -> Optional[str]:
        """Get connection string for display purposes (token masked)"""
        creds = self.load_credentials()
        if not creds:
            return None
        
        masked_token = creds["token"][:8] + "..." + creds["token"][-4:] if len(creds["token"]) > 12 else "***"
        return f"databricks://{creds['server_hostname']}{creds['http_path']} (token: {masked_token})"