# ===================================
# VPC and Network Outputs
# ===================================

output "vpc_id" {
  description = "ID of the VPC created for the platform"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_id" {
  description = "ID of the public subnet"
  value       = aws_subnet.public.id
}

output "private_subnet_id" {
  description = "ID of the private subnet"
  value       = aws_subnet.private.id
}

output "internet_gateway_id" {
  description = "ID of the internet gateway"
  value       = aws_internet_gateway.main.id
}

# ===================================
# Security Group Outputs
# ===================================

output "eks_cluster_security_group_id" {
  description = "ID of the EKS cluster security group"
  value       = aws_security_group.eks_cluster_sg.id
}

output "eks_nodes_security_group_id" {
  description = "ID of the EKS nodes security group"
  value       = aws_security_group.eks_nodes_sg.id
}

output "platform_security_group_id" {
  description = "ID of the platform security group"
  value       = aws_security_group.platform_sg.id
}

# ===================================
# IAM Role Outputs
# ===================================

output "eks_service_role_arn" {
  description = "ARN of the EKS service role"
  value       = aws_iam_role.eks_service_role.arn
}

output "eks_node_role_arn" {
  description = "ARN of the EKS node role"
  value       = aws_iam_role.eks_node_role.arn
}

output "ec2_role_arn" {
  description = "ARN of the EC2 instance role"
  value       = aws_iam_role.ec2_role.arn
}

# ===================================
# EC2 Instance Outputs
# ===================================

output "instance_id" {
  description = "ID of the created EC2 instance"
  value       = aws_instance.platform_node.id
}

output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.platform_node.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.platform_node.public_dns
}

output "instance_private_ip" {
  description = "Private IP of the EC2 instance"
  value       = aws_instance.platform_node.private_ip
}

# ===================================
# Access Information
# ===================================

output "ssh_command" {
  description = "Ready-to-run SSH command to access the instance"
  value       = var.key_pair_name != "" ? "ssh -i <path-to-private-key> ec2-user@${aws_instance.platform_node.public_ip}" : "SSH key pair not configured. Configure key_pair_name variable."
}

output "instance_access_url" {
  description = "HTTP URL to access the Flask application"
  value       = "http://${aws_instance.platform_node.public_ip}:5000"
}

# ===================================
# Infrastructure Summary
# ===================================

output "infrastructure_summary" {
  description = "Summary of the deployed infrastructure"
  value = {
    region         = var.aws_region
    environment    = var.environment
    vpc_cidr       = aws_vpc.main.cidr_block
    instance_type  = var.instance_type
    security_groups = {
      eks_cluster = aws_security_group.eks_cluster_sg.id
      eks_nodes   = aws_security_group.eks_nodes_sg.id
      platform    = aws_security_group.platform_sg.id
    }
    iam_roles = {
      eks_service = aws_iam_role.eks_service_role.arn
      eks_nodes   = aws_iam_role.eks_node_role.arn
      ec2         = aws_iam_role.ec2_role.arn
    }
  }
}
