# Actions - Cloud Village CTF 2025

## Challenge Overview

The Actions challenge provided us with base64-encoded values that appeared to be related to GitHub Actions workflows and AWS IAM roles.

## Initial Discovery

We were given two base64-encoded strings:
- `YXJuOmF3czppYW06OjE3MDk3NDUwNjUxNTpyb2xlL2dpdGh1Yi1kZXBsb3ltZW50LXJvbGU=`
- `aW50ZXJuYWwvc2VjcmV0cy9pZC12Mg==`

## Solution

Decoding the first base64 string revealed an AWS IAM role ARN:

```bash
echo 'YXJuOmF3czppYW06OjE3MDk3NDUwNjUxNTpyb2xlL2dpdGh1Yi1kZXBsb3ltZW50LXJvbGU=' | base64 -d
# Output: arn:aws:iam::170974506515:role/github-deployment-role
```

The second string decoded to a secret path:

```bash
echo 'aW50ZXJuYWwvc2VjcmV0cy9pZC12Mg==' | base64 -d
# Output: internal/secrets/id-v2
```

#TODO: Add details about how these decoded values were used to access the GitHub Actions workflow and retrieve the flag, including any specific steps taken to exploit the GitHub deployment role or access the secret.

## Key Takeaways

This challenge demonstrated the importance of:
- Proper secret management in CI/CD pipelines
- Securing GitHub Actions workflows
- Understanding the relationship between cloud IAM roles and automation services

#TODO: Add the actual flag that was retrieved
