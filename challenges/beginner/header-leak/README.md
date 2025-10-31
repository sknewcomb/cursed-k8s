# Header Information Disclosure Challenge

## Challenge Description

You've discovered an administrative portal for a company's internal system. The application claims to use "advanced security headers for protection," but something seems off. Your mission is to intercept the HTTP traffic and find the hidden flag!

**Difficulty:** Beginner  
**Category:** Web Security & Information Disclosure  
**Burp Suite Compatible:** Yes

## Learning Objectives

- Understand how HTTP headers can leak sensitive information
- Learn to use Burp Suite (or browser dev tools) to examine HTTP headers
- Recognize common security misconfigurations in web applications
- Practice identifying information disclosure vulnerabilities

## Challenge Setup

The application is deployed in the `header-leak` namespace. It's an admin portal that exposes various endpoints.

**Access the application:**
- Web Interface: `http://localhost:30101`
- Or use port-forward: `kubectl port-forward -n header-leak svc/header-leak 8080:8080`

## Your Mission

Find the flag hidden somewhere in the HTTP responses. The flag format is: `FLAG{...}`

**Tip:** Use Burp Suite to intercept and examine HTTP responses, or use your browser's developer tools to inspect the response headers.

## Hints

1. 🔍 HTTP headers are sent with every response - check them carefully!
2. 🛠️ Use Burp Suite's Proxy to intercept responses and examine headers
3. 📋 Custom headers starting with `X-` often contain debug or diagnostic information
4. 🌐 You can also use browser developer tools (F12) to inspect response headers

## What to Look For

- Use Burp Suite Proxy to intercept HTTP responses
- Check all response headers, especially custom ones (X-*)
- Try accessing different endpoints (`/`, `/api/status`, `/api/users`)
- Look for headers that might contain sensitive information

## Getting Started

If you haven't deployed the challenge yet:

```bash
kubectl apply -f challenges/beginner/header-leak/
```

Or use the deployment script:

```bash
cd challenges/beginner/header-leak
./deploy.sh
```

## Using Burp Suite

1. Configure your browser to use Burp Suite as a proxy (usually `127.0.0.1:8080`)
2. Enable interception in Burp Suite Proxy
3. Visit `http://localhost:30101` in your browser
4. Examine the intercepted response in Burp Suite
5. Look at the Response headers section
6. Try accessing different endpoints and check their headers

## Verification

Once you find the flag, verify it matches the format `FLAG{...}`

## Solution Path

<details>
<summary>Click to reveal the solution path</summary>

1. Access the web application at `http://localhost:30101`
2. Use Burp Suite Proxy to intercept HTTP responses (or use browser dev tools)
3. Make a request to any endpoint (e.g., `/` or `/api/status`)
4. Examine the Response headers in Burp Suite
5. Look for the `X-Flag` header - it contains the flag!
6. The flag is: `FLAG{headers_are_public_metadata}`

**Alternative:** You can also use browser developer tools:
- Press F12 to open DevTools
- Go to Network tab
- Make a request to the site
- Click on the request and check the Response Headers section
- Look for `X-Flag` header

</details>

## Security Lesson

This challenge demonstrates a critical security mistake:

- **HTTP headers are public metadata** - They're sent with every HTTP response and can be read by anyone who intercepts the traffic
- **Never expose sensitive information in headers** - Headers like `X-Flag`, `X-Debug-Token`, or `X-Internal-*` can leak secrets
- **Disable debug headers in production** - Headers like `X-Powered-By` or `X-Server-Version` can aid attackers
- **Use security headers properly** - Headers like `X-Frame-Options`, `Content-Security-Policy` are for protection, not for storing secrets
- **Always audit what headers your application sends** - Use tools like Burp Suite to review all headers in production

## Burp Suite Tips

- Use Proxy → Intercept to view requests/responses in real-time
- The Response tab shows all headers sent by the server
- Custom headers are often shown at the bottom of the headers list
- You can right-click on requests to "Send to Repeater" for further testing

