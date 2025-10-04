# Environmental Stewardship Registration Portal

A modular, production-ready web application for registering environmental stewards and IoT sensor devices in the Living Science Initiative.

**Attribution**: This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Design Principles](#design-principles)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Development](#development)
- [API Integration](#api-integration)
- [Troubleshooting](#troubleshooting)

## Overview

This registration portal provides a user-friendly interface for:

- **Human Stewards**: Environmental observers who register to contribute phenomenological observations
- **SenseBox Devices**: IoT environmental sensors that automatically collect and submit data
- **System Status**: Real-time network statistics and health monitoring

### Key Features

- ✅ Modular, maintainable codebase following 12 design principles
- ✅ Service-based architecture with centralized orchestration
- ✅ Built-in rate limiting and API error handling
- ✅ Comprehensive form validation
- ✅ Arduino configuration generator for IoT devices
- ✅ Debug console for development
- ✅ Responsive design for mobile and desktop
- ✅ Production-ready with nginx configuration

## Architecture

### Design Philosophy

This project embodies the principle: *"You never change things by fighting the existing reality. To change something, build a new model that makes the existing model obsolete."*

The system operates as a **semi-autonomous holon** - a self-contained yet interconnected component of a larger environmental monitoring ecosystem.

### Technology Stack

- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Web Server**: Nginx
- **API Integration**: RESTful API with async/await patterns
- **No Dependencies**: Zero external JavaScript libraries required

## Design Principles

This project strictly adheres to 12 design principles:

### 1. Modular Design and Architecture
Each module operates as a self-contained holon with clearly defined boundaries. Components interact only through well-defined interfaces.

### 2. Service Pattern with Centralized Execution
All modules implement the service pattern. `main.js` serves as the sole orchestrator and entry point. No standalone execution elsewhere.

### 3. Service Registry for Dependencies
All inter-module dependencies are managed through a central service registry. No direct module imports outside of the registry pattern.

### 4. Single Source of Truth
Each piece of information has exactly one canonical location. No data duplication across modules or configuration files.

### 5. Strict Async Operations
ALL I/O operations use async/await patterns. No blocking operations in any code path.

### 6. No Sync Fallbacks or Backward Compatibility
Clean, forward-looking codebase only. Breaking changes are handled through updates of pertinent modules, not compatibility layers.

### 7. Per-Asset Monitoring with Execution Minimums
Individual asset tracking and limits. Minimum thresholds for execution to prevent micro-transactions.

### 8. No Duplicate Configuration
Each configuration parameter is defined exactly once through centralized configuration management.

### 9. Integrated Rate Limiting
Built-in rate limiting for all external API calls to prevent service abuse and ensure compliance with provider limits.

### 10. Clear Separation of Concerns
Active processing is clearly separated from passive monitoring. Business logic is isolated from infrastructure code.

### 11. Comprehensive Documentation
Every file includes docstrings explaining purpose and usage. All code includes proper attribution.

### 12. Method Singularity (No Redundancy)
Each method is implemented exactly once in the entire codebase. Shared functionality is extracted to common modules.

## Project Structure

```
registration-portal/
├── index.html                          # Main HTML entry point
├── config/
│   └── config.js                       # Centralized configuration
├── styles/
│   ├── base.css                        # Reset, variables, typography
│   ├── components.css                  # Reusable UI components
│   └── layout.css                      # Page layout and structure
├── scripts/
│   ├── main.js                         # Application orchestrator (ONLY entry point)
│   ├── services/
│   │   ├── debug.service.js           # Debug logging service
│   │   └── api.service.js             # API communication service
│   ├── components/
│   │   ├── steward-form.component.js  # Steward registration UI
│   │   ├── sensebox-form.component.js # SenseBox registration UI
│   │   └── status.component.js        # System status display
│   └── utils/
│       ├── validation.js              # Input validation utilities
│       └── arduino-config.js          # Arduino code generator
└── deploy/
    ├── deploy.sh                       # Automated deployment script
    ├── nginx.conf                      # Web server configuration
    └── README.md                       # This file
```

## Installation

### Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Nginx web server
- Sudo/root access
- Backend API server running

### Quick Install

1. **Clone or download the project files**

```bash
# Create project directory
sudo mkdir -p /var/www/registration-portal
cd /var/www/registration-portal

# Copy all project files here
```

2. **Run the deployment script**

```bash
cd deploy
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

The script will:
- Check system requirements
- Create backups of existing files
- Deploy all files to `/var/www/registration-portal`
- Configure nginx
- Set proper permissions

### Manual Installation

If you prefer manual installation:

```bash
# Create directory
sudo mkdir -p /var/www/registration-portal

# Copy files
sudo cp -r * /var/www/registration-portal/

# Set permissions
sudo chown -R www-data:www-data /var/www/registration-portal
sudo chmod -R 755 /var/www/registration-portal

# Configure nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/registration-portal
sudo ln -s /etc/nginx/sites-available/registration-portal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Configuration

### API Endpoint Configuration

Edit `config/config.js` and update the environment-specific settings:

```javascript
const ENV_CONFIG = {
    [ENVIRONMENT.PRODUCTION]: {
        API_HOST: 'your-api-server.com',  // Update this
        API_PORT: '443',                   // Update this
        DEBUG_MODE: false,
        LOG_LEVEL: 'error',
        ENABLE_MOCK: false
    }
};
```

### Nginx Configuration

Edit `deploy/nginx.conf` and update:

```nginx
server_name your-domain.com www.your-domain.com;  # Update this
```

### SSL Setup (Production)

For production deployment with HTTPS:

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Certbot will automatically configure SSL in nginx
```

## Deployment

### Development Deployment

For local development:

```bash
# Option 1: Python HTTP server
cd /path/to/registration-portal
python3 -m http.server 8080

# Option 2: Node.js http-server
npx http-server -p 8080

# Access at: http://localhost:8080
```

### Production Deployment

1. **Update configuration** in `config/config.js`
2. **Run deployment script**: `sudo ./deploy/deploy.sh`
3. **Configure SSL**: `sudo certbot --nginx -d your-domain.com`
4. **Test**: Visit `https://your-domain.com`

### Environment Variables

The application automatically detects the environment based on hostname:

- `localhost` or `127.0.0.1` → Development
- Hostname containing `staging` → Staging
- Other hostnames → Production

## Development

### Local Development

1. Update `config/config.js` with development API endpoint
2. Serve files with any HTTP server
3. Press `Ctrl+D` to toggle debug console
4. Check browser console for detailed logs

### Making Changes

**Important**: Follow the design principles!

- Modify components in their respective files
- Never create duplicate methods
- Always use the service registry
- Update documentation when changing code
- Test thoroughly before deploying

### Code Style

```javascript
/**
 * Function description
 * 
 * @param {Type} paramName - Parameter description
 * @returns {Type} Return description
 */
async function myFunction(paramName) {
    // Keep functions short (20-30 lines max)
    // Single responsibility
    // Clear naming
}
```

### Testing

While this is a frontend-only application, test:

1. **Form Validation**: Try invalid inputs
2. **API Integration**: Test with your backend
3. **Responsive Design**: Test on mobile devices
4. **Browser Compatibility**: Test on major browsers
5. **Error Handling**: Disconnect network and test

## API Integration

### Expected API Endpoints

The application expects these API v2 endpoints:

```
POST /api/v2/observers/register  - Register observer
POST /api/v2/observe             - Submit observation
GET  /api/v2/system/stats        - Get system statistics
GET  /api/v2/health              - Health check
```

### Request Format

**Register Steward:**
```json
{
  "observer_type": "human",
  "external_identity": {
    "name": "John Doe",
    "email": "john@example.com",
    "role": "steward"
  },
  "essence": {
    "organization": "UBEC",
    "stellar_address": "G...",
    "land_relationship": "..."
  },
  "sensory_capacities": {
    "sight": true,
    "hearing": true,
    ...
  }
}
```

**Register SenseBox:**
```json
{
  "observer_type": "device",
  "external_identity": {
    "device_id": "SENS_123...",
    "name": "School Garden Monitor",
    "serial": "123..."
  },
  "essence": {
    "location": {"lat": 52.3476, "lon": 14.5506},
    "sensors": ["hdc1080", "dps310", ...],
    "steward_stellar": "G..."
  },
  "sensory_capacities": {
    "technological": true,
    "temperature": true,
    ...
  }
}
```

### Response Format

```json
{
  "observer_id": "uuid-here",
  "muxed_wallet": "M..." // Optional
}
```

## Troubleshooting

### Portal doesn't load

1. Check nginx is running: `sudo systemctl status nginx`
2. Check file permissions: `ls -la /var/www/registration-portal`
3. Check nginx error log: `sudo tail -f /var/log/nginx/registration-portal-error.log`

### API connection fails

1. Check API endpoint in `config/config.js`
2. Press `Ctrl+D` to open debug console
3. Verify API is running and accessible
4. Check CORS settings if API is on different domain

### Forms not submitting

1. Open browser DevTools (F12)
2. Check Console for JavaScript errors
3. Check Network tab for failed requests
4. Verify form validation passes

### SSL issues

1. Verify certificate: `sudo certbot certificates`
2. Renew if needed: `sudo certbot renew`
3. Check nginx SSL config: `sudo nginx -t`

## Support

For issues or questions:

1. Check this README thoroughly
2. Review browser console for errors
3. Check nginx and application logs
4. Verify API endpoint configuration

## Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

## License

This project is part of the Living Science Initiative at Freie Waldorfschule Frankfurt (Oder).

---

**Last Updated**: 2025-01-29  
**Version**: 2.0.0 (Modular Rewrite)
