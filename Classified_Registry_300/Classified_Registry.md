# Classified Registry - Cloud Village CTF 2025

## Challenge Overview

The Classified Registry challenge involved container security and environment variable enumeration. The challenge centered around discovering sensitive information stored within container environment variables.

## Challenge Description

The challenge presented what appeared to be a website with some form of "lock picking pattern" that needed to be bypassed to access a container registry or containerized application.

## Solution

The key to solving this challenge was understanding that the flag was stored as an environment variable within a Docker container. The approach involved:

1. **Container Access:** Gaining access to the running container
2. **Environment Enumeration:** Listing all environment variables within the container
3. **Flag Discovery:** Identifying the specific environment variable containing the flag

### Container Environment Analysis

Once inside the container, we enumerated the environment variables and found:

```bash
env | grep FLAG
# or
printenv | grep MY_ENV_VAR
```

### Flag Discovery

The flag was stored in an environment variable named `MY_ENV_VAR`:

```
MY_ENV_VAR=FLAG-{zDAkRWAi4znMkIhjaqZnU2T264XG2fPQ}
```

## Flag
`FLAG-{zDAkRWAi4znMkIhjaqZnU2T264XG2fPQ}`

## Key Techniques
- Container security assessment
- Environment variable enumeration
- Docker container access
- Registry exploitation

#TODO: Add details about the specific "website lock picking pattern" mentioned in the notes and how it was used to gain container access

## Lessons Learned

This challenge highlighted several important security concepts:
- **Environment Variable Security:** Sensitive data should never be stored in environment variables, as they're easily accessible to anyone with container access
- **Container Hardening:** Proper container security involves limiting access to runtime information
- **Secret Management:** Use proper secret management solutions instead of environment variables for sensitive data

The challenge demonstrated how seemingly simple container misconfigurations can lead to complete exposure of sensitive information.