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
        kubernetes = {
            source = "hashicorp/kubernetes"
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

provider "kubernetes" {
    host = module.eks_cluster.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks_cluster_certificate.certificate_authority_data)
    exec {
      api_version = "client.authentication.k8s.io/v1"
      command = "aws"
      args = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
}