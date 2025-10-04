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

Version: 3.0.3 (Fixed Routes for Existing Files)
"""

import os
import sys
import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
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
    logger.info("║" + "    Single Entry Point Architecture v3.0.3".center(58) + "║")
    logger.info("║" + "    🌍 English + 🇩🇪 Deutsch Support".center(58) + "║")
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
    logger.info(f"  Multilingual: English + Deutsch")
    
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
                logger.info("⚠ Continuing without Stellar integration")
                app.state.stellar = None
        else:
            logger.info("⚠ Stellar integration disabled (no distributor key)")
        
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
                logger.info("⚠ Continuing without IPFS")
                app.state.ipfs = None
        else:
            logger.info("⚠ IPFS disabled (no configuration)")
        
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
        
        # 5. Pattern Recognition
        app.state.pattern_engine = None
        logger.info("✓ Pattern recognition ready")
        
        # Register services with the service registry
        registry.register("database", app.state.db)
        if app.state.stellar:
            registry.register("stellar", app.state.stellar)
        if app.state.ipfs:
            registry.register("ipfs", app.state.ipfs)
        registry.register("observation_service", app.state.observation_service)
        
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
        logger.info(f"    Impressum: http://localhost:{config.API_PORT}/impressum")
        logger.info(f"    Datenschutz: http://localhost:{config.API_PORT}/datenschutz")
        logger.info("")
        logger.info(f"  API Docs: http://localhost:{config.API_PORT}/docs")
        logger.info(f"  Reciprocal Economy: ACTIVE")
        logger.info("")
        logger.info("  Services Active:")
        logger.info(f"    - Database: {'✓' if app.state.db else '✗'}")
        logger.info(f"    - Stellar: {'✓' if app.state.stellar else '✗'}")
        logger.info(f"    - IPFS: {'✓' if app.state.ipfs else '✗'}")
        logger.info(f"    - Multilingual: ✓")
        logger.info(f"    - Legal Pages: ✓")
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
    
    ### Multilingual Support:
    - 🌍 English (Primary)
    - 🇩🇪 Deutsch (German)
    
    ### Legal Compliance:
    - EU GDPR compliant
    - German TMG § 5 compliant (Impressum)
    - Blockchain data protection considerations
    """,
    version="3.0.3",
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
    logger.warning(f"⚠ Registration portal not found at {portal_path}")

# ==================================================
# IMPORT AND MOUNT ROUTERS
# ==================================================

# Import the phenomenological API routes
from phenomenological_api import pheno_router

# Mount the phenomenological API router
app.include_router(pheno_router)

# Import and mount legal pages router (EU compliance)
# NOTE: Commenting out because routes are defined directly in main.py
# If you have additional legal routes in legal_routes.py, uncomment this
# try:
#     from legal_routes import router as legal_router
#     app.include_router(legal_router, tags=['legal'])
#     logger.info("✓ Legal compliance routes loaded from legal_routes.py")
# except ImportError as e:
#     logger.info(f"  Legal routes defined in main.py (legal_routes.py not found)")
logger.info("✓ Legal compliance routes defined in main.py")

# ==================================================
# CORE ENDPOINTS - ENGLISH PAGES
# ==================================================

