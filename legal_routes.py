"""
Legal Pages Router for FastAPI - EU Compliance Module
Serves Impressum and Datenschutz pages as required by EU/German law.

This module provides HTTP endpoints for legally required pages from the register_portal directory.

Design Principles Applied:
- Principle #2: Service Pattern (router only, no standalone execution)
- Principle #10: Clear separation of concerns (legal compliance isolated)

Attribution: This project uses the services of Claude and Anthropic PBC to inform our decisions 
and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

Version: 1.0.0
"""

from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import logging

# Configure module logger
logger = logging.getLogger(__name__)

# Create router for legal pages
router = APIRouter()

# Determine the register_portal directory location
REGISTER_PORTAL_DIR = Path(__file__).parent / "register_portal"

# Log the directory being used
logger.info(f"Legal routes using directory: {REGISTER_PORTAL_DIR}")


@router.get("/impressum", response_class=HTMLResponse, tags=["legal"])
async def impressum():
    """
    Serve the Impressum (legal notice) page.
    Required by German TMG (Telemediengesetz) § 5.
    
    Returns:
        HTMLResponse: The impressum page or fallback message
    """
    impressum_path = REGISTER_PORTAL_DIR / "impressum.html"
    
    if impressum_path.exists():
        logger.info(f"Serving impressum from: {impressum_path}")
        with open(impressum_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    
    # Fallback if file doesn't exist
    logger.warning(f"Impressum file not found at: {impressum_path}")
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Impressum - Living Science Initiative</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 { color: #2E7D32; }
                a { color: #1976D2; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚠️ Impressum Not Found</h1>
                <p>The Impressum page could not be loaded.</p>
                <p>Expected location: <code>register_portal/impressum.html</code></p>
                <p><a href="/">← Back to Home</a></p>
            </div>
        </body>
        </html>
        """,
        status_code=503
    )


@router.get("/datenschutz", response_class=HTMLResponse, tags=["legal"])
async def datenschutz():
    """
    Serve the Datenschutz (privacy policy) page.
    Required by GDPR/DSGVO.
    
    Returns:
        HTMLResponse: The datenschutz page or fallback message
    """
    datenschutz_path = REGISTER_PORTAL_DIR / "datenschutz.html"
    
    if datenschutz_path.exists():
        logger.info(f"Serving datenschutz from: {datenschutz_path}")
        with open(datenschutz_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    
    # Fallback if file doesn't exist
    logger.warning(f"Datenschutz file not found at: {datenschutz_path}")
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Datenschutzerklärung - Living Science Initiative</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 { color: #2E7D32; }
                a { color: #1976D2; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚠️ Datenschutzerklärung Not Found</h1>
                <p>The privacy policy page could not be loaded.</p>
                <p>Expected location: <code>register_portal/datenschutz.html</code></p>
                <p><a href="/">← Back to Home</a></p>
            </div>
        </body>
        </html>
        """,
        status_code=503
    )


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Serve the favicon from register_portal directory.
    
    Returns:
        FileResponse: The favicon file or 404
    """
    favicon_path = REGISTER_PORTAL_DIR / "favicon.ico"
    
    if favicon_path.exists():
        return FileResponse(
            favicon_path,
            media_type="image/x-icon",
            headers={"Cache-Control": "public, max-age=31536000"}
        )
    
    # Return 404 if favicon not found (don't log - normal for browsers to request)
    return Response(status_code=404)


@router.get("/apple-touch-icon.png", include_in_schema=False)
async def apple_touch_icon():
    """
    Serve the Apple touch icon from register_portal directory.
    
    Returns:
        FileResponse: The Apple touch icon or 404
    """
    icon_path = REGISTER_PORTAL_DIR / "apple-touch-icon.png"
    
    if icon_path.exists():
        return FileResponse(
            icon_path,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=31536000"}
        )
    
    return Response(status_code=404)


@router.get("/favicon-{size}.png", include_in_schema=False)
async def favicon_png(size: str):
    """
    Serve PNG favicons of various sizes from register_portal directory.
    
    Args:
        size: The size of the favicon (e.g., "16x16", "32x32", "192x192")
    
    Returns:
        FileResponse: The favicon PNG file or 404
    """
    icon_path = REGISTER_PORTAL_DIR / f"favicon-{size}.png"
    
    if icon_path.exists():
        return FileResponse(
            icon_path,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=31536000"}
        )
    
    return Response(status_code=404)


# Health check endpoint for legal routes
@router.get("/api/legal/health", tags=["legal"])
async def legal_routes_health():
    """
    Check the health of legal compliance routes.
    
    Returns:
        dict: Status of legal pages availability
    """
    impressum_exists = (REGISTER_PORTAL_DIR / "impressum.html").exists()
    datenschutz_exists = (REGISTER_PORTAL_DIR / "datenschutz.html").exists()
    favicon_exists = (REGISTER_PORTAL_DIR / "favicon.ico").exists()
    
    return {
        "status": "healthy" if (impressum_exists and datenschutz_exists) else "degraded",
        "legal_pages": {
            "impressum": {
                "available": impressum_exists,
                "path": str(REGISTER_PORTAL_DIR / "impressum.html")
            },
            "datenschutz": {
                "available": datenschutz_exists,
                "path": str(REGISTER_PORTAL_DIR / "datenschutz.html")
            }
        },
        "assets": {
            "favicon": {
                "available": favicon_exists,
                "path": str(REGISTER_PORTAL_DIR / "favicon.ico")
            }
        },
        "compliance": {
            "tmg_section_5": impressum_exists,  # German TMG § 5 requirement
            "gdpr": datenschutz_exists  # GDPR/DSGVO requirement
        },
        "directory": str(REGISTER_PORTAL_DIR),
        "directory_exists": REGISTER_PORTAL_DIR.exists()
    }


"""
Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations. This project was made
possible with the assistance of Claude and Anthropic PBC.
"""
