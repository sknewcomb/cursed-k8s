#!/bin/bash
# Deploy all beginner challenges

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHALLENGES_DIR="$(cd "$SCRIPT_DIR/../challenges/beginner" && pwd)"

echo "========================================="
echo "Deploying All Beginner Challenges"
echo "========================================="
echo ""

# List of challenges to deploy
CHALLENGES=(
    "secret-leak"
    "header-leak"
    "file-disclosure"
    "hidden-params"
)

for challenge in "${CHALLENGES[@]}"; do
    challenge_dir="$CHALLENGES_DIR/$challenge"
    
    if [ ! -d "$challenge_dir" ]; then
        echo "⚠ Warning: Challenge directory not found: $challenge_dir"
        continue
    fi
    
    echo "Deploying: $challenge"
    echo "----------------------------------------"
    
    if [ -f "$challenge_dir/deploy.sh" ]; then
        # Use challenge's own deploy script
        cd "$challenge_dir"
        bash deploy.sh
        cd - > /dev/null
    else
        # Deploy using kubectl
        kubectl apply -f "$challenge_dir/"
        
        # Wait for deployment
        namespace=$(basename "$challenge")
        kubectl wait --for=condition=available --timeout=120s deployment/$challenge -n $namespace || true
    fi
    
    echo ""
done

echo "========================================="
echo "All challenges deployed!"
echo "========================================="
echo ""
echo "Challenge URLs:"
kubectl get svc -A -o wide | grep -E "(secret-leak|header-leak|file-disclosure|hidden-params)" | awk '{printf "  %s/%s - http://localhost:%s\n", $1, $2, $5}' | sed 's|http://localhost:||' | sed 's|/TCP||' | awk '{print "  http://localhost:" $NF}'

echo ""
echo "To test challenges, run:"
echo "  python3 tools/test-challenges.py"

