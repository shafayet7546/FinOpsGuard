variable "aws_region" {
    description = "AWS region for resources"
    type = string
    default = "us-west-2"
    # currently restrict deployments to validation for accepted US-based AWS regions
    validation {
    condition = contains([
      "us-east-1",
      "us-east-2",
      "us-west-1",
      "us-west-2"
    ], var.aws_region)

    error_message = "Invalid AWS region selected. Only approved US regions are allowed."
    }
}
# reusable project identifier variable
variable "project" {
    description = "Project identifier for resource naming"
    type = string
    default = "finopsguard"
}