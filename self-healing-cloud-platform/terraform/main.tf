# Discover the default VPC in the target region for a beginner-friendly setup.
data "aws_vpc" "default" {
  default = true
}

# Discover subnets in the default VPC and select the first one for EC2 placement.
data "aws_subnets" "default_vpc_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Dynamically fetch the latest Amazon Linux 2 AMI in the selected region.
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security group controlling inbound and outbound network access.
resource "aws_security_group" "platform_sg" {
  name        = "self-healing-platform-sg"
  description = "Security group for Self-Healing Cloud Deployment Platform demo"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "Allow SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    description = "Allow HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.allowed_http_cidr]
  }

  ingress {
    description = "Allow Flask app port"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = [var.allowed_app_cidr]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    {
      Name        = "self-healing-platform-sg"
      Environment = "demo"
      Project     = "self-healing-cloud-platform"
      ManagedBy   = "terraform"
    },
    var.additional_tags
  )
}

# Single EC2 instance for lightweight infrastructure demonstration.
resource "aws_instance" "platform_node" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.instance_type
  subnet_id              = data.aws_subnets.default_vpc_subnets.ids[0]
  vpc_security_group_ids = [aws_security_group.platform_sg.id]
  key_name               = var.key_pair_name != "" ? var.key_pair_name : null

  # Basic hardening and update script executed during boot.
  user_data = <<-EOT
    #!/bin/bash
    set -eux
    yum update -y
    yum install -y curl
    echo "Self-Healing Cloud Deployment Platform bootstrap complete." > /var/log/self-healing-bootstrap.log
  EOT

  tags = merge(
    {
      Name        = var.instance_name
      Environment = "demo"
      Project     = "self-healing-cloud-platform"
      ManagedBy   = "terraform"
    },
    var.additional_tags
  )
}
