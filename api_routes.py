#!/usr/bin/env python3
"""
API Routes Module - HTTP endpoints for the UBEC system
Provides admin and health check endpoints
NOTE: Observation endpoints are handled by phenomenological_api.py

Design Principles Applied:
- Principle #2: Service pattern - routes only, no standalone execution
- Principle #3: Dependencies via service registry
- Principle #5: Strict async operations
- Principle #12: Method singularity - no duplicate endpoints

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

import logging
from typing import List
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException

logger = logging.getLogger(__name__)


# ==================================================
# ADMIN ROUTER - Health and System Management
# ==================================================

def create_admin_router() -> APIRouter:
    """Create admin router with management endpoints"""
    
    router = APIRouter(prefix="/api/v2/admin", tags=["admin"])
    
    @router.get("/health")
    async def health_check(request: Request):
        """Check system health"""
        try:
            health = {
                "status": "operational",
                "timestamp": datetime.utcnow().isoformat(),
                "services": {}
            }
            
            # Check observation service
            obs_service = getattr(request.app.state, 'observation_service', None)
            if obs_service:
                health["services"]["observation_service"] = {
                    "available": True,
                    "ipfs": obs_service.ipfs_available,
                    "stellar": obs_service.stellar_available,
                    "database": obs_service.db_available
                }
            else:
                health["services"]["observation_service"] = {
                    "available": False
                }
            
            # Check database
            db = getattr(request.app.state, 'db', None)
            if db:
                health["services"]["database"] = {
                    "available": True,
                    "type": "postgresql"
                }
            else:
                health["services"]["database"] = {
                    "available": False
                }
            
            # Check Stellar
            stellar = getattr(request.app.state, 'stellar', None)
            if stellar:
                health["services"]["stellar"] = {
                    "available": True,
                    "can_send_payments": getattr(stellar, 'can_send_payments', False)
                }
            else:
                health["services"]["stellar"] = {
                    "available": False
                }
            
            # Check IPFS
            ipfs = getattr(request.app.state, 'ipfs', None)
            if ipfs:
                health["services"]["ipfs"] = {
                    "available": True
                }
            else:
                health["services"]["ipfs"] = {
                    "available": False
                }
            
            return health
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "degraded",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @router.get("/observers/{observer_id}")
    async def get_observer_stats(request: Request, observer_id: str):
        """Get statistics for a specific observer"""
        try:
            db = getattr(request.app.state, 'db', None) or getattr(request.app.state, 'pheno_db', None)
            if not db:
                raise HTTPException(
                    status_code=503,
                    detail="Database not available"
                )
            
            # Get observer stats if method exists
            if hasattr(db, 'get_observer_stats'):
                stats = await db.get_observer_stats(observer_id)
                
                if "error" in stats:
                    raise HTTPException(
                        status_code=404,
                        detail=stats["error"]
                    )
                
                return stats
            else:
                # Fallback: basic observer info
                async with db.pool.acquire() as conn:
                    observer = await conn.fetchrow(
                        "SELECT * FROM phenomenological.observers WHERE id = $1",
                        observer_id
                    )
                    
                    if not observer:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Observer {observer_id} not found"
                        )
                    
                    return dict(observer)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get observer stats: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error getting observer stats: {str(e)}"
            )
    
    return router


def get_all_routers() -> List[APIRouter]:
    """
    Get all API routers for mounting in main app
    
    NOTE: Observation endpoints are in phenomenological_api.py to avoid conflicts
    This module only provides admin and health check endpoints
    """
    return [
        create_admin_router()
    ]


"""
Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations.

IMPORTANT: This module does NOT include observation endpoints.
Observation handling is done by phenomenological_api.py at /api/v2/observations
to follow Principle #12: Method Singularity - no duplicate implementations.
"""
