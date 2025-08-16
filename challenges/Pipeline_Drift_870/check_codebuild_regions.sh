#!/bin/bash

# Script to check CodeBuild projects across all AWS regions enabled by default
# Default AWS regions (as of 2024)
DEFAULT_REGIONS=(
    "us-east-1"
    "us-east-2"
    "us-west-1"
    "us-west-2"
    "af-south-1"
    "ap-east-1"
    "ap-south-1"
    "ap-northeast-1"
    "ap-northeast-2"
    "ap-northeast-3"
    "ap-southeast-1"
    "ap-southeast-2"
    "ap-southeast-3"
    "ap-southeast-4"
    "ca-central-1"
    "eu-central-1"
    "eu-west-1"
    "eu-west-2"
    "eu-west-3"
    "eu-north-1"
    "eu-south-1"
    "eu-south-2"
    "me-south-1"
    "me-central-1"
    "sa-east-1"
    "us-gov-east-1"
    "us-gov-west-1"
)

echo "Checking CodeBuild projects across all default AWS regions..."
echo "=========================================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: AWS CLI is not configured or credentials are invalid"
    exit 1
fi

# Get current identity for reference
echo "Current AWS Identity:"
aws sts get-caller-identity
echo ""

# Counter for projects found
total_projects=0
regions_with_projects=0

# Loop through each region
for region in "${DEFAULT_REGIONS[@]}"; do
    echo "Checking region: $region"

    # Try to list CodeBuild projects in this region
    if result=$(aws codebuild list-projects --region "$region" 2>&1); then
        # Extract the projects array
        projects=$(echo "$result" | jq -r '.projects[]?' 2>/dev/null)

        if [ -n "$projects" ]; then
            echo "  ✅ Found projects in $region:"
            echo "$projects" | while read -r project; do
                echo "    - $project"
            done
            ((total_projects += $(echo "$projects" | wc -l)))
            ((regions_with_projects++))
        else
            echo "  ❌ No projects found"
        fi
    else
        echo "  ⚠️  Error or no access to CodeBuild in $region:"
        echo "     $result"
    fi

    echo ""
done

echo "=========================================================="
echo "Summary:"
echo "  Regions with projects: $regions_with_projects"
echo "  Total projects found: $total_projects"
echo "  Regions checked: ${#DEFAULT_REGIONS[@]}"