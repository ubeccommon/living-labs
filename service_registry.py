#!/usr/bin/env python3
"""
Service Registry - Central registration and discovery for all services

Design Principles Applied:
- Principle #3: Service Registry for Dependencies
- Principle #12: Method Singularity (single registry for all services)

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

import logging
import asyncio
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Central registry for all system services.
    Provides service discovery and dependency injection.
    """
    
    def __init__(self):
        """Initialize the service registry"""
        self._services: Dict[str, Any] = {}
        logger.info("Service Registry initialized")
    
    def register(self, name: str, service: Any) -> None:
        """
        Register a service with the registry
        
        Args:
            name: Service identifier
            service: Service instance
        """
        if name in self._services:
            logger.warning(f"Service '{name}' already registered, overwriting")
        
        self._services[name] = service
        logger.info(f"Service registered: {name}")
    
    def get(self, name: str) -> Optional[Any]:
        """
        Get a service from the registry
        
        Args:
            name: Service identifier
            
        Returns:
            Service instance or None if not found
        """
        service = self._services.get(name)
        if not service:
            logger.warning(f"Service '{name}' not found in registry")
        return service
    
    def unregister(self, name: str) -> bool:
        """
        Remove a service from the registry
        
        Args:
            name: Service identifier
            
        Returns:
            True if service was removed, False if not found
        """
        if name in self._services:
            del self._services[name]
            logger.info(f"Service unregistered: {name}")
            return True
        return False
    
    def list_services(self) -> list:
        """
        Get list of all registered service names
        
        Returns:
            List of service identifiers
        """
        return list(self._services.keys())
    
    def clear(self) -> None:
        """Clear all registered services"""
        self._services.clear()
        logger.info("Service registry cleared")
    
    def health_check(self) -> dict:
        """
        Check health of all registered services
        
        Returns:
            Dictionary with health status of each service
        """
        health_status = {}
        
        for name, service in self._services.items():
            try:
                # Check if service has health_check method
                if hasattr(service, 'health_check'):
                    if asyncio.iscoroutinefunction(service.health_check):
                        # Handle async health checks
                        import asyncio
                        loop = asyncio.get_event_loop()
                        health = loop.run_until_complete(service.health_check())
                    else:
                        health = service.health_check()
                    health_status[name] = health
                else:
                    # Basic availability check
                    health_status[name] = {
                        "status": "unknown",
                        "available": service is not None
                    }
            except Exception as e:
                health_status[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_status
    
    def __contains__(self, name: str) -> bool:
        """Check if a service is registered"""
        return name in self._services
    
    def __getitem__(self, name: str) -> Any:
        """Get service using bracket notation"""
        service = self.get(name)
        if service is None:
            raise KeyError(f"Service '{name}' not found")
        return service
    
    def __len__(self) -> int:
        """Get number of registered services"""
        return len(self._services)
    
    def __repr__(self) -> str:
        """String representation"""
        return f"ServiceRegistry(services={list(self._services.keys())})"


# ============================================================
# Service Initialization Functions
# ============================================================

async def initialize_stellar_onboarding(config):
    """
    Initialize Stellar Onboarding Service for automatic wallet creation.
    
    This service creates and funds new Stellar wallets for stewards who don't have one,
    automatically funding them with minimum XLM and adding UBECrc trustlines.
    
    Args:
        config: Configuration object with stellar_onboarding settings
        
    Returns:
        StellarOnboardingService instance or None if not configured
    """
    # Check if onboarding is enabled and configured
    if not config.stellar_onboarding.enabled:
        logger.info("Stellar Onboarding service disabled (STELLAR_ONBOARDING_ENABLED=false)")
        return None
    
    if not config.stellar_onboarding.is_configured:
        logger.warning("Stellar Onboarding enabled but not fully configured - missing credentials")
        return None
    
    try:
        # Import here to avoid circular dependencies
        from stellar_onboarding_service import StellarOnboardingService
        
        # Build configuration for onboarding service
        onboarding_config = {
            'stellar_horizon_url': config.stellar.horizon_url,
            'stellar_network': config.stellar.network,
            'funding_source_public': config.stellar_onboarding.funding_public,
            'funding_source_secret': config.stellar_onboarding.funding_secret,
            'ubecrc_asset_code': 'UBECrc',
            'ubecrc_issuer': config.stellar.ubecrc_issuer_public
        }
        
        # Create service instance
        service = StellarOnboardingService(onboarding_config)
        
        # Check funding account status
        status = await service.check_funding_account_balance()
        
        if status.get('configured'):
            xlm_balance = status.get('xlm_balance', 0)
            accounts_possible = status.get('accounts_possible', 0)
            
            logger.info(
                f"✅ Stellar Onboarding service initialized: "
                f"{xlm_balance} XLM available, can create {accounts_possible} wallets"
            )
            
            # Log warning if balance is low
            if status.get('warning'):
                logger.warning(f"⚠️  {status['warning']}")
            
            # Log critical alert if very low
            if accounts_possible < 5:
                logger.error(
                    f"❌ CRITICAL: Funding account almost depleted! "
                    f"Only {accounts_possible} wallets can be created. Please add XLM."
                )
        else:
            logger.error(f"Failed to check funding account: {status.get('error', 'Unknown error')}")
            return None
        
        return service
        
    except ImportError as e:
        logger.error(f"Failed to import StellarOnboardingService: {e}")
        logger.error("Make sure stellar_onboarding_service.py is in the Python path")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Stellar Onboarding service: {e}", exc_info=True)
        return None


# ============================================================
# Global registry instance
# ============================================================
registry = ServiceRegistry()


# Helper functions for convenience
def register_service(name: str, service: Any) -> None:
    """Register a service with the global registry"""
    registry.register(name, service)


def get_service(name: str) -> Optional[Any]:
    """Get a service from the global registry"""
    return registry.get(name)


def list_services() -> list:
    """List all registered services"""
    return registry.list_services()


"""
Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations.
"""
