#!/usr/bin/env python3
"""
Simple Python application that exposes Prometheus metrics
"""
from flask import Flask
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import random
import time

app = Flask(__name__)

# Define metrics
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'status'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method'])
active_connections = Gauge('active_connections', 'Number of active connections')
requests_per_second = Gauge('requests_per_second', 'Requests per second')

@app.route('/')
def index():
    start_time = time.time()
    
    # Simulate some processing time
    time.sleep(random.uniform(0.01, 0.1))
    
    # Increment counters
    status = '200' if random.random() > 0.05 else '500'  # 5% error rate
    http_requests_total.labels(method='GET', status=status).inc()
    
    # Record duration
    duration = time.time() - start_time
    http_request_duration_seconds.labels(method='GET').observe(duration)
    
    # Update active connections (simulate)
    active_connections.set(random.randint(5, 50))
    
    return f'''
    <h1>Python Metrics Demo</h1>
    <p>This application exposes Prometheus metrics</p>
    <ul>
        <li><a href="/metrics">/metrics</a> - Prometheus metrics endpoint</li>
        <li><a href="/health">/health</a> - Health check</li>
    </ul>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

