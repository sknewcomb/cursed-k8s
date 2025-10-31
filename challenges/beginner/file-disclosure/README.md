# File Disclosure / Path Traversal Challenge

## Challenge Description

You've discovered a document viewer application that allows users to read files from the server. The application claims to only allow access to "public" documents, but there might be a way to access restricted files. Your mission is to exploit a path traversal vulnerability to find the hidden flag!

**Difficulty:** Beginner  
**Category:** Web Security & Path Traversal  
**Burp Suite Compatible:** Yes

## Learning Objectives

- Understand path traversal (directory traversal) vulnerabilities
- Learn to exploit insufficient input validation in file access endpoints
- Practice using Burp Suite to modify HTTP request parameters
- Recognize common security mistakes in file access controls

## Challenge Setup

The application is deployed in the `file-disclosure` namespace. It's a document viewer that allows reading files via an API endpoint.

**Access the application:**
- Web Interface: `http://localhost:30102`
- Or use port-forward: `kubectl port-forward -n file-disclosure svc/file-disclosure 8080:8080`

## Your Mission

Exploit the path traversal vulnerability to read a file that should be private. The flag format is: `FLAG{...}`

**Tip:** Use Burp Suite to modify the file path parameter in HTTP requests to include path traversal sequences.

## Hints

1. 🔍 The application checks if a path starts with "public/" but doesn't prevent path traversal
2. 🛠️ Use Burp Suite's Proxy or Repeater to modify the `file` parameter
3. 📋 Try using `../` sequences to escape from the `public/` directory
4. 🌐 The flag is in a file called `flag.txt` in the `private/` directory

## What to Look For

- Use Burp Suite Proxy to intercept requests to `/api/read`
- Modify the `file` parameter to include path traversal sequences
- Try paths like `public/../private/flag.txt` or variations
- URL encode special characters if needed (`%2e%2e%2f` for `../`)

## Getting Started

If you haven't deployed the challenge yet:

```bash
kubectl apply -f challenges/beginner/file-disclosure/
```

Or use the deployment script:

```bash
cd challenges/beginner/file-disclosure
./deploy.sh
```

## Using Burp Suite

1. Configure your browser to use Burp Suite as a proxy
2. Visit `http://localhost:30102` in your browser
3. Try reading a file using the web form (e.g., `public/readme.txt`)
4. Intercept the request in Burp Suite Proxy
5. Modify the `file` parameter in the GET request
6. Try: `public/../private/flag.txt` or `public/../../app/data/private/flag.txt`
7. Forward the modified request and check the response

**Example request:**
```
GET /api/read?file=public/../private/flag.txt HTTP/1.1
```

## Path Traversal Techniques

The application only checks if the path starts with `public/`, but you can use path traversal:
- `public/../private/flag.txt` - Goes up one directory then into private
- `public/../../etc/passwd` - Goes up multiple directories
- URL-encoded: `public%2F..%2F..%2Fprivate%2Fflag.txt`

## Verification

Once you find the flag, verify it matches the format `FLAG{...}`

## Solution Path

<details>
<summary>Click to reveal the solution path</summary>

1. Access the web application at `http://localhost:30102`
2. Use Burp Suite Proxy to intercept a request to `/api/read`
3. Try a normal request first: `GET /api/read?file=public/readme.txt`
4. Modify the request to use path traversal: `GET /api/read?file=public/../private/flag.txt`
5. Forward the request and check the JSON response
6. The response will contain the flag in the `content` field
7. The flag is: `FLAG{path_traversal_escape_directories}`

**Alternative methods:**
- You can also try: `public/../../app/data/private/flag.txt`
- Or use URL encoding: `public%2F..%2Fprivate%2Fflag.txt`
- Direct browser access: `http://localhost:30102/api/read?file=public/../private/flag.txt`

</details>

## Security Lesson

This challenge demonstrates a critical file access vulnerability:

- **Always validate and sanitize file paths** - Never trust user input for file operations
- **Use whitelist-based access control** - Check if the resolved path is within allowed directories
- **Use proper path normalization** - Normalize paths before validation, not after
- **Prevent path traversal** - Filter or block sequences like `../`, `..\\`, encoded variants
- **Use chroot or jail directories** - Limit filesystem access to a specific directory
- **Principle of least privilege** - Applications should only have access to files they need

## Common Path Traversal Patterns

Attackers might try:
- `../` - Go up one directory
- `..\\` - Windows-style traversal
- `%2e%2e%2f` - URL-encoded `../`
- `....//` - Double encoding bypass
- `public/../../etc/passwd` - Accessing system files

## Burp Suite Tips

- Use Proxy → Intercept to modify requests in real-time
- Use Repeater to test multiple variations quickly
- Enable "URL-encode these characters" when needed
- Check both the decoded and encoded versions in the request

