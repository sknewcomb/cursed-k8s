#!/usr/bin/env python3
"""
Test module for header-leak challenge
"""

import requests
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import TestResult, check_service_health, extract_flag_from_response, validate_flag_format, wait_for_service, check_namespace_exists, check_service_exists


def test_header_leak_challenge(base_url: Optional[str] = None, verbose: bool = False) -> TestResult:
    """Test the header-leak challenge vulnerability"""
    result = TestResult("Header Leak Challenge")
    
    # Determine URL
    if not base_url:
        if verbose:
            print("  Checking if namespace exists...")
        if not check_namespace_exists('header-leak'):
            result.failure("Namespace 'header-leak' does not exist. Deploy the challenge first using: kubectl apply -f challenges/beginner/header-leak/")
            return result
        
        if verbose:
            print("  Checking if service exists...")
        if not check_service_exists('header-leak', 'header-leak'):
            result.failure("Service 'header-leak' does not exist in namespace 'header-leak'. Deploy the challenge first.")
            return result
        
        if verbose:
            print("  Waiting for service NodePort...")
        port = wait_for_service('header-leak', 'header-leak')
        if not port:
            result.failure("Could not get service NodePort. The service may not be ready yet. Try: kubectl get svc -n header-leak")
            result.details['namespace_exists'] = check_namespace_exists('header-leak')
            result.details['service_exists'] = check_service_exists('header-leak', 'header-leak')
            return result
        base_url = f"http://localhost:{port}"
    
    # Check service health with retries (pods might still be starting)
    if verbose:
        print("  Checking service health...")
    is_healthy, health_error = check_service_health(base_url, timeout=10, retries=5, retry_delay=3)
    if not is_healthy:
        error_msg = f"Service not healthy at {base_url} after multiple attempts."
        if health_error:
            error_msg += f" Error: {health_error}"
        result.failure(error_msg)
        result.details['base_url'] = base_url
        result.details['health_error'] = health_error
        result.details['suggestion'] = "Try checking pod status: kubectl get pods -n header-leak && kubectl logs -n header-leak -l app=header-leak"
        return result
    
    try:
        # Make a request to any endpoint
        response = requests.get(f"{base_url}/api/status", timeout=10)
        
        if response.status_code != 200:
            result.failure(f"Unexpected status code: {response.status_code}")
            return result
        
        # Check for flag in headers
        flag = None
        for header_name, header_value in response.headers.items():
            if 'x-flag' in header_name.lower():
                flag = header_value
                break
        
        if not flag:
            result.failure("Flag not found in response headers")
            result.details['headers'] = dict(response.headers)
            return result
        
        # Validate flag format
        if not validate_flag_format(flag):
            result.failure(f"Invalid flag format: {flag}")
            return result
        
        result.success(f"Flag found in {header_name} header", flag)
        result.details['header_name'] = header_name
        result.details['all_headers'] = dict(response.headers)
        return result
        
    except Exception as e:
        result.failure(f"Error during test: {str(e)}")
        return result


if __name__ == '__main__':
    # Allow direct execution for testing
    result = test_header_leak_challenge()
    print(result)

