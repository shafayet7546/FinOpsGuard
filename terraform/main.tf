# virtual private connection
resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"

    tags = {
        Name = "${var.project}-vpc"
    }
}

resource "random_string" suffix {
    length = 8
    special = false
    upper = false
}

# storage for generated application reports
resource "aws_s3_bucket" "reports" {
    bucket = "${var.project}-reports-${random_string.suffix.result}"
    
    tags = {
        Name = "${var.project}-reports" 
    }
}

# trust policy assumed by EC2 to access AWS services
resource "aws_iam_role" "app_user_role" {
    name = "${var.project}-app-role"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [{
            Action = "sts:AssumeRole"
            Effect = "Allow"
            Principal = {
                Service = "ec2.amazonaws.com"
            }
        }]
    })
}

resource "aws_iam_policy" "app_policy" {
  name = "${var.project}-app-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.reports.arn,
          "${aws_s3_bucket.reports.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "app_policy_attach" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.app_policy.arn
}

# EKS Cluster (Fargate)
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name = var.project
  kubernetes_version = "1.30"

  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.private[*].id

  fargate_profiles = {
    default = {
      name = "default"
      selectors = [
        { namespace = "default" }
      ]
    }
  }

  tags = {
    Environment = "dev"
  }
}

# Kubernetes Deployment
# specified number of pods, resource requests and limits to ensure efficient utilization of cluster resources
resource "kubernetes_deployment" "finopsguard" {
  metadata {
    name = "finopsguard"
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "finopsguard"
      }
    }

    template {
      metadata {
        labels = {
          app = "finopsguard"
        }
      }

      spec {
        container {
          name  = "finopsguard"
          image = "finopsguard:latest"

          port {
            container_port = 8000
          }

          resources {
            requests = {
              cpu    = "250m"
              memory = "512Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "1Gi"
            }
          }
        }
      }
    }
 
  }
}

# Kubernetes Service (Load Balancer)
resource "kubernetes_service" "finopsguard" {
  metadata {
    name = "finopsguard"
  }

  spec {
    selector = {
      app = "finopsguard"
    }

    port {
      port        = 80
      target_port = 8000
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_horizontal_pod_autoscaler_v2" "finopsguard" {
  metadata {
    name = "finopsguard-hpa"
  }
  # autoscales pods based on cpu utilization, minimum of 2 pods and maximum of 4 pods to handle load
  # unlikely of utilization but to demonstrate understanding of hpa in Kubernetes and ability to scale based on demand
  spec {
    min_replicas = 2
    max_replicas = 4

    scale_target_ref {
      api_version = "apps/v1"
      kind = "Deployment"
      name = kubernetes_deployment.finopsguard.metadata[0].name
    }

    metric {
      type = "Resource"

      resource {
        name = "cpu"

        target {
          type = "Utilization"
          average_utilization = 70
        }
      }
    }
  }
}