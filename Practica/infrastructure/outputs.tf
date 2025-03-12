output "public_ip" {
  value = try(aws_instance.ec2_bastion.public_ip, "")
}

output "rds_endpoint" {
  value = aws_db_instance.mysql-instance.endpoint
}

output "rds_username" {
  value = aws_db_instance.mysql-instance.username
}

output "rds_password" {
  sensitive = true
  value     = aws_db_instance.mysql-instance.password
}

output "rds_db_name" {
  value = aws_db_instance.mysql-instance.db_name
}