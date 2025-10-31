#!/usr/bin/env python3
"""
Main test runner for CTF challenges
Tests all challenges to verify vulnerabilities work correctly
"""

import sys
import argparse
import time
from pathlib import Path

# Try to import tqdm for progress bars, fallback to simple progress if not available
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    # Simple progress bar fallback
    class tqdm:
        def __init__(self, iterable=None, total=None, desc=None, unit=None, **kwargs):
            self.iterable = iterable or range(total or 1)
            self.total = total or len(self.iterable) if hasattr(self.iterable, '__len__') else 1
            self.desc = desc or ""
            self.current = 0
            self.start_time = time.time()
        
        def __iter__(self):
            return iter(self.iterable)
        
        def update(self, n=1):
            self.current += n
            elapsed = time.time() - self.start_time
            percent = (self.current / self.total) * 100 if self.total > 0 else 0
            bar_length = 30
            filled = int(bar_length * self.current / self.total) if self.total > 0 else 0
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r{self.desc} [{bar}] {percent:.1f}% ({self.current}/{self.total})", end='', flush=True)
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            print()  # New line after progress bar
        
        def set_description(self, desc):
            self.desc = desc
        
        def close(self):
            """Close method for compatibility"""
            print()  # New line after progress bar

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import check_kubectl, TestResult, check_namespace_exists
from challenge_testers import header_leak, file_disclosure, hidden_params
import subprocess


# Challenge registry
CHALLENGES = {
    'header-leak': {
        'name': 'Header Information Disclosure',
        'namespace': 'header-leak',
        'tester': header_leak.test_header_leak_challenge,
        'path': 'challenges/beginner/header-leak',
    },
    'file-disclosure': {
        'name': 'File Disclosure / Path Traversal',
        'namespace': 'file-disclosure',
        'tester': file_disclosure.test_file_disclosure_challenge,
        'path': 'challenges/beginner/file-disclosure',
    },
    'hidden-params': {
        'name': 'Hidden Parameters / Auth Bypass',
        'namespace': 'hidden-params',
        'tester': hidden_params.test_hidden_params_challenge,
        'path': 'challenges/beginner/hidden-params',
    },
}


def deploy_challenge(challenge_id: str, verbose: bool = False) -> bool:
    """Deploy a challenge using its deploy script or kubectl"""
    if challenge_id not in CHALLENGES:
        return False
    
    challenge = CHALLENGES[challenge_id]
    challenge_path = Path(__file__).parent.parent / challenge['path']
    
    if not challenge_path.exists():
        if verbose:
            print(f"  ✗ Challenge directory not found: {challenge_path}")
        return False
    
    deploy_script = challenge_path / 'deploy.sh'
    
    try:
        if deploy_script.exists() and deploy_script.is_file():
            # Use challenge's deploy script
            if verbose:
                print(f"  Running deploy script: {deploy_script}")
            result = subprocess.run(
                ['bash', str(deploy_script)],
                cwd=str(challenge_path),
                capture_output=not verbose,
                timeout=180,
                check=False
            )
            if result.returncode != 0:
                if verbose:
                    print(f"  ✗ Deploy script failed with exit code {result.returncode}")
                return False
        else:
            # Fallback: use kubectl apply
            if verbose:
                print(f"  Deploying with kubectl: {challenge_path}")
            result = subprocess.run(
                ['kubectl', 'apply', '-f', str(challenge_path)],
                capture_output=not verbose,
                timeout=120,
                check=False
            )
            if result.returncode != 0:
                if verbose:
                    print(f"  ✗ kubectl apply failed")
                return False
            
            # Wait for deployment
            namespace = challenge['namespace']
            deployment_name = challenge_id.replace('-', '-')  # Use challenge_id as deployment name
            if verbose:
                print(f"  Waiting for deployment to be ready...")
            wait_result = subprocess.run(
                ['kubectl', 'wait', '--for=condition=available', '--timeout=120s', 
                 f'deployment/{challenge_id}', '-n', namespace],
                capture_output=not verbose,
                timeout=125,
                check=False
            )
            if wait_result.returncode != 0 and verbose:
                print(f"  ⚠ Deployment may still be starting (this is okay)")
        
        return True
    except subprocess.TimeoutExpired:
        if verbose:
            print(f"  ✗ Deployment timed out")
        return False
    except Exception as e:
        if verbose:
            print(f"  ✗ Deployment error: {str(e)}")
        return False


