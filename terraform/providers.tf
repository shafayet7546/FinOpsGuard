terraform {
    # pin AWS provider version to ensure reproducible builds
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 5.0"
        }
        random = {
            source = "hashicorp/random"
            version = "~> 3.0"
        }
    }
}
# region is variable-driven to allow:
# -multi-region deployments
# -reuse capabilities across environments
provider "aws" {
    region = var.aws_region
}