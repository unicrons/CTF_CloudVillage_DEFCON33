variable "env_mode" {
  description = "Toggle between production and dev mode"
  type        = string
  default     = "prod" // used in ternary condition later
}