def test_challenge(challenge_id: str, verbose: bool = False, progress_bar=None) -> TestResult:
    """Test a specific challenge"""
    if challenge_id not in CHALLENGES:
        result = TestResult(challenge_id)
        result.failure(f"Unknown challenge: {challenge_id}")
        return result
    
    challenge = CHALLENGES[challenge_id]
    
    if not verbose:
        # Simple output when not verbose
        if progress_bar:
            progress_bar.set_description(f"Testing {challenge['name']}")
        else:
            print(f"\nTesting: {challenge['name']}...", end='', flush=True)
    else:
        print(f"\n{'='*60}")
        print(f"Testing: {challenge['name']}")
        print(f"{'='*60}")
        print(f"Challenge ID: {challenge_id}")
        print(f"Namespace: {challenge['namespace']}")
    
    if verbose:
        print("Step 1: Checking service availability...")
    
    start_time = time.time()
    
    # Run the test - pass verbose flag to tester
    tester_func = challenge['tester']
    # Check if tester function accepts verbose parameter
    import inspect
    sig = inspect.signature(tester_func)
    if 'verbose' in sig.parameters:
        result = tester_func(verbose=verbose)
    else:
        result = tester_func()
    
    elapsed = time.time() - start_time
    
    if not verbose:
        if progress_bar:
            progress_bar.update(1)
        else:
            status = "✓" if result.passed else "✗"
            print(f" {status} ({elapsed:.2f}s)")
    else:
        print(f"\nTest completed in {elapsed:.2f} seconds")
        if result.passed:
            print("✓ Test PASSED")
            if result.flag:
                print(f"  Flag extracted: {result.flag}")
            if result.details:
                print("  Details:")
                for key, value in result.details.items():
                    if key != 'traceback':
                        print(f"    - {key}: {value}")
        else:
            print("✗ Test FAILED")
            print(f"  Error: {result.message}")
            if result.details:
                print("  Details:")
                for key, value in result.details.items():
                    if key == 'traceback' and verbose:
                        print(f"    {key}:")
                        print(f"      {value}")
                    elif key != 'traceback':
                        print(f"    - {key}: {value}")
    
    return result


def test_all_challenges(verbose: bool = False, auto_deploy: bool = False) -> list[TestResult]:
    """Test all challenges"""
    results = []
    
    print("="*60)
    print("CTF Challenge Testing Toolkit")
    print("="*60)
    
    # Check prerequisites
    if verbose:
        print("\n[1/3] Checking prerequisites...")
    else:
        print("\nChecking prerequisites...", end=' ', flush=True)
    
    if not check_kubectl():
        print("\n✗ ERROR: kubectl not available or cluster not accessible")
        print("  Make sure kubectl is configured and k3s cluster is running")
        sys.exit(1)
    
    if verbose:
        print("✓ kubectl is available and cluster is accessible")
    else:
        print("✓")
    
    # Pre-check: Verify challenges are deployed (or deploy them)
    if verbose:
        print("\n[2/3] Checking if challenges are deployed...")
    else:
        print("Checking deployments...", end=' ', flush=True)
    
    missing_challenges = []
    for challenge_id, challenge_info in CHALLENGES.items():
        namespace = challenge_info['namespace']
        if not check_namespace_exists(namespace):
            missing_challenges.append(challenge_id)
    
    if missing_challenges:
        if auto_deploy:
            if verbose:
                print(f"\n  Auto-deploying {len(missing_challenges)} missing challenge(s)...")
            else:
                print(f"\nAuto-deploying {len(missing_challenges)} challenge(s)...", end=' ', flush=True)
            
            deployed = 0
            for ch_id in missing_challenges:
                if verbose:
                    print(f"\n  Deploying: {ch_id}...")
                if deploy_challenge(ch_id, verbose):
                    deployed += 1
                    if verbose:
                        print(f"  ✓ {ch_id} deployed successfully")
                else:
                    if verbose:
                        print(f"  ✗ Failed to deploy {ch_id}")
            
            if verbose:
                print(f"\n  Deployed {deployed}/{len(missing_challenges)} challenge(s)")
            else:
                status = "✓" if deployed == len(missing_challenges) else "⚠"
                print(f"{status} ({deployed}/{len(missing_challenges)})")
            
            # Wait a bit for pods to be fully ready (deployment ready != pods ready for traffic)
            if verbose:
                print(f"\n  Waiting for pods to be ready for traffic...")
            else:
                print("Waiting for pods...", end=' ', flush=True)
            
            time.sleep(5)  # Give pods a moment to start serving
            
            # Re-check after deployment and update missing list
            still_missing = [ch_id for ch_id in missing_challenges 
                            if not check_namespace_exists(CHALLENGES[ch_id]['namespace'])]
            if still_missing:
                if verbose:
                    print(f"\n  ⚠ Warning: {len(still_missing)} challenge(s) failed to deploy:")
                    for ch_id in still_missing:
                        print(f"    - {ch_id}")
            else:
                if not verbose:
                    print("✓")
            # Update missing_challenges to only include those that still don't exist
            missing_challenges = still_missing
        else:
            if verbose:
                print("⚠ Warning: Some challenges are not deployed:")
                for ch_id in missing_challenges:
                    print(f"  - {ch_id} (namespace: {CHALLENGES[ch_id]['namespace']})")
                print("\n  Deploy missing challenges using:")
                print("    ./tools/deploy-all.sh")
                print("  Or run tests with --deploy to auto-deploy:")
                print("    python3 tools/test-challenges.py --deploy")
                print("\n  Continuing with deployed challenges...")
            else:
                print(f"⚠ ({len(missing_challenges)} not deployed)")
    else:
        if verbose:
            print("✓ All challenges appear to be deployed")
        else:
            print("✓")
    
    # Determine which challenges to test (only deployed ones)
    challenge_ids_to_test = [ch_id for ch_id in CHALLENGES.keys() 
                            if ch_id not in missing_challenges]
    
    if not challenge_ids_to_test:
        print("\n✗ No challenges available to test")
        if not auto_deploy:
            print("  Run with --deploy to automatically deploy challenges")
        return []
    
    # Test each challenge
    total_challenges = len(challenge_ids_to_test)
    
    if verbose:
        print(f"\n[3/3] Testing {total_challenges} challenge(s)...")
        print()
    else:
        print(f"\nTesting {total_challenges} challenge(s)...")
    
    # Create progress bar if not verbose
    if not verbose:
        progress_bar = tqdm(
            total=total_challenges,
            desc="Progress",
            unit="challenge",
            bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}'
        )
    else:
        progress_bar = None
    
    try:
        for idx, challenge_id in enumerate(challenge_ids_to_test, 1):
            if verbose:
                print(f"\n[{idx}/{total_challenges}]")
            
            result = test_challenge(challenge_id, verbose, progress_bar)
            results.append(result)
            
            # Small delay for readability in verbose mode
            if verbose and idx < total_challenges:
                time.sleep(0.5)
    finally:
        if progress_bar and not verbose:
            # tqdm doesn't have a close() method - it handles cleanup automatically
            # Just ensure we finish any remaining output
            pass
    
    return results


