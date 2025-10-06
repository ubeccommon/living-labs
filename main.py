#!/usr/bin/env python3
"""
UBEC System - Main Orchestrator (Reciprocal Economy Edition)
Single Entry Point for All Services

This is the ONLY file that should run a server.
All other modules are imported as services/routers.

Design Principles Applied:
- Principle #2: Service Pattern with Centralized Execution
- Principle #5: Strict async operations throughout
- Principle #10: Clear separation of concerns

Attribution: This project uses the services of Claude and Anthropic PBC.

Version: 3.0.6 (Fixed Multilingual Routing - Exact Files Only)
"""

import os
import sys
import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from pathlib import Path
from decimal import Decimal

# Import the configuration from config.py
from config import config, SENSOR_SCHEMA, PHENOMENOLOGICAL_SCHEMA

# Import the service registry
from service_registry import ServiceRegistry

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.getenv('LOG_FILE', 'ubec_system.log'))
    ]
)
logger = logging.getLogger(__name__)

# Create global service registry
registry = ServiceRegistry()

# ==================================================
# APPLICATION LIFECYCLE
# ==================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the entire system lifecycle
    Initialize all services on startup, cleanup on shutdown
    """
    logger.info("╔" + "═"*58 + "╗")
    logger.info("║" + " "*58 + "║")
    logger.info("║" + "    UBEC RECIPROCAL ECONOMY SYSTEM".center(58) + "║")
    logger.info("║" + "    Environmental Monitoring Network".center(58) + "║")
    logger.info("║" + " "*58 + "║")
    logger.info("║" + "    Freie Waldorfschule Frankfurt (Oder)".center(58) + "║")
    logger.info("║" + "    Living Science Initiative".center(58) + "║")
    logger.info("║" + " "*58 + "║")
    logger.info("║" + "    Single Entry Point Architecture v3.0.6".center(58) + "║")
    logger.info("║" + "    🌍 EN + 🇩🇪 DE + 🇵🇱 PL Support".center(58) + "║")
    logger.info("║" + " "*58 + "║")
    logger.info("╚" + "═"*58 + "╝")
    
    # Log configuration status
    logger.info("System Configuration:")
    logger.info(f"  Database schema: {PHENOMENOLOGICAL_SCHEMA}")
    logger.info(f"  Search path: {config.database.search_path}")
    logger.info(f"  Stellar network: {config.stellar.network}")
    logger.info(f"  Environment: {config.ENVIRONMENT}")
    
    # Check for IPFS configuration
    has_ipfs = False
    if hasattr(config, 'ipfs') and hasattr(config.ipfs, 'is_configured'):
        has_ipfs = config.ipfs.is_configured
    else:
        # Check environment variables directly
        has_ipfs = bool(os.getenv('PINATA_API_KEY') or os.getenv('IPFS_API_URL'))
    
    logger.info(f"  IPFS configured: {has_ipfs}")
    logger.info(f"  Stellar configured: {config.stellar.is_configured}")
    logger.info(f"  Multilingual: English + Deutsch + Polski")
    
    # Initialize services
    try:
        # 1. Database Connection with Schema Configuration
        logger.info("Initializing phenomenological database...")
        from phenomenological_db import PhenomenologicalDB
        
        app.state.db = PhenomenologicalDB(
            config.database.url,
            schema=PHENOMENOLOGICAL_SCHEMA,
            search_path=config.database.search_path
        )
        await app.state.db.connect()
        app.state.pheno_db = app.state.db  # Alias for compatibility
        logger.info("✓ Phenomenological database connected")
        logger.info(f"  Schema: {PHENOMENOLOGICAL_SCHEMA}")
        logger.info(f"  Mode: Reciprocal Economy")
        
        # 2. Stellar Reciprocal Network
        app.state.stellar = None
        if config.stellar.is_configured:
            try:
                logger.info("Initializing UBEC reciprocal network...")
                from stellar_integration import StellarReciprocalNetwork
                
                app.state.stellar = StellarReciprocalNetwork({
                    'stellar_horizon_url': config.stellar.horizon_url,
                    'stellar_network': config.stellar.network,
                    'ubecrc_asset_code': 'UBECrc',
                    'ubecrc_issuer': config.stellar.ubecrc_issuer_public,
                    'ubecrc_distributor': config.stellar.distributor_public,
                    'ubecrc_distributor_secret': config.stellar.distributor_secret
                })
                await app.state.stellar.connect()
                
                # Check health
                health = await app.state.stellar.health_check()
                if health.get('can_send_payments'):
                    logger.info("✓ UBEC reciprocal network connected (payments enabled)")
                    logger.info(f"  UBECrc balance: {health.get('distributor_ubecrc_balance', '0')}")
                else:
                    logger.info("✓ Stellar network connected (view only mode)")
            except Exception as e:
                logger.warning(f"Stellar initialization failed: {e}")
                logger.info("⚠  Continuing without Stellar integration")
                app.state.stellar = None
        else:
            logger.info("⚠  Stellar integration disabled (no distributor key)")
        
        # 3. IPFS Service
        app.state.ipfs = None
        if has_ipfs:
            try:
                logger.info("Initializing IPFS service...")
                
                # Check for Pinata credentials first
                pinata_api_key = os.getenv('PINATA_API_KEY')
                pinata_secret = os.getenv('PINATA_SECRET_KEY')
                pinata_jwt = os.getenv('PINATA_JWT')
                
                if pinata_api_key and pinata_secret:
                    # Use PinataService
                    from ipfs_service import PinataService
                    app.state.ipfs = PinataService(
                        api_key=pinata_api_key,
                        secret_key=pinata_secret,
                        jwt=pinata_jwt
                    )
                    logger.info("✓ IPFS service initialized (Pinata)")
                    logger.info(f"  Gateway: https://gateway.pinata.cloud")
                else:
                    # Fallback to local IPFS
                    ipfs_api_url = os.getenv('IPFS_API_URL', 'http://localhost:5001')
                    from ipfs_service import IPFSService
                    app.state.ipfs = IPFSService(ipfs_api_url)
                    logger.info("✓ IPFS service initialized (local)")
                    logger.info(f"  API: {ipfs_api_url}")
                    
            except Exception as e:
                logger.warning(f"IPFS initialization failed: {e}")
                logger.info("⚠  Continuing without IPFS")
                app.state.ipfs = None
        else:
            logger.info("⚠  IPFS disabled (no configuration)")
        
        # 4. Observation Service
        logger.info("Initializing observation service...")
        from observation_service import ObservationService
        
        app.state.observation_service = ObservationService(
            ipfs_service=app.state.ipfs,
            stellar_service=app.state.stellar,
            database=app.state.db,
            phenomenological_db=app.state.db
        )
        logger.info("✓ Observation service initialized")
        
        # 5. Stellar Onboarding Service (Wallet Creation)
        app.state.stellar_onboarding = None
        if hasattr(config, 'stellar_onboarding') and config.stellar_onboarding.is_configured:
            try:
                logger.info("Initializing Stellar onboarding service...")
                from stellar_onboarding_service import StellarOnboardingService
                
                # Check if we have a funding account
                funding_account = config.stellar_onboarding.funding_public
                funding_secret = config.stellar_onboarding.funding_secret
                
                if not funding_account or not funding_secret:
                    # Fallback to distributor account if funding account not configured
                    logger.info("  Using distributor account for funding")
                    funding_account = config.stellar.distributor_public
                    funding_secret = config.stellar.distributor_secret
                
                # Initialize onboarding service
                app.state.stellar_onboarding = StellarOnboardingService(
                    stellar_service=app.state.stellar,
                    funding_account_public=funding_account,
                    funding_account_secret=funding_secret,
                    ubecrc_asset_code='UBECrc',
                    ubecrc_issuer=config.stellar.ubecrc_issuer_public,
                    min_funding_amount=config.stellar_onboarding.total_funding_amount,
                    database=app.state.db
                )
                
                # Check funding capacity
                capacity = await app.state.stellar_onboarding.check_funding_capacity()
                logger.info(f"✓ Stellar onboarding service initialized")
                logger.info(f"  Funding balance: {capacity['xlm_balance']} XLM")
                logger.info(f"  Can create: {capacity['wallets_can_create']} wallets")
                
            except Exception as e:
                logger.warning(f"Stellar onboarding initialization failed: {e}")
                logger.info("⚠  Continuing without onboarding service")
                app.state.stellar_onboarding = None
        else:
            logger.info("⚠  Stellar onboarding disabled (no funding account)")
        
        # 6. Pattern Recognition
        app.state.pattern_engine = None
        logger.info("✓ Pattern recognition ready")
        
        # Register services with the service registry
        registry.register("database", app.state.db)
        if app.state.stellar:
            registry.register("stellar", app.state.stellar)
        if app.state.ipfs:
            registry.register("ipfs", app.state.ipfs)
        registry.register("observation_service", app.state.observation_service)
        if app.state.stellar_onboarding:
            registry.register("stellar_onboarding", app.state.stellar_onboarding)
        
        logger.info("")
        logger.info("="*60)
        logger.info("  UBEC RECIPROCAL SYSTEM READY")
        logger.info("="*60)
        logger.info("")
        logger.info(f"  🌍 English Pages:")
        logger.info(f"    Landing Page: http://localhost:{config.API_PORT}/")
        logger.info(f"    Steward Registration: http://localhost:{config.API_PORT}/steward")
        logger.info(f"    Device Registration: http://localhost:{config.API_PORT}/sensebox")
        logger.info(f"    Network Status: http://localhost:{config.API_PORT}/network-status")
        logger.info(f"    Imprint: http://localhost:{config.API_PORT}/impressum-en.html")
        logger.info(f"    Privacy: http://localhost:{config.API_PORT}/datenschutz-en.html")
        logger.info("")
        logger.info(f"  🇩🇪 Deutsche Seiten:")
        logger.info(f"    Startseite: http://localhost:{config.API_PORT}/index-de.html")
        logger.info(f"    Steward-Registrierung: http://localhost:{config.API_PORT}/steward-de.html")
        logger.info(f"    Geräteregistrierung: http://localhost:{config.API_PORT}/sensebox-de.html")
        logger.info(f"    Netzwerkstatus: http://localhost:{config.API_PORT}/status-de.html")
        logger.info(f"    Impressum: http://localhost:{config.API_PORT}/impressum-de.html")
        logger.info(f"    Datenschutz: http://localhost:{config.API_PORT}/datenschutz-de.html")
        logger.info("")
        logger.info(f"  🇵🇱 Polskie Strony:")
        logger.info(f"    Strona główna: http://localhost:{config.API_PORT}/index-pl.html")
        logger.info(f"    Rejestracja Zarządcy: http://localhost:{config.API_PORT}/steward-pl.html")
        logger.info(f"    Rejestracja Urządzenia: http://localhost:{config.API_PORT}/sensebox-pl.html")
        logger.info(f"    Status Sieci: http://localhost:{config.API_PORT}/status-pl.html")
        logger.info(f"    Stopka Prawna: http://localhost:{config.API_PORT}/impressum-pl.html")
        logger.info(f"    Polityka Prywatności: http://localhost:{config.API_PORT}/datenschutz-pl.html")
        logger.info("")
        logger.info(f"  API Docs: http://localhost:{config.API_PORT}/docs")
        logger.info(f"  Reciprocal Economy: ACTIVE")
        logger.info("")
        logger.info("  Services Active:")
        logger.info(f"    - Database: {'✓' if app.state.db else '✗'}")
        logger.info(f"    - Stellar: {'✓' if app.state.stellar else '✗'}")
        logger.info(f"    - IPFS: {'✓' if app.state.ipfs else '✗'}")
        logger.info(f"    - Wallet Creation: {'✓' if app.state.stellar_onboarding else '✗'}")
        logger.info(f"    - Multilingual: ✓")
        logger.info(f"    - Legal Pages: ✓")
        logger.info(f"    - Favicon Support: ✓")
        logger.info("")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}", exc_info=True)
        raise
    
    yield  # Application runs here
    
    # Graceful shutdown
    logger.info("Shutting down UBEC reciprocal system...")
    
    if hasattr(app.state, 'db'):
        await app.state.db.close()
        logger.info("✓ Database connection closed")
    
    if hasattr(app.state, 'stellar') and app.state.stellar:
        await app.state.stellar.close()
        logger.info("✓ Stellar connection closed")
    
    if hasattr(app.state, 'stellar_onboarding') and app.state.stellar_onboarding:
        await app.state.stellar_onboarding.close()
        logger.info("✓ Stellar onboarding service closed")
    
    logger.info("System shutdown complete")


# ==================================================
# APPLICATION CREATION
# ==================================================

app = FastAPI(
    title="Ubuntu Economic Commons DAO - Living Labs Initiative - Environmental Monitoring API",
    description="""
    # From Seeds to Blockchain: Growing the Future
    ## Multilingual Reciprocal Value Exchange for Environmental Monitoring
    
    A comprehensive environmental monitoring system implementing reciprocal economy
    principles through IoT sensors, phenomenological observation, and blockchain technology.
    
    ### Core Principles:
    - Environmental sensors as conscious observers
    - Data as reciprocal value exchange
    - Blockchain verification of contributions
    - UBECrc token distribution for stewardship
    - **Automated wallet creation for new users**
    
    ### Multilingual Support:
    - 🌍 English (Primary)
    - 🇩🇪 Deutsch (German)
    - 🇵🇱 Polski (Polish)
    
    ### Features:
    - Automatic Stellar wallet generation
    - Account funding with 5+ XLM
    - UBECrc trustline creation
    - Secure credential delivery
    
    ### Legal Compliance:
    - EU GDPR compliant
    - German TMG § 5 compliant (Impressum)
    - Blockchain data protection considerations
    """,
    version="3.0.6",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# ==================================================
# CORS MIDDLEWARE
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ==================================================
# STATIC FILES - REGISTRATION PORTAL
# ==================================================

# Mount the registration portal static files
portal_path = Path("register_portal")
if portal_path.exists():
    app.mount("/portal", StaticFiles(directory="register_portal"), name="portal")
    logger.info(f"✓ Registration portal mounted at /portal")
else:
    logger.warning(f"⚠  Registration portal not found at {portal_path}")

# ==================================================
# IMPORT AND MOUNT ROUTERS
# ==================================================

# Import the phenomenological API routes
from phenomenological_api import pheno_router

# Mount the phenomenological API router
app.include_router(pheno_router)

# Import and mount Stellar onboarding routes
try:
    from stellar_onboarding_routes import router as onboarding_router
    app.include_router(onboarding_router)
    logger.info("✓ Stellar onboarding routes mounted")
except ImportError as e:
    logger.info(f"⚠  Stellar onboarding routes not available: {e}")

logger.info("✓ Multilingual routes loaded")

# ==================================================
# FAVICON ROUTES (ONLY FOR EXISTING FILES)
# ==================================================

@app.get("/favicon.ico", include_in_schema=False)
async def favicon_ico():
    """Serve favicon.ico"""
    return FileResponse("register_portal/favicon.ico", media_type="image/x-icon")

@app.get("/favicon.svg", include_in_schema=False)
async def favicon_svg():
    """Serve favicon.svg"""
    return FileResponse("register_portal/favicon.svg", media_type="image/svg+xml")

@app.get("/favicon-{size}.png", include_in_schema=False)
async def favicon_png(size: str):
    """Serve PNG favicons (16x16, 32x32, 192x192, 180x180)"""
    valid_sizes = ["16x16", "32x32", "192x192", "180x180"]
    if size in valid_sizes:
        return FileResponse(f"register_portal/favicon-{size}.png", media_type="image/png")
    return Response(status_code=404)

# ==================================================
# ENGLISH PAGES (PRIMARY)
# ==================================================

@app.get("/")
@app.get("/index.html")
@app.get("/index-en.html")
async def index_en():
    """English landing page"""
    return FileResponse("register_portal/index-en.html")

@app.get("/steward")
@app.get("/steward-en.html")
async def steward_en():
    """English steward registration"""
    return FileResponse("register_portal/steward-en.html")

@app.get("/sensebox")
@app.get("/sensebox-en.html")
async def sensebox_en():
    """English device registration"""
    return FileResponse("register_portal/sensebox-en.html")

@app.get("/network-status")
@app.get("/status-en.html")
async def status_en():
    """English network status"""
    return FileResponse("register_portal/status-en.html")

@app.get("/impressum-en.html")
async def impressum_en():
    """English imprint page"""
    return FileResponse("register_portal/impressum-en.html")

@app.get("/datenschutz-en.html")
async def datenschutz_en():
    """English privacy policy"""
    return FileResponse("register_portal/datenschutz-en.html")

# ==================================================
# GERMAN PAGES (DEUTSCHE SEITEN)
# ==================================================

@app.get("/index-de.html")
async def index_de():
    """Deutsche Startseite"""
    return FileResponse("register_portal/index-de.html")

@app.get("/steward-de.html")
async def steward_de():
    """Deutsche Steward-Registrierung"""
    return FileResponse("register_portal/steward-de.html")

@app.get("/sensebox-de.html")
async def sensebox_de():
    """Deutsche Geräteregistrierung"""
    return FileResponse("register_portal/sensebox-de.html")

@app.get("/status-de.html")
async def status_de():
    """Deutscher Netzwerkstatus"""
    return FileResponse("register_portal/status-de.html")

@app.get("/impressum")
@app.get("/impressum-de.html")
async def impressum_de():
    """Deutsches Impressum (Primary Legal Page)"""
    return FileResponse("register_portal/impressum-de.html")

@app.get("/datenschutz")
@app.get("/datenschutz-de.html")
async def datenschutz_de():
    """Deutsche Datenschutzerklärung (Primary Privacy Page)"""
    return FileResponse("register_portal/datenschutz-de.html")

# ==================================================
# POLISH PAGES (POLSKIE STRONY)
# ==================================================

@app.get("/index-pl.html")
async def index_pl():
    """Polska strona główna"""
    return FileResponse("register_portal/index-pl.html")

@app.get("/steward-pl.html")
async def steward_pl():
    """Polska rejestracja zarządcy"""
    return FileResponse("register_portal/steward-pl.html")

@app.get("/sensebox-pl.html")
async def sensebox_pl():
    """Polska rejestracja urządzenia"""
    return FileResponse("register_portal/sensebox-pl.html")

@app.get("/status-pl.html")
async def status_pl():
    """Polski status sieci"""
    return FileResponse("register_portal/status-pl.html")

@app.get("/impressum-pl.html")
async def impressum_pl():
    """Polska stopka prawna"""
    return FileResponse("register_portal/impressum-pl.html")

@app.get("/datenschutz-pl.html")
async def datenschutz_pl():
    """Polska polityka prywatności"""
    return FileResponse("register_portal/datenschutz-pl.html")

# ==================================================
# LEGACY COMPATIBILITY
# ==================================================

@app.get("/register")
async def old_registration_redirect():
    """Legacy /register endpoint"""
    return await steward_en()

# ==================================================
# SYSTEM STATUS ENDPOINTS
# ==================================================

@app.get("/status")
async def status():
    """System status and configuration check"""
    # Check IPFS configuration
    if hasattr(app.state, 'ipfs') and app.state.ipfs:
        ipfs_configured = True
        ipfs_gateway = getattr(app.state.ipfs, 'gateway_url', None)
    else:
        ipfs_configured = bool(os.getenv('PINATA_API_KEY') or os.getenv('IPFS_API_URL'))
        ipfs_gateway = os.getenv('PINATA_GATEWAY_URL', 'https://gateway.pinata.cloud')
    
    return {
        "api": {
            "host": config.API_HOST,
            "port": config.API_PORT,
            "version": "3.0.6"
        },
        "database": {
            "schema": PHENOMENOLOGICAL_SCHEMA,
            "search_path": config.database.search_path,
            "configured": config.database.is_configured
        },
        "stellar": {
            "network": config.stellar.network,
            "asset_code": "UBECrc",
            "issuer": config.stellar.ubecrc_issuer_public,
            "distributor_configured": config.stellar.is_configured
        },
        "stellar_onboarding": {
            "enabled": hasattr(app.state, 'stellar_onboarding') and app.state.stellar_onboarding is not None,
            "funding_available": hasattr(app.state, 'stellar_onboarding') and 
                                app.state.stellar_onboarding is not None
        },
        "ipfs": {
            "configured": ipfs_configured,
            "gateway": ipfs_gateway
        },
        "reciprocal_economy": {
            "observation_value": 7.14,
            "sensor_bonus": 0.5,
            "stewardship_model": True
        },
        "multilingual": {
            "supported_languages": ["en", "de", "pl"],
            "default_language": "en"
        },
        "legal_compliance": {
            "impressum_en": "/impressum-en.html",
            "impressum_de": "/impressum-de.html",
            "impressum_pl": "/impressum-pl.html",
            "datenschutz_en": "/datenschutz-en.html",
            "datenschutz_de": "/datenschutz-de.html",
            "datenschutz_pl": "/datenschutz-pl.html",
            "gdpr_compliant": True
        },
        "environment": config.ENVIRONMENT,
        "debug": config.DEBUG
    }

@app.get("/awareness")
async def awareness_check():
    """Phenomenological awareness check"""
    return {
        "awareness": "I am observing environmental phenomena through technological senses",
        "database": "connected" if hasattr(app.state, 'db') else "disconnected",
        "stellar_network": "connected" if hasattr(app.state, 'stellar') and app.state.stellar else "independent",
        "ipfs_storage": "connected" if hasattr(app.state, 'ipfs') and app.state.ipfs else "ephemeral",
        "reciprocal_economy": "active",
        "stewardship": "engaged",
        "wallet_creation": "enabled" if hasattr(app.state, 'stellar_onboarding') and app.state.stellar_onboarding else "disabled",
        "multilingual": "enabled",
        "languages": ["en", "de", "pl"],
        "legal_compliance": "enabled",
        "favicon_support": "enabled",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v2/system/stats")
async def get_system_stats():
    """
    Get system-wide statistics from the phenomenological database
    Returns counts of observers, observations, devices, and UBEC distributed
    """
    try:
        # Initialize stats with zeros
        stats = {
            "total_observers": 0,
            "total_observations": 0,
            "total_devices": 0,
            "total_ubec": 0,
            "active_patterns": 0
        }
        
        # Check if database is available
        if not hasattr(app.state, 'db'):
            logger.warning("Database not available for stats")
            return stats
        
        db = app.state.db
        
        # Use asyncpg connection pool pattern
        async with db.pool.acquire() as conn:
            # Count total observers (both human and device)
            observer_query = """
                SELECT COUNT(*) as count 
                FROM phenomenological.observers
            """
            result = await conn.fetchrow(observer_query)
            if result:
                stats["total_observers"] = result['count']
            
            # Count devices specifically
            device_query = """
                SELECT COUNT(*) as count 
                FROM phenomenological.observers
                WHERE observer_type = 'device'
            """
            result = await conn.fetchrow(device_query)
            if result:
                stats["total_devices"] = result['count']
            
            # Count total observations
            obs_query = """
                SELECT COUNT(*) as count 
                FROM phenomenological.observations
            """
            result = await conn.fetchrow(obs_query)
            if result:
                stats["total_observations"] = result['count']
            
            # Calculate total UBEC distributed (7.14 per observation)
            if stats["total_observations"] > 0:
                stats["total_ubec"] = round(stats["total_observations"] * 7.14, 2)
            
            # Count active patterns (if patterns table exists)
            try:
                pattern_query = """
                    SELECT COUNT(*) as count 
                    FROM phenomenological.patterns
                    WHERE active = true
                """
                result = await conn.fetchrow(pattern_query)
                if result:
                    stats["active_patterns"] = result['count']
            except Exception:
                # Patterns table might not exist yet
                stats["active_patterns"] = 0
        
        logger.info(f"System stats retrieved: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching system stats: {e}", exc_info=True)
        # Return zeros on error so the page doesn't break
        return {
            "total_observers": 0,
            "total_observations": 0,
            "total_devices": 0,
            "total_ubec": 0,
            "active_patterns": 0
        }

# ==================================================
# DIAGNOSTIC ENDPOINTS
# ==================================================

@app.get("/api/v2/diagnostics")
async def diagnostics():
    """
    Comprehensive diagnostic endpoint to check database connectivity and content
    """
    diagnostics_result = {
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "connected": False,
            "schema": PHENOMENOLOGICAL_SCHEMA,
            "search_path": config.database.search_path,
            "tables": {},
            "sample_data": {}
        },
        "services": {
            "stellar": False,
            "ipfs": False,
            "observation_service": False,
            "stellar_onboarding": False
        },
        "multilingual": {
            "enabled": True,
            "languages": ["en", "de", "pl"]
        },
        "errors": []
    }
    
    # Check database connection
    if hasattr(app.state, 'db'):
        try:
            diagnostics_result["database"]["connected"] = True
            db = app.state.db
            
            # Use asyncpg connection pool pattern
            async with db.pool.acquire() as conn:
                # Check if tables exist
                table_check_query = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = $1
                    ORDER BY table_name
                """
                tables = await conn.fetch(table_check_query, PHENOMENOLOGICAL_SCHEMA)
                diagnostics_result["database"]["tables"] = {
                    "count": len(tables),
                    "names": [t['table_name'] for t in tables]
                }
                
                # Check observers table
                try:
                    obs_count_query = f"""
                        SELECT 
                            COUNT(*) as total,
                            COUNT(CASE WHEN observer_type = 'human' THEN 1 END) as humans,
                            COUNT(CASE WHEN observer_type = 'device' THEN 1 END) as devices
                        FROM {PHENOMENOLOGICAL_SCHEMA}.observers
                    """
                    obs_result = await conn.fetchrow(obs_count_query)
                    diagnostics_result["database"]["sample_data"]["observers"] = {
                        "total": obs_result['total'],
                        "humans": obs_result['humans'],
                        "devices": obs_result['devices']
                    }
                    
                    # Get a sample observer
                    sample_query = f"""
                        SELECT id, observer_type, presence_began
                        FROM {PHENOMENOLOGICAL_SCHEMA}.observers
                        LIMIT 1
                    """
                    sample = await conn.fetchrow(sample_query)
                    if sample:
                        diagnostics_result["database"]["sample_data"]["sample_observer"] = dict(sample)
                        
                except Exception as e:
                    diagnostics_result["errors"].append(f"Error querying observers: {str(e)}")
                
                # Check observations table
                try:
                    observations_count_query = f"""
                        SELECT COUNT(*) as count
                        FROM {PHENOMENOLOGICAL_SCHEMA}.observations
                    """
                    obs_count = await conn.fetchrow(observations_count_query)
                    diagnostics_result["database"]["sample_data"]["observations"] = {
                        "count": obs_count['count']
                    }
                    
                    # Get a sample observation
                    sample_obs_query = f"""
                        SELECT id, observer_id, perceived_at
                        FROM {PHENOMENOLOGICAL_SCHEMA}.observations
                        LIMIT 1
                    """
                    sample_obs = await conn.fetchrow(sample_obs_query)
                    if sample_obs:
                        diagnostics_result["database"]["sample_data"]["sample_observation"] = dict(sample_obs)
                        
                except Exception as e:
                    diagnostics_result["errors"].append(f"Error querying observations: {str(e)}")
                
        except Exception as e:
            diagnostics_result["database"]["connected"] = False
            diagnostics_result["errors"].append(f"Database error: {str(e)}")
    else:
        diagnostics_result["errors"].append("Database not initialized in app.state")
    
    # Check services
    diagnostics_result["services"]["stellar"] = hasattr(app.state, 'stellar') and app.state.stellar is not None
    diagnostics_result["services"]["ipfs"] = hasattr(app.state, 'ipfs') and app.state.ipfs is not None
    diagnostics_result["services"]["observation_service"] = hasattr(app.state, 'observation_service')
    diagnostics_result["services"]["stellar_onboarding"] = hasattr(app.state, 'stellar_onboarding') and app.state.stellar_onboarding is not None
    
    return diagnostics_result


