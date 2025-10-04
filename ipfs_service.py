#!/usr/bin/env python3
"""
IPFS Service Module - Handles IPFS/Pinata integration
Provides permanent, decentralized storage for environmental observations

Design Principles Applied:
- Principle #2: Service pattern - no standalone execution
- Principle #5: Strict async operations
- Principle #12: Method singularity

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

import json
import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ObservationData:
    """Standard format for environmental observations"""
    device_id: str
    timestamp: str
    readings: Dict[str, float]
    location: Dict[str, float]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class PinataService:
    """
    Pinata IPFS service for permanent data storage
    Handles all IPFS operations through Pinata's API
    """
    
    def __init__(self, api_key: str, secret_key: str, jwt: Optional[str] = None):
        """
        Initialize Pinata service
        
        Args:
            api_key: Pinata API key
            secret_key: Pinata secret key
            jwt: Optional JWT token for enhanced security
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.jwt = jwt
        self.base_url = "https://api.pinata.cloud"
        self.gateway_url = "https://gateway.pinata.cloud"
        
        # Rate limiting
        self._rate_limit_semaphore = asyncio.Semaphore(10)
        
        logger.info("PinataService initialized")
    
    async def add_json(self, data: dict, metadata: Optional[dict] = None) -> Optional[str]:
        """
        Pin JSON data to IPFS via Pinata
        
        Args:
            data: Dictionary to store on IPFS
            metadata: Optional Pinata metadata
            
        Returns:
            IPFS hash (CID) if successful, None otherwise
        """
        try:
            async with self._rate_limit_semaphore:
                url = f"{self.base_url}/pinning/pinJSONToIPFS"
                
                headers = {
                    "pinata_api_key": self.api_key,
                    "pinata_secret_api_key": self.secret_key
                }
                
                if self.jwt:
                    headers = {"Authorization": f"Bearer {self.jwt}"}
                
                pin_data = {
                    "pinataContent": data,
                    "pinataOptions": {
                        "cidVersion": 1
                    }
                }
                
                if metadata:
                    pin_data["pinataMetadata"] = metadata
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=pin_data, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            cid = result.get("IpfsHash")
                            logger.info(f"Successfully pinned to IPFS: {cid}")
                            return cid
                        else:
                            error_text = await response.text()
                            logger.error(f"Pinata error ({response.status}): {error_text}")
                            return None
                            
        except Exception as e:
            logger.error(f"Failed to pin to IPFS: {e}")
            return None
    
    async def get_json(self, cid: str) -> Optional[dict]:
        """
        Retrieve JSON data from IPFS via Pinata gateway
        
        Args:
            cid: IPFS Content Identifier
            
        Returns:
            Retrieved data as dictionary, or None if failed
        """
        try:
            url = f"{self.gateway_url}/ipfs/{cid}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Retrieved data from IPFS: {cid}")
                        return data
                    else:
                        logger.error(f"Failed to retrieve from IPFS: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error retrieving from IPFS: {e}")
            return None
    
    async def store_observation(self, observation: ObservationData) -> Optional[str]:
        """
        Store environmental observation on IPFS
        
        Args:
            observation: ObservationData object
            
        Returns:
            IPFS CID if successful
        """
        metadata = {
            "name": f"observation_{observation.device_id}_{observation.timestamp}",
            "keyvalues": {
                "type": "environmental_observation",
                "device_id": observation.device_id,
                "timestamp": observation.timestamp,
                "location_lat": str(observation.location.get("latitude", 0)),
                "location_lon": str(observation.location.get("longitude", 0))
            }
        }
        
        return await self.add_json(observation.to_dict(), metadata)
    
    async def get_pin_list(self, status: str = "pinned", limit: int = 100) -> List[dict]:
        """
        Get list of pinned items from Pinata
        
        Args:
            status: Filter by pin status ('pinned', 'unpinned', 'all')
            limit: Maximum number of results
            
        Returns:
            List of pin objects
        """
        try:
            url = f"{self.base_url}/data/pinList"
            
            headers = {
                "pinata_api_key": self.api_key,
                "pinata_secret_api_key": self.secret_key
            }
            
            if self.jwt:
                headers = {"Authorization": f"Bearer {self.jwt}"}
            
            params = {
                "status": status,
                "pageLimit": limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("rows", [])
                    else:
                        logger.error(f"Failed to get pin list: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting pin list: {e}")
            return []
    
    async def unpin(self, cid: str) -> bool:
        """
        Unpin content from Pinata
        
        Args:
            cid: IPFS CID to unpin
            
        Returns:
            True if successfully unpinned
        """
        try:
            url = f"{self.base_url}/pinning/unpin/{cid}"
            
            headers = {
                "pinata_api_key": self.api_key,
                "pinata_secret_api_key": self.secret_key
            }
            
            if self.jwt:
                headers = {"Authorization": f"Bearer {self.jwt}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"Successfully unpinned: {cid}")
                        return True
                    else:
                        logger.error(f"Failed to unpin: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error unpinning: {e}")
            return False
    
    def get_ipfs_url(self, cid: str) -> str:
        """Get public gateway URL for a CID"""
        return f"{self.gateway_url}/ipfs/{cid}"
    
    @property
    def is_available(self) -> bool:
        """Check if service is available"""
        return bool(self.api_key and self.secret_key)
    
    @property
    def can_send_payments(self) -> bool:
        """Compatibility property for service registry"""
        return False  # IPFS doesn't handle payments
    
    async def health_check(self) -> dict:
        """Check service health"""
        try:
            # Try to get pin list as a health check
            pins = await self.get_pin_list(limit=1)
            return {
                "status": "healthy",
                "service": "pinata",
                "available": True,
                "total_pins": len(pins)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "pinata",
                "available": False,
                "error": str(e)
            }
    
    async def close(self):
        """Cleanup (compatibility method)"""
        logger.info("PinataService closing")


class IPFSService:
    """
    Basic IPFS service for local IPFS nodes
    Fallback when Pinata is not available
    
    Implements the same interface as PinataService for interoperability.
    """
    
    def __init__(self, api_url: str = "http://localhost:5001"):
        """
        Initialize IPFS service for local node
        
        Args:
            api_url: IPFS API endpoint URL
        """
        self.api_url = api_url
        self.gateway_url = "http://localhost:8080"
        
        logger.info(f"IPFSService initialized with {api_url}")
    
    async def add_json(self, data: dict) -> Optional[str]:
        """
        Add JSON data to local IPFS node
        
        Args:
            data: Dictionary to store
            
        Returns:
            IPFS CID if successful
        """
        try:
            url = f"{self.api_url}/api/v0/add"
            
            json_str = json.dumps(data)
            
            form_data = aiohttp.FormData()
            form_data.add_field('file', json_str, 
                              filename='data.json',
                              content_type='application/json')
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        cid = result.get("Hash")
                        logger.info(f"Added to IPFS: {cid}")
                        return cid
                    else:
                        logger.error(f"IPFS add failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Failed to add to IPFS: {e}")
            return None
    
    async def get_json(self, cid: str) -> Optional[dict]:
        """
        Retrieve JSON from local IPFS node
        
        Args:
            cid: IPFS Content Identifier
            
        Returns:
            Retrieved data as dictionary
        """
        try:
            url = f"{self.api_url}/api/v0/cat?arg={cid}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as response:
                    if response.status == 200:
                        text = await response.text()
                        return json.loads(text)
                    else:
                        logger.error(f"IPFS cat failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Failed to retrieve from IPFS: {e}")
            return None
    
    async def store_observation(self, observation: ObservationData) -> Optional[str]:
        """
        Store environmental observation on local IPFS node
        
        This method provides the same interface as PinataService.store_observation()
        to ensure interoperability between IPFS backends.
        
        Args:
            observation: ObservationData object
            
        Returns:
            IPFS CID if successful, None otherwise
        """
        try:
            # Convert observation to dictionary
            obs_dict = observation.to_dict()
            
            # Store on IPFS
            cid = await self.add_json(obs_dict)
            
            if cid:
                logger.info(f"Observation stored on local IPFS: {cid}")
                logger.debug(f"  Device: {observation.device_id}")
                logger.debug(f"  Timestamp: {observation.timestamp}")
            else:
                logger.error("Failed to store observation on local IPFS")
            
            return cid
            
        except Exception as e:
            logger.error(f"Error storing observation on local IPFS: {e}")
            return None
    
    def get_ipfs_url(self, cid: str) -> str:
        """Get local gateway URL for a CID"""
        return f"{self.gateway_url}/ipfs/{cid}"
    
    @property
    def is_available(self) -> bool:
        """Check if service is available"""
        return True  # Assume available if created
    
    @property
    def can_send_payments(self) -> bool:
        """Compatibility property for service registry"""
        return False  # IPFS doesn't handle payments
    
    async def health_check(self) -> dict:
        """Check service health"""
        try:
            url = f"{self.api_url}/api/v0/version"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        version = await response.json()
                        return {
                            "status": "healthy",
                            "service": "ipfs_local",
                            "available": True,
                            "version": version.get("Version")
                        }
            return {
                "status": "unhealthy",
                "service": "ipfs_local",
                "available": False
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "ipfs_local",
                "available": False,
                "error": str(e)
            }
    
    async def close(self):
        """Cleanup (compatibility method)"""
        logger.info("IPFSService closing")


"""
Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations.
"""
