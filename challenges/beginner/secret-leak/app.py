#!/usr/bin/env python3
"""
Vulnerable Web Application
This application has several security issues - can you find them?
"""

from flask import Flask, render_template_string, jsonify
import os

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Company Dashboard</title>
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
        <h1>🏢 Company Internal Dashboard</h1>
        <p>Welcome to the internal company dashboard.</p>
        
        <div class="info-box">
            <h3>System Information</h3>
            <p><strong>Environment:</strong> <code>{{ env_name }}</code></p>
            <p><strong>Version:</strong> <code>{{ version }}</code></p>
        </div>
        
        <div class="info-box">
            <h3>API Endpoints</h3>
            <p>Try accessing:</p>
            <ul>
                <li><code>/api/info</code> - System information</li>
                <li><code>/api/config</code> - Configuration details</li>
            </ul>
        </div>
        
        <div class="info-box">
            <p><em>Note: This is an internal tool. Do not expose sensitive information!</em></p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Main dashboard page"""
    env_name = os.getenv('ENVIRONMENT', 'production')
    version = os.getenv('APP_VERSION', '1.0.0')
    return render_template_string(HTML_TEMPLATE, env_name=env_name, version=version)


@app.route('/api/info')
def api_info():
    """API endpoint that might leak information"""
    info = {
        'app_name': os.getenv('APP_NAME', 'dashboard'),
        'environment': os.getenv('ENVIRONMENT', 'production'),
        'version': os.getenv('APP_VERSION', '1.0.0'),
        'hostname': os.getenv('HOSTNAME', 'unknown'),
        # Oops! This might be too much information
        'node_name': os.getenv('NODE_NAME', ''),
        'pod_name': os.getenv('POD_NAME', ''),
    }
    return jsonify(info)


@app.route('/api/config')
def api_config():
    """API endpoint that exposes configuration"""
    config = {
        'database_host': os.getenv('DATABASE_HOST', 'localhost'),
        'database_port': os.getenv('DATABASE_PORT', '5432'),
        'api_key': os.getenv('API_KEY', ''),
        'secret_token': os.getenv('SECRET_TOKEN', ''),
        # Wait, should we really expose this?
        'admin_password': os.getenv('ADMIN_PASSWORD', ''),
        'flag': os.getenv('FLAG', ''),
    }
    return jsonify(config)


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