def print_summary(results: list[TestResult], verbose: bool = False):
    """Print test summary"""
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    
    if verbose:
        print("\nDetailed Results:")
        print("-" * 60)
    
    for result in results:
        if verbose:
            print(f"\n{result.name}:")
            print(f"  Status: {'✓ PASSED' if result.passed else '✗ FAILED'}")
            if result.message:
                print(f"  Message: {result.message}")
            if result.flag:
                print(f"  Flag: {result.flag}")
            if result.details:
                print(f"  Details: {len(result.details)} item(s)")
        else:
            print(result)
    
    print("\n" + "-"*60)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    
    if passed == len(results):
        print("Success Rate: 100%")
    else:
        success_rate = (passed / len(results)) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    print("-"*60)
    
    if failed == 0:
        print("\n✓ All challenges are working correctly!")
        if verbose:
            print("All vulnerabilities were successfully exploited and flags extracted.")
        return 0
    else:
        print(f"\n✗ {failed} challenge(s) failed")
        if verbose:
            print("\nFailed challenges may need:")
            print("  - Deployment verification (check: kubectl get pods -A)")
            print("  - Service accessibility (check: kubectl get svc -A)")
            print("  - Network connectivity")
            print("  - Challenge-specific configuration")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Test CTF challenges to verify vulnerabilities work correctly'
    )
    parser.add_argument(
        '--challenge',
        choices=list(CHALLENGES.keys()),
        help='Test a specific challenge (default: test all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show verbose output'
    )
    parser.add_argument(
        '--deploy',
        action='store_true',
        help='Automatically deploy challenges before testing if they are not already deployed'
    )
    
    args = parser.parse_args()
    
    if args.challenge:
        # Test single challenge
        print("="*60)
        print("CTF Challenge Testing Toolkit")
        print("="*60)
        result = test_challenge(args.challenge, args.verbose, None)
        if not args.verbose:
            print(f"\n{result}")
        return 0 if result.passed else 1
    else:
        # Test all challenges
        results = test_all_challenges(args.verbose, args.deploy)
        return print_summary(results, args.verbose)


if __name__ == '__main__':
    sys.exit(main())

