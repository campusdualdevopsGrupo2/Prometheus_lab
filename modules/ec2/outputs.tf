

output "prometheus_sg_id" {
  description = "ID del security group de Elasticsearch"
  value       = aws_security_group.prometheus.id
}