@app.get("/api/v2/test-db-query")
async def test_db_query():
    """
    Simple test endpoint to verify database queries work
    """
    if not hasattr(app.state, 'db'):
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        db = app.state.db
        
        # Use asyncpg connection pool pattern
        async with db.pool.acquire() as conn:
            # Test basic connectivity
            test_query = "SELECT 1 as test"
            test_result = await conn.fetchrow(test_query)
            
            # Test schema query
            schema_query = """
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = $1
            """
            schema_result = await conn.fetchrow(schema_query, PHENOMENOLOGICAL_SCHEMA)
            
            # Test observers count
            observers_query = f"""
                SELECT COUNT(*) as count
                FROM {PHENOMENOLOGICAL_SCHEMA}.observers
            """
            observers_result = await conn.fetchrow(observers_query)
            
            return {
                "success": True,
                "test_connection": dict(test_result) if test_result else None,
                "schema_exists": dict(schema_result) if schema_result else None,
                "observers_count": dict(observers_result) if observers_result else None,
                "schema_used": PHENOMENOLOGICAL_SCHEMA
            }
        
    except Exception as e:
        logger.error(f"Test query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ==================================================
# OBSERVATION ENDPOINTS
# ==================================================

@app.post("/observe")
async def submit_observation(request: Request):
    """
    Simple observation endpoint for Arduino/SenseBox devices
    Compatible with existing sensor infrastructure
    """
    try:
        data = await request.json()
        
        # Extract device info
        device_id = data.get('device_id')
        readings = data.get('readings', {})
        location = data.get('location', {})
        
        if not device_id or not readings:
            raise HTTPException(status_code=400, detail="Missing device_id or readings")
        
        # Use observation service if available
        if hasattr(app.state, 'observation_service'):
            # Process observation through service
            result = await app.state.observation_service.process_observation(
                device_id=device_id,
                readings=readings,
                location=location,
                student_wallet=data.get('student_wallet'),
                metadata=data.get('metadata', {})
            )
            return {
                "success": True,
                "observation_id": result.observation_id,
                "ipfs_cid": result.ipfs_cid,
                "stellar_tx_hash": result.stellar_tx_hash,
                "tokens_distributed": str(result.tokens_distributed),
                "blockchain_verified": result.blockchain_verified,
                "reciprocal_value": float(result.tokens_distributed),
                "message": "Observation received and processed"
            }
        else:
            return {
                "success": True,
                "message": "Observation received",
                "reciprocal_value": 7.14
            }
            
    except Exception as e:
        logger.error(f"Error in observation submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================================================
# MAIN ENTRY POINT
# ==================================================

def main():
    """
    Main entry point for the entire system.
    This is the ONLY function that should start a server.
    """
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║               UBEC RECIPROCAL MONITORING SYSTEM          ║
    ║                                                          ║
    ║               Ubuntu Economic Commons DAO                ║
    ║                  Living Labs Initiative                  ║
    ║              Environmental Monitoring API                ║
    ║                                                          ║
    ║    "From Seeds to Blockchain: Growing the Future        ║
    ║        through Reciprocal Value Exchange"               ║
    ║                                                          ║
    ║      🌍 English + 🇩🇪 Deutsch + 🇵🇱 Polski Support        ║
    ║              + Automated Wallet Creation                 ║
    ║              + EU Legal Compliance                       ║
    ║              + Exact File Routing                        ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    
    Design Principles:
    - Service Pattern with Centralized Execution
    - Reciprocal Economy Model
    - Blockchain Verification
    - Single Entry Point Architecture
    - Multilingual Support (EN/DE/PL)
    - Automated Stellar Wallet Creation
    - EU GDPR & German TMG Compliance
    - EXACT routes for existing files only
    
    Version: 3.0.6 (Fixed Multilingual Routing - Exact Files Only)
    
    Starting system...
    """)
    
    # Run the application
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.AUTO_RELOAD if hasattr(config, 'AUTO_RELOAD') else False,
        log_level=config.LOG_LEVEL.lower(),
        access_log=True
    )

if __name__ == "__main__":
    main()

"""
Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations. This project was made
possible with the assistance of Claude and Anthropic PBC.
"""
