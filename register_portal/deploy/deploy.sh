#!/bin/bash

# ==========================================
# Environmental Stewardship Portal
# Deployment Script
# ==========================================
# 
# This script automates the deployment of the registration portal.
# Follows Design Principle #11 (Comprehensive Documentation)
# 
# Attribution: This project uses the services of Claude and Anthropic PBC.
# ==========================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="registration-portal"
DEPLOY_DIR="/var/www/${PROJECT_NAME}"
BACKUP_DIR="/var/backups/${PROJECT_NAME}"
NGINX_CONFIG="/etc/nginx/sites-available/${PROJECT_NAME}"
NGINX_ENABLED="/etc/nginx/sites-enabled/${PROJECT_NAME}"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_requirements() {
    print_header "Checking Requirements"
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
    
    # Check for required commands
    local required_commands=("nginx" "systemctl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            print_error "$cmd is not installed"
            exit 1
        else
            print_success "$cmd is available"
        fi
    done
}

create_backup() {
    print_header "Creating Backup"
    
    if [ -d "$DEPLOY_DIR" ]; then
        local timestamp=$(date +%Y%m%d_%H%M%S)
        local backup_path="${BACKUP_DIR}/${timestamp}"
        
        mkdir -p "$BACKUP_DIR"
        cp -r "$DEPLOY_DIR" "$backup_path"
        
        print_success "Backup created at: $backup_path"
    else
        print_info "No existing deployment to backup"
    fi
}

deploy_files() {
    print_header "Deploying Files"
    
    # Create deployment directory
    mkdir -p "$DEPLOY_DIR"
    
    # Copy all files
    print_info "Copying files to $DEPLOY_DIR..."
    
    # Create directory structure
    mkdir -p "$DEPLOY_DIR"/{config,scripts/{services,components,utils},styles}
    
    # Copy files (assuming script is run from project root)
    cp index.html "$DEPLOY_DIR/"
    cp config/config.js "$DEPLOY_DIR/config/"
    cp scripts/services/*.js "$DEPLOY_DIR/scripts/services/" 2>/dev/null || true
    cp scripts/components/*.js "$DEPLOY_DIR/scripts/components/" 2>/dev/null || true
    cp scripts/utils/*.js "$DEPLOY_DIR/scripts/utils/" 2>/dev/null || true
    cp scripts/main.js "$DEPLOY_DIR/scripts/"
    cp styles/*.css "$DEPLOY_DIR/styles/"
    
    # Set proper permissions
    chown -R www-data:www-data "$DEPLOY_DIR"
    chmod -R 755 "$DEPLOY_DIR"
    
    print_success "Files deployed successfully"
}

configure_nginx() {
    print_header "Configuring Nginx"
    
    # Check if nginx config exists
    if [ -f "nginx.conf" ]; then
        cp nginx.conf "$NGINX_CONFIG"
        
        # Enable site if not already enabled
        if [ ! -L "$NGINX_ENABLED" ]; then
            ln -s "$NGINX_CONFIG" "$NGINX_ENABLED"
            print_success "Nginx site enabled"
        else
            print_info "Nginx site already enabled"
        fi
        
        # Test nginx configuration
        if nginx -t &> /dev/null; then
            print_success "Nginx configuration is valid"
        else
            print_error "Nginx configuration test failed"
            nginx -t
            exit 1
        fi
        
        # Reload nginx
        systemctl reload nginx
        print_success "Nginx reloaded"
    else
        print_warning "nginx.conf not found - skipping nginx configuration"
        print_info "You'll need to configure nginx manually"
    fi
}

configure_ssl() {
    print_header "SSL Configuration"
    
    print_info "For production, you should set up SSL using Let's Encrypt:"
    echo ""
    echo "  sudo apt-get install certbot python3-certbot-nginx"
    echo "  sudo certbot --nginx -d your-domain.com"
    echo ""
    print_warning "SSL setup skipped - configure manually for production"
}

show_completion_message() {
    print_header "Deployment Complete"
    
    echo ""
    print_success "Registration portal deployed successfully!"
    echo ""
    print_info "Deployment location: $DEPLOY_DIR"
    print_info "Nginx configuration: $NGINX_CONFIG"
    echo ""
    print_warning "Next steps:"
    echo "  1. Update config/config.js with your API endpoint"
    echo "  2. Configure SSL for production (see above)"
    echo "  3. Test the application at http://your-server-ip/"
    echo ""
    print_info "Attribution: This project uses the services of Claude and Anthropic PBC"
    echo ""
}

# Main deployment flow
main() {
    print_header "Environmental Stewardship Portal Deployment"
    echo ""
    
    check_requirements
    create_backup
    deploy_files
    configure_nginx
    configure_ssl
    show_completion_message
}

# Run main function
main
