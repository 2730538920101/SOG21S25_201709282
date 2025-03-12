resource "aws_vpc" "PracticaSOG" {                # Creating VPC here
  cidr_block           = var.PracticaSOG_vpc_cidr # Defining the CIDR block use 10.0.0.0/24 for demo
  instance_tenancy     = "default"
  enable_dns_hostnames = true
  enable_dns_support   = true
}

resource "aws_internet_gateway" "IGW" { # Creating Internet Gateway
  vpc_id = aws_vpc.PracticaSOG.id          # vpc_id will be generated after we create VPC
}

resource "aws_subnet" "PublicS1" { # Creating Public Subnets
  vpc_id                  = aws_vpc.PracticaSOG.id
  map_public_ip_on_launch = "true"
  availability_zone       = "us-east-1a"
  cidr_block              = var.public1 # CIDR block of public subnets
}
#Create a Private Subnet                   # Creating Private Subnets
resource "aws_subnet" "PrivateS1" {
  vpc_id            = aws_vpc.PracticaSOG.id
  cidr_block        = var.private1 # CIDR block of private subnets
  availability_zone = "us-east-1a"
}
#Create a Public Subnets.
resource "aws_subnet" "PublicS2" { # Creating Public Subnets
  vpc_id                  = aws_vpc.PracticaSOG.id
  map_public_ip_on_launch = "true"
  availability_zone       = "us-east-1b"
  cidr_block              = var.public2 # CIDR block of public subnets
}
#Create a Private Subnet                   # Creating Private Subnets
resource "aws_subnet" "PrivateS2" {
  vpc_id            = aws_vpc.PracticaSOG.id
  cidr_block        = var.private2 # CIDR block of private subnets
  availability_zone = "us-east-1b"
}

#Route table for Public Subnet's
resource "aws_route_table" "PublicRT" { # Creating RT for Public Subnet
  vpc_id = aws_vpc.PracticaSOG.id
  route {
    cidr_block = "0.0.0.0/0" # Traffic from Public Subnet reaches Internet via Internet Gateway
    gateway_id = aws_internet_gateway.IGW.id
  }
}
#Route table for Private Subnet's
resource "aws_route_table" "PrivateRT" { # Creating RT for Private Subnet
  vpc_id = aws_vpc.PracticaSOG.id
  route {
    cidr_block     = "0.0.0.0/0" # Traffic from Private Subnet reaches Internet via NAT Gateway
    nat_gateway_id = aws_nat_gateway.NATgw.id
  }
}
#Route table Association with Public Subnet's
resource "aws_route_table_association" "PublicRTassociation" {
  subnet_id      = aws_subnet.PublicS1.id
  route_table_id = aws_route_table.PublicRT.id
}
#Route table Association with Private Subnet's
resource "aws_route_table_association" "PrivateRTassociation" {
  subnet_id      = aws_subnet.PrivateS1.id
  route_table_id = aws_route_table.PrivateRT.id
}

#Route table Association with Public Subnet's
resource "aws_route_table_association" "PublicRTassociation2" {
  subnet_id      = aws_subnet.PublicS2.id
  route_table_id = aws_route_table.PublicRT.id
}
#Route table Association with Private Subnet's
resource "aws_route_table_association" "PrivateRTassociation2" {
  subnet_id      = aws_subnet.PrivateS2.id
  route_table_id = aws_route_table.PrivateRT.id
}

#Creating the NAT Gateway using subnet_id and allocation_id
resource "aws_nat_gateway" "NATgw" {
  allocation_id = aws_eip.nateIP.id
  subnet_id     = aws_subnet.PrivateS1.id
}

resource "aws_eip" "nateIP" {

}
