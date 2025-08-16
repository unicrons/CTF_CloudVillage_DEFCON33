# Hexform - Cloud Village CTF 2025

## Challenge Overview

Hexform was an intricate Infrastructure as Code (IaC) challenge that required extracting a 7-part deactivation key from Terraform configuration files without executing `terraform plan` or `terraform apply` commands.

## Challenge Requirements

The goal was to analyze static Terraform files and piece together a complete flag from seven different parts (P1-P7) hidden throughout the configuration using various encoding and obfuscation techniques.

## Flag Reconstruction

The complete flag was: `FLAG-{he1iosI5A53cre7MsgFlagF0rTer4Pzl}`

## Solution Breakdown

### Part 1: "he1ios" - Unicode Steganography
**Location:** `assets/modules/1_network/variables.tf`
**Technique:** Hidden in invisible Unicode characters

The first part was concealed using invisible Unicode characters (⁢⁣) after Japanese text. We decoded the hidden binary sequence:
```
000000000110100000000000011001010000000000110001000000000110100100000000011011110000000001110011
```

ASCII decoding revealed: **"he1ios"** (Helios with 1 instead of l)

### Part 2: "I5" - String Concatenation
**Location:** `assets/modules/2_identity/main.tf`
**Technique:** Terraform join function

Found within bucket labels using Terraform's string manipulation:
```hcl
join("", ["I", "5"])
```

### Part 3: "A53cre7" - Base64 + Gzip Compression
**Location:** `assets/modules/3_storage/locals.tf`
**Technique:** Double encoding with compression

Extracted from a compressed and encoded gamma variable:
```bash
echo 'H4sICOvjgmgAA...' | base64 -d | gzip -d
# Output: {"key":"A53cre7"}
```

### Part 4: "Msg" - JSON Mapping
**Location:** `assets/main.tf` + `assets/data/geo_nodes.json`
**Technique:** Cross-file reference mapping

Used selection_map where `primary_node="eu-west-1"` mapped to `"Msg"` in the geo_nodes.json data structure.

### Part 5: "FlagF0r" - String Manipulation  
**Location:** `assets/modules/4_decoy_compute/main.tf`
**Technique:** Terraform substr function

Extracted using substring operation:
```hcl
substr("zz-FlagF0r-FROM-zz", 3, 7) = "FlagF0r"
```

### Part 6: "Ter4" - Nested Ternary Logic
**Location:** `assets/locals.tf`
**Technique:** Complex conditional logic

Hidden in nested ternary operators:
```hcl
var.env_mode == "prod" ? (true ? "Ter4" : "DEBUG") : "DEV"
```

When `env_mode` equals "prod", the inner ternary always evaluates to "Ter4".

### Part 7: "Pzl" - Direct Output
**Location:** `assets/modules/2_identity/outputs.tf`
**Technique:** Plain text output value

The final part was stored as a direct output value: `"Pzl"`

#TODO: Add screenshots showing the specific locations of each part in the Terraform files

## Key Techniques Used

- **Static Code Analysis:** Examining Terraform files without execution
- **Unicode Steganography:** Invisible character detection and binary decoding
- **Multi-layer Encoding:** Base64 and gzip decompression
- **Cross-file Reference Resolution:** Following data relationships between files
- **String Manipulation Analysis:** Understanding Terraform string functions
- **Conditional Logic Evaluation:** Analyzing ternary operators and variable states

## Tools and Methods

- Text editors with Unicode support for invisible character detection
- Command-line tools: `base64`, `gzip`, `xxd` for decoding
- Manual Terraform configuration analysis
- JSON parsing for data structure examination

## Lessons Learned

This challenge demonstrated:
- **IaC Security:** How sensitive information can be hidden in infrastructure code
- **Multi-layer Obfuscation:** The complexity of modern steganographic techniques
- **Static Analysis Importance:** The need to analyze code without execution
- **Cross-file Dependencies:** How information can be scattered across multiple configuration files

The Hexform challenge showcased sophisticated methods for hiding information in Infrastructure as Code, emphasizing the importance of thorough security reviews of Terraform and similar IaC tools in production environments.