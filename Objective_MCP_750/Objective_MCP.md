# Objective MCP - Cloud Village CTF 2025

## Challenge Overview

Objective MCP was a sophisticated Azure cloud security challenge that involved exploiting Model Context Protocol (MCP) servers and Azure Key Vault misconfigurations to demonstrate RBAC privilege escalation vulnerabilities.

## Initial Discovery

### MCP Server Identification
The challenge began with discovering an MCP server running at:
**Target:** `http://13.91.85.21:8080`

Model Context Protocol is a framework for AI assistants to interact with external tools and services, making it an interesting attack vector for cloud environments.

## MCP Exploitation

### Tool Enumeration
We used JSON-RPC calls to enumerate available MCP tools and services:

```bash
# List available MCP tools
curl -X POST http://13.91.85.21:8080 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### Azure Key Vault Discovery
The MCP server exposed tools for interacting with Azure Key Vaults, revealing:

**Development Environment:**
- Access to dev vault secrets:
  - `api-key`
  - `app-settings` 
  - `db-connection`

**Security Warning:** The enumeration revealed an excessive permissions warning, indicating the development identity had more access than intended.

## Azure RBAC Misconfiguration

### Cross-Environment Access
The critical vulnerability was an RBAC misconfiguration where the development identity had production access:

**Production Key Vault:** `https://kv-ctf-prod-uqrl85n4.vault.azure.net/`

### Privilege Escalation
Despite being a development identity, we discovered it could access production resources due to improper Azure role assignments.

## Flag Extraction

### Production Secret Access
Using the MCP server's admin functions, we accessed the production Key Vault:

1. **Vault Discovery:** Identified the production Key Vault URL
2. **Secret Enumeration:** Listed available secrets in production
3. **Flag Retrieval:** Found and extracted the `ctf-flag` secret

### Admin Function Exploitation
The MCP server provided admin-level functions that allowed direct extraction of the flag from the production environment:

## Flag
`FLAG-{OwldcqhaOtCFcpS0u4khfg23hassw90q}`

## Attack Summary

1. **MCP Server Discovery:** Found exposed MCP server with Azure integration
2. **Tool Enumeration:** Used JSON-RPC to list available cloud tools  
3. **Development Access:** Gained access to development Key Vault secrets
4. **RBAC Analysis:** Identified excessive permissions warning
5. **Production Discovery:** Found production Key Vault URL
6. **Privilege Escalation:** Exploited RBAC misconfiguration for prod access
7. **Flag Extraction:** Retrieved flag using admin MCP functions

## Key Vulnerabilities

- **RBAC Misconfiguration:** Development identity with production access
- **Excessive Permissions:** Identity granted more privileges than needed
- **MCP Security:** Exposed server with admin functions
- **Cross-Environment Access:** Poor environment isolation

## Technical Insights

### Model Context Protocol
This challenge introduced MCP as a potential attack vector:
- AI assistants using MCP can access cloud resources
- Poor configuration can lead to privilege escalation
- JSON-RPC interfaces need proper security controls

### Azure Key Vault Security
Key lessons about Azure Key Vault security:
- Proper RBAC configuration is critical
- Environment isolation must be enforced
- Regular access reviews are essential
- Principle of least privilege should be applied

## Key Techniques
- Model Context Protocol exploitation
- JSON-RPC enumeration and manipulation
- Azure RBAC analysis and privilege escalation
- Cross-environment resource access
- Key Vault secret extraction

## Lessons Learned

This challenge highlighted critical cloud security concepts:
- **Environment Isolation:** Dev and prod must be properly separated
- **RBAC Principle of Least Privilege:** Grant minimal necessary permissions
- **AI Integration Security:** Emerging AI tools create new attack surfaces
- **Regular Access Audits:** Periodically review and validate permissions
- **MCP Security:** New protocols require security considerations

The Objective MCP challenge demonstrated how modern AI integration tools can become attack vectors when cloud environments are not properly secured, emphasizing the need for comprehensive RBAC reviews in Azure environments.