# CTF Challenge Testing Toolkit

This directory contains tools for testing and validating CTF challenges.

## Structure

```
tools/
├── README.md                    # This file
├── test-challenges.py          # Main test runner for all challenges
├── challenge_testers/          # Individual test modules for each challenge
│   ├── __init__.py
│   ├── header_leak.py
│   ├── file_disclosure.py
│   └── hidden_params.py
├── utils.py                    # Shared utilities
└── deploy-all.sh               # Deploy all challenges script
```

## Usage

### Test All Challenges

```bash
# Quick test with progress bar (only tests already-deployed challenges)
python3 tools/test-challenges.py

# Auto-deploy missing challenges before testing
python3 tools/test-challenges.py --deploy

# Verbose output with detailed information
python3 tools/test-challenges.py --verbose

# Auto-deploy and verbose
python3 tools/test-challenges.py --deploy --verbose
```

### Test Specific Challenge

```bash
# Quick test
python3 tools/test-challenges.py --challenge header-leak

# Verbose output
python3 tools/test-challenges.py --challenge header-leak --verbose
```

### Deploy All Challenges

```bash
./tools/deploy-all.sh
```

## Requirements

- Python 3.7+
- Required: `requests` library: `pip install requests`
- Optional: `tqdm` library for better progress bars: `pip install tqdm`
  - If not installed, a simple progress indicator will be used
- kubectl configured and cluster accessible

Install all requirements:
```bash
pip install -r tools/requirements.txt
```

## Test Structure

Each challenge tester validates:
1. Challenge deployment status
2. Application accessibility
3. Vulnerability exploitation
4. Flag extraction
5. Expected flag format

