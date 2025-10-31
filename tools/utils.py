#!/usr/bin/env python3
"""
Shared utilities for challenge testing
"""

import subprocess
import time
import requests
from typing import Optional, Dict, Any
import json


def check_kubectl() -> bool:
    """Check if kubectl is available and cluster is accessible"""
    try:
        result = subprocess.run(
            ['kubectl', 'get', 'nodes'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def wait_for_pod_ready(namespace: str, pod_name: str, timeout: int = 120) -> bool:
    """Wait for a pod to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'pod', pod_name, '-n', namespace, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                status = data.get('status', {})
                conditions = status.get('conditions', [])
                for condition in conditions:
                    if condition.get('type') == 'Ready' and condition.get('status') == 'True':
                        return True
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return False


def check_service_exists(namespace: str, service_name: str) -> bool:
    """Check if a service exists in the namespace"""
    try:
        result = subprocess.run(
            ['kubectl', 'get', 'svc', service_name, '-n', namespace],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def check_namespace_exists(namespace: str) -> bool:
    """Check if a namespace exists"""
    try:
        result = subprocess.run(
            ['kubectl', 'get', 'namespace', namespace],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def wait_for_service(namespace: str, service_name: str, timeout: int = 60) -> Optional[str]:
    """Get the NodePort for a service"""
    # First check if namespace exists
    if not check_namespace_exists(namespace):
        return None
    
    # Then check if service exists
    if not check_service_exists(namespace, service_name):
        return None
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'svc', service_name, '-n', namespace, '-o', 'jsonpath={.spec.ports[0].nodePort}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                port = result.stdout.strip()
                if port and port != '<no value>':
                    return port
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return None


def check_service_health(url: str, timeout: int = 10, retries: int = 3, retry_delay: int = 2) -> tuple:
    """Check if a service is responding with retries. Returns (is_healthy, error_message)"""
    last_error = None
    
    for attempt in range(retries):
        # First try to connect to the base URL to check if port is open
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=False)
            # Any response means the service is up (even 404 is OK - means service is running)
            if response.status_code in [200, 301, 302, 404, 500]:
                return (True, None)
        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection refused - port not open or service not listening: {str(e)}"
            if attempt < retries - 1:
                time.sleep(retry_delay)
            continue
        except requests.exceptions.Timeout as e:
            last_error = f"Connection timeout: {str(e)}"
            if attempt < retries - 1:
                time.sleep(retry_delay)
            continue
        except Exception as e:
            last_error = f"Connection error: {str(e)}"
            if attempt < retries - 1:
                time.sleep(retry_delay)
            continue
        
        # Try health endpoint specifically
        try:
            response = requests.get(f"{url}/health", timeout=timeout)
            if response.status_code == 200:
                return (True, None)
        except requests.exceptions.ConnectionError as e:
            last_error = f"Health endpoint connection refused: {str(e)}"
            if attempt < retries - 1:
                time.sleep(retry_delay)
            continue
        except requests.exceptions.Timeout as e:
            last_error = f"Health endpoint timeout: {str(e)}"
            if attempt < retries - 1:
                time.sleep(retry_delay)
            continue
        except Exception as e:
            last_error = f"Health endpoint error: {str(e)}"
            if attempt < retries - 1:
                time.sleep(retry_delay)
            continue
        
        if attempt < retries - 1:
            time.sleep(retry_delay)
    
    return (False, last_error or "Unknown error")


def wait_for_pod_ready_in_namespace(namespace: str, label_selector: str = None, timeout: int = 120) -> bool:
    """Wait for pods to be ready in a namespace"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            cmd = ['kubectl', 'get', 'pods', '-n', namespace, '-o', 'json']
            if label_selector:
                cmd.extend(['-l', label_selector])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                pods = data.get('items', [])
                
                if not pods:
                    time.sleep(2)
                    continue
                
                all_ready = True
                for pod in pods:
                    status = pod.get('status', {})
                    phase = status.get('phase', '')
                    conditions = status.get('conditions', [])
                    
                    # Check if pod is running and ready
                    ready = False
                    for condition in conditions:
                        if condition.get('type') == 'Ready' and condition.get('status') == 'True':
                            ready = True
                            break
                    
                    if phase != 'Running' or not ready:
                        all_ready = False
                        break
                
                if all_ready:
                    return True
            
            time.sleep(2)
        except Exception:
            time.sleep(2)
    
    return False


def extract_flag_from_response(response: requests.Response) -> Optional[str]:
    """Extract flag from various response formats"""
    # Try JSON response
    try:
        data = response.json()
        # Check common flag locations
        if isinstance(data, dict):
            # Direct flag field
            if 'flag' in data:
                flag = data['flag']
                if isinstance(flag, str) and flag.startswith('FLAG{'):
                    return flag
            # Nested in content field (for file disclosure)
            if 'content' in data and isinstance(data['content'], str):
                content = data['content']
                # Try to find FLAG{...} in content
                import re
                match = re.search(r'FLAG\{[^}]+\}', content)
                if match:
                    return match.group(0)
    except Exception:
        pass
    
    # Try headers
    for header_name, header_value in response.headers.items():
        if 'flag' in header_name.lower() and header_value.startswith('FLAG{'):
            return header_value
        if 'x-flag' in header_name.lower() and header_value.startswith('FLAG{'):
            return header_value
    
    # Try text content
    try:
        text = response.text
        import re
        match = re.search(r'FLAG\{[^}]+\}', text)
        if match:
            return match.group(0)
    except Exception:
        pass
    
    return None


def validate_flag_format(flag: str) -> bool:
    """Validate that flag matches expected format"""
    if not flag or not isinstance(flag, str):
        return False
    return flag.startswith('FLAG{') and flag.endswith('}') and len(flag) > 6


class TestResult:
    """Container for test results"""
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.flag = None
        self.details: Dict[str, Any] = {}
    
    def success(self, message: str = "", flag: Optional[str] = None):
        self.passed = True
        self.message = message
        self.flag = flag
    
    def failure(self, message: str):
        self.passed = False
        self.message = message
    
    def __str__(self):
        status = "✓ PASS" if self.passed else "✗ FAIL"
        result = f"{status} - {self.name}"
        if self.message:
            result += f": {self.message}"
        if self.flag:
            result += f" [Flag: {self.flag}]"
        return result

