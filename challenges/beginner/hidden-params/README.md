# Hidden Parameters / Authentication Bypass Challenge

## Challenge Description

You've discovered a secure admin panel that requires authentication. The application claims to be secure, but there might be hidden ways to bypass the authentication mechanism. Your mission is to find undocumented parameters or endpoints that grant you admin access and reveal the hidden flag!

**Difficulty:** Beginner  
**Category:** Web Security & Authentication Bypass  
**Burp Suite Compatible:** Yes

## Learning Objectives

- Understand how hidden parameters can be used to bypass security controls
- Learn to discover undocumented API parameters using Burp Suite
- Practice modifying HTTP requests to exploit authentication bypasses
- Recognize common security mistakes in authentication implementations

## Challenge Setup

The application is deployed in the `hidden-params` namespace. It's an admin panel with a login form.

**Access the application:**
- Web Interface: `http://localhost:30103`
- Or use port-forward: `kubectl port-forward -n hidden-params svc/hidden-params 8080:8080`

## Your Mission

Find a way to bypass authentication and access the admin endpoint to retrieve the flag. The flag format is: `FLAG{...}`

**Tip:** Use Burp Suite to intercept and modify HTTP requests. Look for hidden form fields, query parameters, or headers.

## Hints

1. 🔍 Try modifying form data or query parameters that aren't visible on the page
2. 🛠️ Use Burp Suite to intercept POST requests and add additional parameters
3. 📋 Check query strings, form data, and HTTP headers for hidden values
4. 🌐 Some endpoints might accept parameters in multiple places (form, query, headers)

## What to Look For

- Use Burp Suite Proxy to intercept login requests
- Try adding hidden parameters to form submissions
- Check query string parameters (e.g., `?debug=true`)
- Modify HTTP headers in requests
- Look for alternative authentication mechanisms

## Getting Started

If you haven't deployed the challenge yet:

```bash
kubectl apply -f challenges/beginner/hidden-params/
```

Or use the deployment script:

```bash
cd challenges/beginner/hidden-params
./deploy.sh
```

## Using Burp Suite

1. Configure your browser to use Burp Suite as a proxy
2. Visit `http://localhost:30103` in your browser
3. Intercept a login request (try with wrong credentials)
4. Modify the intercepted request in Burp Suite:
   - Add hidden parameters to form data
   - Try query string parameters
   - Modify HTTP headers
5. Forward the modified request and check the response

## Verification

Once you find the flag, verify it matches the format `FLAG{...}`

## Solution Path

<details>
<summary>Click to reveal the solution path</summary>

### Method 1: Hidden Form Parameter

1. Access the web application at `http://localhost:30103`
2. Use Burp Suite Proxy to intercept a POST request to `/api/login`
3. Modify the form data to include `admin=true`:
   ```
   username=test&password=test&admin=true
   ```
4. Forward the request - you'll get admin access and the flag!

### Method 2: Query String Parameter

1. Try accessing `/api/login?debug=true` with a POST request
2. The response reveals hints about the `admin` parameter

### Method 3: Direct Admin Endpoint

1. Use Burp Suite to make a request to `/api/admin`
2. Try adding `?token=admin-token-secret` to the URL
3. Or add header: `X-Admin-Bypass: true`
4. The flag is: `FLAG{hidden_params_bypass_auth}`

</details>

## Security Lesson

This challenge demonstrates critical authentication vulnerabilities:

- **Never trust client-side validation** - Hidden parameters can bypass security checks
- **Document all API parameters** - Undocumented parameters are security risks
- **Use proper authentication** - Don't rely on hidden "admin" flags or bypass mechanisms
- **Validate all inputs** - Check all parameters, not just visible ones
- **Use strong authentication** - Implement proper token-based auth instead of simple flags
- **Audit your code** - Review code for hidden features or debug modes that bypass security

## Common Hidden Parameter Attacks

Attackers might look for:
- Hidden form fields (`<input type="hidden">`)
- Undocumented query parameters (`?debug=true`, `?admin=1`)
- HTTP headers (`X-Admin-Bypass`, `X-Debug-Mode`)
- Alternative parameter names (trying variations)
- Multiple parameter locations (form, query, header, JSON body)

## Burp Suite Tips

- Use Proxy → Intercept to modify requests in real-time
- Use Intruder to fuzz parameters with common values
- Use Repeater to test multiple variations quickly
- Check both the Params and Headers tabs
- Try adding parameters to different locations (body, query, headers)

