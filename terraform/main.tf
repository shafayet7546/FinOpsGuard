# virtual private connection
resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"

    tags = {
        Name = "${var.project}-vpc"
    }
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

resource "random_string" suffix {
    length = 8
    special = false
    upper = false
}