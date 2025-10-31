#!/usr/bin/env python3
"""
Vulnerable Web Application - Header Information Disclosure
This application leaks sensitive information through HTTP headers
"""

from flask import Flask, render_template_string, jsonify, Response
import os

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .info-box { background: #e8f4f8; padding: 15px; margin: 10px 0; border-radius: 4px; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Admin Portal</h1>
        <p>Welcome to the administrative portal.</p>
        
        <div class="info-box">
            <h3>System Status</h3>
            <p><strong>Status:</strong> <code>Operational</code></p>
            <p><strong>Version:</strong> <code>{{ version }}</code></p>
        </div>
        
        <div class="info-box">
            <h3>Available Endpoints</h3>
            <ul>
                <li><code>/</code> - This page</li>
                <li><code>/api/status</code> - System status</li>
                <li><code>/api/users</code> - User list (requires authentication)</li>
            </ul>
        </div>
        
        <div class="info-box">
            <p><em>Note: This portal uses advanced security headers for protection.</em></p>
        </div>
    </div>
</body>
</html>
"""

@app.after_request
def add_headers(response):
    """Add custom headers to all responses - OOPS! This leaks sensitive info"""
    # Security misconfiguration: exposing debug information in headers
    response.headers['X-Powered-By'] = 'Flask/3.0.0'
    response.headers['X-Server-Version'] = os.getenv('APP_VERSION', '1.0.0')
    response.headers['X-Environment'] = os.getenv('ENVIRONMENT', 'production')
    
    # CRITICAL: Exposing sensitive debug information!
    response.headers['X-Debug-Mode'] = 'enabled'
    response.headers['X-Internal-Token'] = os.getenv('INTERNAL_TOKEN', 'dev-token-12345')
    response.headers['X-Database-Path'] = os.getenv('DATABASE_PATH', '/var/lib/db/data.sqlite')
    
    # The flag is leaked in a header!
    response.headers['X-Flag'] = os.getenv('FLAG', 'FLAG{not_set}')
    
    # Additional debug headers that might be useful
    response.headers['X-Request-ID'] = os.urandom(8).hex()
    response.headers['X-Pod-Name'] = os.getenv('POD_NAME', 'unknown')
    
    return response

@app.route('/')
def index():
    """Main portal page"""
    version = os.getenv('APP_VERSION', '1.0.0')
    return render_template_string(HTML_TEMPLATE, version=version)

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    status = {
        'status': 'operational',
        'version': os.getenv('APP_VERSION', '1.0.0'),
        'uptime': '99.9%'
    }
    return jsonify(status)

@app.route('/api/users')
def api_users():
    """Protected endpoint - requires authentication (but headers might leak the token)"""
    auth_token = os.getenv('ADMIN_TOKEN', 'secret-admin-token')
    
    # Simulated authentication check
    # In a real app, this would check the Authorization header
    # But we're exposing the token in response headers!
    
    users = {
        'users': [
            {'id': 1, 'name': 'admin', 'role': 'administrator'},
            {'id': 2, 'name': 'user1', 'role': 'user'}
        ]
    }
    return jsonify(users)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

