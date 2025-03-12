resource "aws_db_subnet_group" "mysql-subnet-group" {
  name       = "mysql-subnet-group"
  subnet_ids = ["${aws_subnet.PrivateS1.id}", "${aws_subnet.PrivateS2.id}"]
}

resource "aws_db_instance" "mysql-instance" {
  allocated_storage       = 100
  engine                  = "mysql"
  engine_version          = "8.4.4"
  instance_class          = "db.t3.micro"
  identifier              = "mysql"
  db_name                 = var.DATABASE_NAME
  username                = var.DATABASE_USER
  password                = var.DATABASE_PASSWORD
  db_subnet_group_name    = aws_db_subnet_group.mysql-subnet-group.name
  multi_az                = "false"
  vpc_security_group_ids  = ["${aws_security_group.MySql-sg.id}"]
  storage_type            = "gp2"
  backup_retention_period = 30
  availability_zone       = aws_subnet.PrivateS1.availability_zone
  skip_final_snapshot     = true
}

resource "aws_security_group" "MySql-sg" {
  vpc_id = aws_vpc.PracticaSOG.id
  name   = "MySql-sg"
  egress = [
    {
      cidr_blocks      = ["0.0.0.0/0", ]
      description      = ""
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "-1"
      security_groups  = []
      self             = false
      to_port          = 0
    }
  ]
  ingress = [
    {
      cidr_blocks      = ["0.0.0.0/0",]
      description      = ""
      from_port        = 3306
      to_port          = 3306
      protocol         = "tcp"
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      self             = false
      security_groups  = ["${aws_security_group.PracticaSOG-sg.id}"]
    }
  ]
}