"""
config.py - Configuration for UBEC Environmental Monitoring System

This is a minimal configuration file. All values can be overridden via environment variables.

This project uses the services of Claude and Anthropic PBC.
"""

import os
from typing import List, Dict, Any
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded configuration from {env_path}")
    else:
        print(f"ℹ️  No .env file found at {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    pass


class DatabaseConfig:
    """
    Database configuration with support for two-schema architecture.
    
    The UBEC Sensors database uses two schemas:
    - ubec_sensors: Sensor hardware and time-series data
    - phenomenological: Observations and gift economy
    """
    
    def __init__(self):
        # Database connection
        self.url = os.getenv('DATABASE_URL', 'postgresql://postgres@localhost/ubec_sensors')
        self.enabled = os.getenv('ENABLE_DATABASE', 'true').lower() in ('true', '1', 'yes')
        
        # Schema configuration
        self.sensor_schema = os.getenv('DB_SENSOR_SCHEMA', 'ubec_sensors')
        self.phenomenological_schema = os.getenv('DB_PHENOMENOLOGICAL_SCHEMA', 'phenomenological')
        self.public_schema = os.getenv('DB_PUBLIC_SCHEMA', 'public')
        
        # Search path (order matters - searched in sequence)
        search_path_env = os.getenv('DB_SEARCH_PATH', '')
        if search_path_env:
            self.search_path = search_path_env
        else:
            # Default search path: phenomenological first, then ubec_sensors, then public
            self.search_path = f"{self.phenomenological_schema},{self.sensor_schema},{self.public_schema}"
        
        # Connection pool settings
        self.pool_min_size = int(os.getenv('DB_POOL_MIN_SIZE', '5'))
        self.pool_max_size = int(os.getenv('DB_POOL_MAX_SIZE', '20'))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', '60'))
        self.command_timeout = int(os.getenv('DB_COMMAND_TIMEOUT', '60'))
        
        # Query settings
        self.statement_cache_size = int(os.getenv('DB_STATEMENT_CACHE_SIZE', '100'))
        self.use_prepared_statements = os.getenv('DB_USE_PREPARED_STATEMENTS', 'true').lower() in ('true', '1', 'yes')
    
    @property
    def connection_kwargs(self) -> Dict[str, Any]:
        """
        Get connection kwargs for asyncpg.create_pool()
        
        Returns dict with all connection parameters including server_settings
        for proper schema search path.
        """
        return {
            'dsn': self.url,
            'min_size': self.pool_min_size,
            'max_size': self.pool_max_size,
            'timeout': self.pool_timeout,
            'command_timeout': self.command_timeout,
            'server_settings': {
                'search_path': self.search_path
            }
        }
    
    @property
    def is_configured(self) -> bool:
        """Check if database is properly configured"""
        return bool(self.url and self.enabled)
    
    def get_qualified_table(self, table_name: str, schema: str = None) -> str:
        """
        Get fully qualified table name with schema prefix.
        
        Args:
            table_name: Name of the table
            schema: Schema name (defaults to search_path logic)
        
        Returns:
            Qualified table name like 'schema.table'
        
        Examples:
            >>> db.get_qualified_table('devices', 'ubec_sensors')
            'ubec_sensors.devices'
            >>> db.get_qualified_table('observers', 'phenomenological')
            'phenomenological.observers'
        """
        if schema:
            return f"{schema}.{table_name}"
        
        # Default to appropriate schema based on table name
        sensor_tables = {'devices', 'sensor_readings', 'users', 'farmers', 
                        'ubecrc_distributions', 'reward_calculations', 'observation_cache'}
        
        if table_name in sensor_tables:
            return f"{self.sensor_schema}.{table_name}"
        else:
            return f"{self.phenomenological_schema}.{table_name}"
    
    def __repr__(self):
        """Return string representation (excluding sensitive connection string)"""
        return f"<DatabaseConfig enabled={self.enabled} search_path={self.search_path}>"


class IPFSConfig:
    """IPFS/Pinata configuration"""
    
    def __init__(self):
        self.api_key = os.getenv('PINATA_API_KEY', '')
        self.secret_key = os.getenv('PINATA_SECRET_KEY', '')
        self.jwt = os.getenv('PINATA_JWT', '')
        self.api_url = os.getenv('PINATA_API_URL', 'https://api.pinata.cloud')
        self.gateway_url = os.getenv('IPFS_GATEWAY', 'https://gateway.pinata.cloud')
        self.rate_limit_requests = int(os.getenv('IPFS_RATE_LIMIT_REQUESTS', '180'))
        self.rate_limit_window_seconds = int(os.getenv('IPFS_RATE_LIMIT_WINDOW', '60'))
        self.cid_version = int(os.getenv('IPFS_CID_VERSION', '1'))
    
    @property
    def is_configured(self) -> bool:
        """Check if IPFS is properly configured"""
        return bool(self.api_key and self.secret_key and self.jwt)
    
    def __repr__(self):
        """Return string representation"""
        return f"<IPFSConfig configured={self.is_configured}>"


class StellarConfig:
    """Stellar blockchain configuration"""
    
    def __init__(self):
        self.network = os.getenv('STELLAR_NETWORK', 'MAINNET')
        self.distributor_secret = os.getenv('STELLAR_DISTRIBUTOR_SECRET', '')
        self.distributor_public = os.getenv('STELLAR_DISTRIBUTOR_PUBLIC', '')
        self.ubecrc_issuer_public = os.getenv(
            'UBECrc_ISSUER_PUBLIC', 
            'GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC'
        )
        
        # Stellar network URLs
        self.horizon_url = os.getenv(
            'STELLAR_HORIZON_URL',
            'https://horizon.stellar.org' if self.network == 'MAINNET' else 'https://horizon-testnet.stellar.org'
        )
    
    @property
    def is_configured(self) -> bool:
        """Check if Stellar is properly configured"""
        return bool(self.distributor_secret and self.distributor_public)
    
    def __repr__(self):
        """Return string representation"""
        return f"<StellarConfig network={self.network} configured={self.is_configured}>"


class Config:
    """
    Configuration class for the UBEC system.
    
    All values have safe defaults and can be overridden via environment variables.
    
    Two-Schema Database Architecture:
    --------------------------------
    The database uses two schemas to separate concerns:
    
    1. ubec_sensors schema:
       - Sensor hardware layer
       - Tables: devices, sensor_readings, users, farmers, etc.
       
    2. phenomenological schema:
       - Observation and gift economy layer
       - Tables: observers, phenomena, observations, gifts, patterns, etc.
    
    Search path is configured as: phenomenological, ubec_sensors, public
    This means queries will search phenomenological first, then ubec_sensors,
    then public (which should only contain PostGIS system tables).
    """
    
    def __init__(self):
        # Environment
        self.ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
        self.LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
        self.DEBUG: bool = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')
        
        # API Configuration
        self.API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
        self.API_PORT: int = int(os.getenv('API_PORT', '8000'))
        
        # CORS Configuration
        cors_str = os.getenv('CORS_ORIGINS', '*')
        self.CORS_ORIGINS: List[str] = cors_str.split(',') if cors_str != '*' else ['*']
        
        # Database Configuration (nested object)
        self.database = DatabaseConfig()
        
        # IPFS Configuration (nested object)
        self.ipfs = IPFSConfig()
        
        # Stellar Configuration (nested object)
        self.stellar = StellarConfig()
        
        # ============================================================
        # Legacy flat attributes for backward compatibility
        # ============================================================
        # These maintain compatibility with existing code
        
        # Database (legacy)
        self.ENABLE_DATABASE: bool = self.database.enabled
        self.DATABASE_URL: str = self.database.url
        
        # IPFS (legacy)
        self.PINATA_API_KEY: str = self.ipfs.api_key
        self.PINATA_API_SECRET: str = self.ipfs.secret_key
        self.IPFS_GATEWAY: str = self.ipfs.gateway_url
        
        # Stellar (legacy)
        self.STELLAR_NETWORK: str = self.stellar.network
        self.STELLAR_DISTRIBUTOR_SECRET: str = self.stellar.distributor_secret
        self.STELLAR_DISTRIBUTOR_PUBLIC: str = self.stellar.distributor_public
        self.UBECrc_ISSUER_PUBLIC: str = self.stellar.ubecrc_issuer_public
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == 'production'
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == 'development'
    
    def __repr__(self):
        """Return string representation (excluding sensitive values)"""
        return (
            f"<Config "
            f"env={self.ENVIRONMENT} "
            f"log_level={self.LOG_LEVEL} "
            f"db={self.database.is_configured} "
            f"ipfs={self.ipfs.is_configured} "
            f"stellar={self.stellar.is_configured}"
            f">"
        )


# ============================================================
# Global config instance
# ============================================================

config = Config()


# ============================================================
# Schema Constants (for explicit schema references in code)
# ============================================================

# Use these constants when you need explicit schema references
SENSOR_SCHEMA = config.database.sensor_schema
PHENOMENOLOGICAL_SCHEMA = config.database.phenomenological_schema
PUBLIC_SCHEMA = config.database.public_schema


# ============================================================
# Validation
# ============================================================

def validate_config():
    """Validate that required configuration is present"""
    warnings = []
    errors = []
    
    # Database validation
    if config.database.enabled:
        if not config.database.url:
            errors.append("❌ DATABASE_URL not set but database is enabled")
        else:
            print(f"✅ Database configured: {config.database.search_path}")
    else:
        warnings.append("⚠️  Database is disabled (ENABLE_DATABASE=false)")
    
    # IPFS validation
    if not config.ipfs.is_configured:
        if not config.ipfs.api_key:
            warnings.append("⚠️  PINATA_API_KEY not set - IPFS service may not work")
        if not config.ipfs.secret_key:
            warnings.append("⚠️  PINATA_SECRET_KEY not set - IPFS service may not work")
        if not config.ipfs.jwt:
            warnings.append("⚠️  PINATA_JWT not set - IPFS service may not work")
    
    # Stellar validation
    if not config.stellar.is_configured:
        if not config.stellar.distributor_secret:
            warnings.append("⚠️  STELLAR_DISTRIBUTOR_SECRET not set - UBECrc payments will not work")
        if not config.stellar.distributor_public:
            warnings.append("⚠️  STELLAR_DISTRIBUTOR_PUBLIC not set - UBECrc payments will not work")
    
    # Print results
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"   {error}")
        print("\n   Fix these errors before starting the application\n")
    
    if warnings:
        print("\n⚠️  Configuration Warnings:")
        for warning in warnings:
            print(f"   {warning}")
        print("\n   Set these values in environment variables or .env file\n")
    
    if not errors and not warnings:
        print("✅ All configuration validated successfully")