@app.get("/")
async def root():
    """Landing page - Beautiful animated home page (English)"""
    # Try English version first
    index_path = Path("register_portal/index.html")
    if index_path.exists():
        return FileResponse("register_portal/index.html")
    
    # Try index-en.html as alternative
    index_en_path = Path("register_portal/index-en.html")
    if index_en_path.exists():
        return FileResponse("register_portal/index-en.html")
    
    # Fallback to simple HTML if landing page not found
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ubuntu Economic Commons DAO - Living Labs Initiative - Environmental Monitoring API</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 40px 20px;
                background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%);
            }
            h1 { color: #2E7D32; }
            h2 { color: #388E3C; }
            .container {
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .endpoints {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .endpoint-card {
                background: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                transition: transform 0.2s;
            }
            .endpoint-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            .endpoint-card h3 {
                margin-top: 0;
                color: #43A047;
            }
            a {
                color: #1976D2;
                text-decoration: none;
            }
            a:hover { text-decoration: underline; }
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #E0E0E0;
                text-align: center;
                font-size: 0.9rem;
                color: #757575;
            }
            .footer a {
                margin: 0 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌱 Ubuntu Economic Commons DAO - Living Labs Initiative - Environmental Monitoring API</h1>
            <h2>Quick Links</h2>
            <div class="endpoints">
                <div class="endpoint-card">
                    <h3>🌍 Become a Steward</h3>
                    <a href="/steward">Register Now →</a>
                </div>
                <div class="endpoint-card">
                    <h3>📡 Register Device</h3>
                    <a href="/sensebox">Connect Device →</a>
                </div>
                <div class="endpoint-card">
                    <h3>📊 Network Status</h3>
                    <a href="/network-status">View Status →</a>
                </div>
            </div>
            <div class="footer">
                <a href="/impressum">Impressum</a>
                <a href="/datenschutz">Datenschutz</a>
                <a href="/docs">API Documentation</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/steward")
async def steward_registration():
    """Steward/Observer registration page (English)"""
    # Try steward-en.html first (English version)
    steward_en_path = Path("register_portal/steward-en.html")
    if steward_en_path.exists():
        return FileResponse("register_portal/steward-en.html")
    
    # Try steward.html as alternative
    steward_path = Path("register_portal/steward.html")
    if steward_path.exists():
        return FileResponse("register_portal/steward.html")
    
    # Fallback to German version if no English found
    steward_de_path = Path("register_portal/steward-de.html")
    if steward_de_path.exists():
        logger.warning("English steward page not found, serving German version")
        return FileResponse("register_portal/steward-de.html")
    
    return HTMLResponse(
        content="<h1>Steward Registration Page Not Found</h1><p>Please ensure steward-en.html or steward.html exists in register_portal/</p>",
        status_code=404
    )

@app.get("/sensebox")
async def sensebox_registration():
    """SenseBox/Device registration page (English)"""
    # Try sensebox-en.html first (English version)
    sensebox_en_path = Path("register_portal/sensebox-en.html")
    if sensebox_en_path.exists():
        return FileResponse("register_portal/sensebox-en.html")
    
    # Try sensebox.html as alternative
    sensebox_path = Path("register_portal/sensebox.html")
    if sensebox_path.exists():
        return FileResponse("register_portal/sensebox.html")
    
    # Fallback to German version if no English found
    sensebox_de_path = Path("register_portal/sensebox-de.html")
    if sensebox_de_path.exists():
        logger.warning("English sensebox page not found, serving German version")
        return FileResponse("register_portal/sensebox-de.html")
    
    return HTMLResponse(
        content="<h1>Device Registration Page Not Found</h1><p>Please ensure sensebox-en.html or sensebox.html exists in register_portal/</p>",
        status_code=404
    )

@app.get("/network-status")
async def network_status():
    """Network status dashboard page (English)"""
    # Try status-en.html first (English version)
    status_en_path = Path("register_portal/status-en.html")
    if status_en_path.exists():
        return FileResponse("register_portal/status-en.html")
    
    # Try status.html as alternative
    status_path = Path("register_portal/status.html")
    if status_path.exists():
        return FileResponse("register_portal/status.html")
    
    # Fallback to German version if no English found
    status_de_path = Path("register_portal/status-de.html")
    if status_de_path.exists():
        logger.warning("English status page not found, serving German version")
        return FileResponse("register_portal/status-de.html")
    
    return HTMLResponse(
        content="<h1>Network Status Page Not Found</h1><p>Please ensure status-en.html or status.html exists in register_portal/</p>",
        status_code=404
    )

# ==================================================
# GERMAN PAGES (DEUTSCHE SEITEN)
# ==================================================

@app.get("/index-de.html")
async def index_de():
    """Startseite - Deutsche Version"""
    index_de_path = Path("register_portal/index-de.html")
    
    if index_de_path.exists():
        return FileResponse("register_portal/index-de.html")
    else:
        return HTMLResponse(
            content="<h1>Deutsche Startseite nicht gefunden</h1><p>Bitte stellen Sie sicher, dass index-de.html im Verzeichnis register_portal/ existiert</p>",
            status_code=404
        )

@app.get("/steward-de.html")
async def steward_de():
    """Steward-Registrierung - Deutsche Version"""
    steward_de_path = Path("register_portal/steward-de.html")
    
    if steward_de_path.exists():
        return FileResponse("register_portal/steward-de.html")
    else:
        return HTMLResponse(
            content="<h1>Steward-Registrierungsseite nicht gefunden</h1><p>Bitte stellen Sie sicher, dass steward-de.html im Verzeichnis register_portal/ existiert</p>",
            status_code=404
        )

@app.get("/sensebox-de.html")
async def sensebox_de():
    """Geräteregistrierung - Deutsche Version"""
    sensebox_de_path = Path("register_portal/sensebox-de.html")
    
    if sensebox_de_path.exists():
        return FileResponse("register_portal/sensebox-de.html")
    else:
        return HTMLResponse(
            content="<h1>Geräteregistrierungsseite nicht gefunden</h1><p>Bitte stellen Sie sicher, dass sensebox-de.html im Verzeichnis register_portal/ existiert</p>",
            status_code=404
        )

@app.get("/status-de.html")
async def status_de():
    """Netzwerkstatus - Deutsche Version"""
    status_de_path = Path("register_portal/status-de.html")
    
    if status_de_path.exists():
        return FileResponse("register_portal/status-de.html")
    else:
        return HTMLResponse(
            content="<h1>Netzwerkstatus-Seite nicht gefunden</h1><p>Bitte stellen Sie sicher, dass status-de.html im Verzeichnis register_portal/ existiert</p>",
            status_code=404
        )

# ==================================================
# LEGAL PAGES - GERMAN (PRIMARY)
# ==================================================

@app.get("/impressum")
async def impressum():
    """Impressum (German legal requirement) - German version"""
    # Try impressum.html first (primary German version)
    impressum_path = Path("register_portal/impressum.html")
    if impressum_path.exists():
        return FileResponse("register_portal/impressum.html")
    
    # Fallback to impressum-de.html
    impressum_de_path = Path("register_portal/impressum-de.html")
    if impressum_de_path.exists():
        return FileResponse("register_portal/impressum-de.html")
    
    return HTMLResponse(
        content="<h1>Impressum nicht gefunden</h1><p>Please ensure impressum.html or impressum-de.html exists in register_portal/</p>",
        status_code=404
    )

@app.get("/datenschutz")
async def datenschutz():
    """Datenschutzerklärung (Privacy Policy) - German version"""
    # Try datenschutz.html first (primary German version)
    datenschutz_path = Path("register_portal/datenschutz.html")
    if datenschutz_path.exists():
        return FileResponse("register_portal/datenschutz.html")
    
    # Fallback to datenschutz-de.html
    datenschutz_de_path = Path("register_portal/datenschutz-de.html")
    if datenschutz_de_path.exists():
        return FileResponse("register_portal/datenschutz-de.html")
    
    return HTMLResponse(
        content="<h1>Datenschutzerklärung nicht gefunden</h1><p>Please ensure datenschutz.html or datenschutz-de.html exists in register_portal/</p>",
        status_code=404
    )

# ==================================================
# ENGLISH LEGAL PAGES
# ==================================================

@app.get("/impressum-en.html")
async def impressum_en():
    """Imprint page (English version)"""
    impressum_en_path = Path("register_portal/impressum-en.html")
    
    if impressum_en_path.exists():
        return FileResponse("register_portal/impressum-en.html")
    else:
        return HTMLResponse(
            content="<h1>Imprint Page Not Found</h1><p>Please ensure impressum-en.html exists in register_portal/</p>",
            status_code=404
        )

@app.get("/datenschutz-en.html")
async def datenschutz_en():
    """Privacy Policy page (English version)"""
    datenschutz_en_path = Path("register_portal/datenschutz-en.html")
    
    if datenschutz_en_path.exists():
        return FileResponse("register_portal/datenschutz-en.html")
    else:
        return HTMLResponse(
            content="<h1>Privacy Policy Page Not Found</h1><p>Please ensure datenschutz-en.html exists in register_portal/</p>",
            status_code=404
        )

# ==================================================
# DIRECT HTML FILE ROUTES (for .html requests)
# ==================================================

@app.get("/index.html")
async def index_html():
    """Direct HTML file request for English index page"""
    return await root()

@app.get("/index-en.html")
async def index_en_html():
    """Direct HTML file request for English index page (alternative naming)"""
    return await root()

@app.get("/steward.html")
async def steward_html():
    """Direct HTML file request for steward page"""
    return await steward_registration()

@app.get("/sensebox.html")
async def sensebox_html():
    """Direct HTML file request for sensebox page"""
    return await sensebox_registration()

@app.get("/status.html")
async def status_html():
    """Direct HTML file request for status page"""
    return await network_status()

@app.get("/impressum.html")
async def impressum_html():
    """Direct HTML file request for impressum page"""
    return await impressum()

@app.get("/datenschutz.html")
async def datenschutz_html():
    """Direct HTML file request for datenschutz page"""
    return await datenschutz()

# ==================================================
# LEGACY/COMPATIBILITY ENDPOINTS
# ==================================================

@app.get("/register")
async def old_registration_redirect():
    """
    Legacy /register endpoint - redirects to steward registration
    Maintains backward compatibility
    """
    return await steward_registration()

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
            "version": "3.0.3"
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
            "supported_languages": ["en", "de"],
            "default_language": "en"
        },
        "legal_compliance": {
            "impressum_en": "/impressum-en.html",
            "impressum_de": "/impressum",
            "datenschutz_en": "/datenschutz-en.html",
            "datenschutz_de": "/datenschutz",
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
        "multilingual": "enabled",
        "languages": ["en", "de"],
        "legal_compliance": "enabled",
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
        
        # FIXED: Use asyncpg connection pool pattern
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
            "observation_service": False
        },
        "multilingual": {
            "enabled": True,
            "languages": ["en", "de"]
        },
        "errors": []
    }
    
    # Check database connection
    if hasattr(app.state, 'db'):
        try:
            diagnostics_result["database"]["connected"] = True
            db = app.state.db
            
            # FIXED: Use asyncpg connection pool pattern
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
        
        # FIXED: Use asyncpg connection pool pattern
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
    ║         🌍 English + 🇩🇪 Deutsch Support                 ║
    ║              + EU Legal Compliance                       ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    
    Design Principles:
    - Service Pattern with Centralized Execution
    - Reciprocal Economy Model
    - Blockchain Verification
    - Single Entry Point Architecture
    - Multilingual Support (EN/DE)
    - EU GDPR & German TMG Compliance
    
    Version: 3.0.3 (Fixed Routes for Existing Files)
    
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
