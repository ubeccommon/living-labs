#!/usr/bin/env python3
"""
Service Registry - Central registration and discovery for all services

Design Principles Applied:
- Principle #3: Service Registry for Dependencies
- Principle #12: Method Singularity (single registry for all services)

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

import logging
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


# Global registry instance
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