# ============================================================
# Run validation when module is imported
# ============================================================

validate_config()


# ============================================================
# Usage Examples (for documentation)
# ============================================================

if __name__ == "__main__":
    """
    Example usage of the updated config module
    """
    
    print("\n" + "="*60)
    print("UBEC Configuration Summary")
    print("="*60)
    
    print(f"\nEnvironment: {config.ENVIRONMENT}")
    print(f"Debug Mode: {config.DEBUG}")
    print(f"API: {config.API_HOST}:{config.API_PORT}")
    
    print(f"\nDatabase:")
    print(f"  - Enabled: {config.database.enabled}")
    print(f"  - Search Path: {config.database.search_path}")
    print(f"  - Sensor Schema: {config.database.sensor_schema}")
    print(f"  - Phenomenological Schema: {config.database.phenomenological_schema}")
    print(f"  - Pool Size: {config.database.pool_min_size}-{config.database.pool_max_size}")
    
    print(f"\nIPFS:")
    print(f"  - Configured: {config.ipfs.is_configured}")
    print(f"  - Gateway: {config.ipfs.gateway_url}")
    
    print(f"\nStellar:")
    print(f"  - Configured: {config.stellar.is_configured}")
    print(f"  - Network: {config.stellar.network}")
    print(f"  - Horizon: {config.stellar.horizon_url}")
    
    print("\nExample: Get qualified table names")
    print(f"  - Devices: {config.database.get_qualified_table('devices')}")
    print(f"  - Observers: {config.database.get_qualified_table('observers')}")
    print(f"  - Gifts: {config.database.get_qualified_table('gifts')}")
    
    print("\nExample: Database connection kwargs")
    print(f"  - Connection params: {config.database.connection_kwargs}")
    
    print("\n" + "="*60)
