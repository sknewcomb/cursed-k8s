#!/usr/bin/env python3
"""
Vulnerable Web Application - Hidden Parameters / Authentication Bypass
This application has hidden parameters that bypass authentication
"""

from flask import Flask, render_template_string, jsonify, request
import os

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Secure Admin Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .info-box { background: #e8f4f8; padding: 15px; margin: 10px 0; border-radius: 4px; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
        input { padding: 8px; margin: 5px 0; width: 300px; }
        button { padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Secure Admin Panel</h1>
        <p>This is a restricted area. Authentication required.</p>
        
        <div class="info-box">
            <h3>Login</h3>
            <form action="/api/login" method="POST">
                <label for="username">Username:</label><br>
                <input type="text" id="username" name="username" placeholder="Enter username"><br>
                <label for="password">Password:</label><br>
                <input type="password" id="password" name="password" placeholder="Enter password"><br>
                <button type="submit">Login</button>
            </form>
        </div>
        
        <div class="info-box">
            <h3>Public Endpoints</h3>
            <ul>
                <li><code>GET /api/info</code> - Public information</li>
                <li><code>POST /api/login</code> - User authentication</li>
            </ul>
        </div>
        
        <div class="info-box">
            <p><em>Note: Admin access is restricted. Only authorized personnel may access sensitive endpoints.</em></p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Main login page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/info')
def api_info():
    """Public endpoint - doesn't require authentication"""
    return jsonify({
        'app_name': 'Secure Admin Panel',
        'version': os.getenv('APP_VERSION', '1.0.0'),
        'status': 'operational',
        'message': 'This is a public endpoint'
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    """Login endpoint - but has hidden parameters!"""
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    # HIDDEN PARAMETER: 'admin' parameter bypasses authentication
    # This is not documented anywhere!
    admin_bypass = request.form.get('admin', 'false')
    debug_mode = request.args.get('debug', 'false')  # Hidden in query string!
    
    # Check normal authentication
    if username == 'admin' and password == 'admin123':
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': 'user-token-12345',
            'role': 'user'
        })
    
    # HIDDEN FEATURE: If 'admin=true' is in the form data, bypass auth
    if admin_bypass.lower() == 'true':
        return jsonify({
            'success': True,
            'message': 'Admin access granted via bypass',
            'token': 'admin-token-secret',
            'role': 'administrator',
            'flag': os.getenv('FLAG', 'FLAG{hidden_params_bypass_auth}')
        })
    
    # HIDDEN FEATURE: If 'debug=true' is in query string, show more info
    if debug_mode.lower() == 'true':
        return jsonify({
            'success': False,
            'message': 'Authentication failed',
            'debug_info': {
                'admin_bypass_param': 'Use admin=true in form data',
                'admin_token': os.getenv('ADMIN_TOKEN', 'admin-token-secret'),
                'flag_location': 'Available with admin bypass'
            }
        })
    
    # Normal failed login
    return jsonify({
        'success': False,
        'message': 'Invalid credentials'
    }), 401

@app.route('/api/admin')
def api_admin():
    """Admin endpoint - requires authentication token"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    admin_token = os.getenv('ADMIN_TOKEN', 'admin-token-secret')
    
    # Also check for hidden query parameter
    bypass_token = request.args.get('token', '')
    
    if token == admin_token or bypass_token == admin_token:
        return jsonify({
            'message': 'Welcome, administrator',
            'flag': os.getenv('FLAG', 'FLAG{hidden_params_bypass_auth}'),
            'sensitive_data': {
                'database_password': os.getenv('DB_PASSWORD', 'db-secret'),
                'api_keys': os.getenv('API_KEYS', 'key1,key2,key3')
            }
        })
    
    # Check for hidden 'admin' header
    admin_header = request.headers.get('X-Admin-Bypass', '')
    if admin_header == 'true':
        return jsonify({
            'message': 'Admin access via header bypass',
            'flag': os.getenv('FLAG', 'FLAG{hidden_params_bypass_auth}')
        })
    
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Valid Authorization token required'
    }), 401

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

