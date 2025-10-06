#!/usr/bin/env python3
"""
File Existence Checker for main.py Route Generation
Only create routes for files that actually exist

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

import os
from pathlib import Path

def check_register_portal_files():
    """Check what files actually exist in register_portal directory"""
    
    portal_dir = Path("register_portal")
    
    if not portal_dir.exists():
        print(f"ERROR: {portal_dir} directory does not exist!")
        return None
    
    # Files we're looking for
    html_files = [
        # English
        "index-en.html",
        "steward-en.html", 
        "sensebox-en.html",
        "status-en.html",
        "impressum-en.html",
        "datenschutz-en.html",
        # German
        "index-de.html",
        "steward-de.html",
        "sensebox-de.html", 
        "status-de.html",
        "impressum-de.html",
        "datenschutz-de.html",
        # Polish
        "index-pl.html",
        "steward-pl.html",
        "sensebox-pl.html",
        "status-pl.html", 
        "impressum-pl.html",
        "datenschutz-pl.html",
        # Legacy
        "steward.html",
        "sensebox.html",
        "status.html",
    ]
    
    icon_files = [
        "favicon.ico",
        "favicon.svg",
        "favicon-16x16.png",
        "favicon-32x32.png",
        "favicon-192x192.png",
        "favicon-180x180.png",
        "apple-touch-icon.png",
    ]
    
    existing_html = []
    existing_icons = []
    
    print("\n" + "="*60)
    print("REGISTER_PORTAL FILE EXISTENCE CHECK")
    print("="*60 + "\n")
    
    print("HTML Files:")
    print("-" * 60)
    for file in html_files:
        file_path = portal_dir / file
        exists = file_path.exists()
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"{status:12} - {file}")
        if exists:
            existing_html.append(file)
    
    print("\n" + "-" * 60)
    print("Icon/Favicon Files:")
    print("-" * 60)
    for file in icon_files:
        file_path = portal_dir / file
        exists = file_path.exists()
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"{status:12} - {file}")
        if exists:
            existing_icons.append(file)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"HTML files found: {len(existing_html)}/{len(html_files)}")
    print(f"Icon files found: {len(existing_icons)}/{len(icon_files)}")
    
    return {
        'html': existing_html,
        'icons': existing_icons,
        'portal_exists': True
    }

def generate_route_recommendations(files):
    """Generate route recommendations based on existing files"""
    
    if not files:
        print("\nNo files found - cannot generate routes")
        return
    
    print("\n" + "="*60)
    print("RECOMMENDED ROUTES TO CREATE")
    print("="*60 + "\n")
    
    html_files = files.get('html', [])
    icon_files = files.get('icons', [])
    
    if html_files:
        print("HTML Routes to add to main.py:")
        print("-" * 60)
        for file in sorted(html_files):
            # Determine route path
            if file == 'index-en.html':
                print(f'@app.get("/")\n@app.get("/index-en.html")')
                print(f'async def index_en():\n    return FileResponse("register_portal/{file}")\n')
            elif file.startswith('index-'):
                lang = file.replace('index-', '').replace('.html', '')
                print(f'@app.get("/{file}")')
                print(f'async def index_{lang}():\n    return FileResponse("register_portal/{file}")\n')
            elif file.startswith('steward'):
                if file == 'steward.html':
                    print(f'@app.get("/steward")')
                    print(f'async def steward():\n    return FileResponse("register_portal/{file}")\n')
                else:
                    lang = file.replace('steward-', '').replace('.html', '')
                    print(f'@app.get("/{file}")')
                    print(f'async def steward_{lang}():\n    return FileResponse("register_portal/{file}")\n')
            elif file.startswith('sensebox'):
                if file == 'sensebox.html':
                    print(f'@app.get("/sensebox")')
                    print(f'async def sensebox():\n    return FileResponse("register_portal/{file}")\n')
                else:
                    lang = file.replace('sensebox-', '').replace('.html', '')
                    print(f'@app.get("/{file}")')
                    print(f'async def sensebox_{lang}():\n    return FileResponse("register_portal/{file}")\n')
            elif file.startswith('status'):
                if file == 'status.html':
                    print(f'@app.get("/status")')
                    print(f'async def status():\n    return FileResponse("register_portal/{file}")\n')
                else:
                    lang = file.replace('status-', '').replace('.html', '')
                    print(f'@app.get("/{file}")')
                    print(f'async def status_{lang}():\n    return FileResponse("register_portal/{file}")\n')
            else:
                # Legal pages
                route_name = file.replace('.html', '').replace('-', '_')
                print(f'@app.get("/{file}")')
                print(f'async def {route_name}():\n    return FileResponse("register_portal/{file}")\n')
    
    if icon_files:
        print("\n" + "-" * 60)
        print("Icon Routes to add to main.py:")
        print("-" * 60)
        for file in sorted(icon_files):
            if 'favicon' in file:
                if file.endswith('.ico'):
                    print(f'@app.get("/favicon.ico")')
                    print(f'async def favicon_ico():\n    return FileResponse("register_portal/{file}", media_type="image/x-icon")\n')
                elif file.endswith('.svg'):
                    print(f'@app.get("/favicon.svg")')
                    print(f'async def favicon_svg():\n    return FileResponse("register_portal/{file}", media_type="image/svg+xml")\n')
                elif 'favicon-' in file:
                    # Dynamic size route
                    size = file.replace('favicon-', '').replace('.png', '')
                    print(f'# Add to dynamic route: /favicon-{{size}}.png')
            elif 'apple-touch-icon' in file:
                print(f'@app.get("/apple-touch-icon.png")')
                print(f'async def apple_touch_icon():\n    return FileResponse("register_portal/{file}", media_type="image/png")\n')
    
    print("\n" + "="*60)
    print("CRITICAL: Only create routes for files that exist!")
    print("="*60)

if __name__ == "__main__":
    files = check_register_portal_files()
    if files and files['portal_exists']:
        generate_route_recommendations(files)
    else:
        print("\nCannot proceed - register_portal directory not found")
