#!/usr/bin/env python3
"""
K3s Status Page - Application Status Monitor
A simple Flask application that monitors Kubernetes deployments and displays their status
"""

from flask import Flask, render_template, jsonify, request
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os
from datetime import datetime
import json

app = Flask(__name__)

# Try to load kubeconfig, fallback to in-cluster config
try:
    config.load_kube_config()
except:
    try:
        config.load_incluster_config()
    except:
        print("Warning: Could not load kubeconfig")

v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()

def get_deployment_status(namespace=None):
    """Get status of all deployments"""
    try:
        if namespace:
            deployments = v1.list_namespaced_deployment(namespace)
        else:
            deployments = v1.list_deployment_for_all_namespaces()
        
        status_list = []
        for deployment in deployments.items:
            metadata = deployment.metadata
            spec = deployment.spec
            status = deployment.status
            
            # Get pods for this deployment
            selector = ','.join([f"{k}={v}" for k, v in spec.selector.match_labels.items()])
            try:
                if namespace:
                    pods = core_v1.list_namespaced_pod(namespace, label_selector=selector)
                else:
                    pods = core_v1.list_pod_for_all_namespaces(label_selector=selector)
            except:
                pods = None
            
            pod_statuses = []
            if pods:
                for pod in pods.items:
                    pod_status = "Unknown"
                    if pod.status.phase:
                        pod_status = pod.status.phase
                    
                    pod_statuses.append({
                        'name': pod.metadata.name,
                        'status': pod_status,
                        'ready': any(c.ready for c in pod.status.container_statuses) if pod.status.container_statuses else False,
                        'restarts': sum(c.restart_count for c in pod.status.container_statuses) if pod.status.container_statuses else 0,
                        'node': pod.spec.node_name,
                    })
            
            # Determine overall status
            overall_status = "Unknown"
            if status.ready_replicas == spec.replicas and status.replicas == spec.replicas:
                overall_status = "Healthy"
            elif status.replicas < spec.replicas:
                overall_status = "Degraded"
            elif status.unavailable_replicas:
                overall_status = "Unavailable"
            
            # Get update/rollout status
            conditions = status.conditions or []
            update_status = "Up to date"
            for condition in conditions:
                if condition.type == "Progressing":
                    if condition.status == "True":
                        update_status = "Updating"
                    else:
                        update_status = "Update Failed"
                elif condition.type == "Available" and condition.status == "False":
                    update_status = "Unavailable"
            
            # Get image versions
            images = [c.image for c in spec.template.spec.containers]
            
            status_list.append({
                'name': metadata.name,
                'namespace': metadata.namespace,
                'replicas': {
                    'desired': spec.replicas,
                    'ready': status.ready_replicas or 0,
                    'available': status.available_replicas or 0,
                    'unavailable': status.unavailable_replicas or 0,
                },
                'status': overall_status,
                'update_status': update_status,
                'images': images,
                'pods': pod_statuses,
                'created': metadata.creation_timestamp.isoformat() if metadata.creation_timestamp else None,
                'updated': status.updated_replicas or 0,
            })
        
        return status_list
    except ApiException as e:
        print(f"Error fetching deployments: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def get_service_status(namespace=None):
    """Get status of all services"""
    try:
        if namespace:
            services = core_v1.list_namespaced_service(namespace)
        else:
            services = core_v1.list_service_for_all_namespaces()
        
        service_list = []
        for service in services.items:
            metadata = service.metadata
            spec = service.spec
            
            # Get endpoints
            try:
                if namespace:
                    endpoints = core_v1.read_namespaced_endpoints(metadata.name, namespace)
                else:
                    endpoints = core_v1.read_namespaced_endpoints(metadata.name, metadata.namespace)
                
                endpoint_count = len(endpoints.subsets[0].addresses) if endpoints.subsets else 0
            except:
                endpoint_count = 0
            
            service_status = "Available" if endpoint_count > 0 else "No Endpoints"
            
            service_list.append({
                'name': metadata.name,
                'namespace': metadata.namespace,
                'type': spec.type,
                'ports': [f"{p.port}/{p.protocol}" for p in spec.ports or []],
                'endpoints': endpoint_count,
                'status': service_status,
                'cluster_ip': spec.cluster_ip,
                'external_ip': spec.load_balancer.ingress[0].hostname if spec.load_balancer and spec.load_balancer.ingress else None,
            })
        
        return service_list
    except ApiException as e:
        print(f"Error fetching services: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

@app.route('/')
def index():
    """Main status page"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint for status data"""
    namespace = request.args.get('namespace', None)
    
    deployments = get_deployment_status(namespace)
    services = get_service_status(namespace)
    
    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'deployments': deployments,
        'services': services,
        'summary': {
            'total_deployments': len(deployments),
            'healthy_deployments': len([d for d in deployments if d['status'] == 'Healthy']),
            'degraded_deployments': len([d for d in deployments if d['status'] == 'Degraded']),
            'total_services': len(services),
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

