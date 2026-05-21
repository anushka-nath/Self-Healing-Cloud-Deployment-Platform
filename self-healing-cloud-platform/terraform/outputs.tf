# Useful outputs for post-deployment verification and access.
output "instance_id" {
  description = "ID of the created EC2 instance."
  value       = aws_instance.platform_node.id
}

output "instance_public_ip" {
  description = "Public IP of the EC2 instance."
  value       = aws_instance.platform_node.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the EC2 instance."
  value       = aws_instance.platform_node.public_dns
}

output "security_group_id" {
  description = "ID of the security group attached to the instance."
  value       = aws_security_group.platform_sg.id
}

output "ssh_command" {
  description = "Ready-to-run SSH command if key_pair_name is configured."
  value       = var.key_pair_name != "" ? "ssh -i <path-to-private-key> ec2-user@${aws_instance.platform_node.public_ip}" : "SSH key pair not configured."
}
