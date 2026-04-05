output "vpc_id" {
    value = aws_vpc.main.id
}

output "s3_bucket_name" {
    value = aws_s3_bucket.reports.bucket
}

output "load_balancer_dns" {
    value = kubernetes_service.finopsguard.status[0].load_balancer[0].ingress[0].hostname
}