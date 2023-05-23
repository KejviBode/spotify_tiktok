variable "app_count" {
  type    = number
  default = 1
}

variable "DB_NAME" {
  type      = string
  sensitive = true
}
variable "DB_USER" {
  type      = string
  sensitive = true
}
variable "DB_PASSWORD" {
  type      = string
  sensitive = true
}
variable "DB_HOST" {
  type      = string
  sensitive = true
}

data "aws_vpc" "c7_vpc" {
  id = "vpc-010fd888c94cf5102"
}

data "aws_subnet" "eu-west-2a-public" {
  vpc_id = data.aws_vpc.c7_vpc.id
  id     = "subnet-0bd43551b596597e1"
}

data "aws_subnet" "eu-west-2b-public" {
  vpc_id = data.aws_vpc.c7_vpc.id
  id     = "subnet-07f982f51c870f9d1"
}

data "aws_subnet" "eu-west-2c-public" {
  vpc_id = data.aws_vpc.c7_vpc.id
  id     = "subnet-0b265a90c0cadfb99"
}

data "aws_subnet" "eu-west-2a-private" {
  vpc_id = data.aws_vpc.c7_vpc.id
  id     = "subnet-0c98b79bf7e67b3d6"
}

data "aws_subnet" "eu-west-2b-private" {
  vpc_id = data.aws_vpc.c7_vpc.id
  id     = "subnet-050a7efe086ea2bc9"
}


resource "aws_security_group" "spotify-tiktok-alb-sg" {
  name   = "spotify-tiktok-alb-sg"
  vpc_id = data.aws_vpc.c7_vpc.id

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "spotify-tiktok-lb" {
  name = "spotify-tiktok-lb"
  subnets = [data.aws_subnet.eu-west-2a-public.id,
    data.aws_subnet.eu-west-2b-public.id,
  data.aws_subnet.eu-west-2c-public.id]
  security_groups = [aws_security_group.spotify-tiktok-alb-sg.id]
}


resource "aws_lb_target_group" "spotify-tiktok-dash-tg" {
  name        = "spotify-tiktok-dash-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.c7_vpc.id
  target_type = "ip"
}

resource "aws_lb_listener" "spotify-tiktok-listener" {
  load_balancer_arn = aws_lb.spotify-tiktok-lb.id
  port              = "80"
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_lb_target_group.spotify-tiktok-dash-tg.id
    type             = "forward"
  }
}

resource "aws_ecs_task_definition" "spotify-tiktok-dash-app" {
  family                   = "spotify-tiktok-dash-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = "arn:aws:iam::605126261673:role/ecsTaskExecutionRole"

  container_definitions = jsonencode(
    [
      {
        "image" : "605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7_kejvi_basic:latest",
        "cpu" : 1024,
        "memory" : 2048,
        "name" : "c7_kejvi_basic",
        "networkMode" : "awsvpc",
        "environment" : [
          {
            "name" : "DB_PORT",
            "value" : "5432",
          },
          {
            "name" : "DB_HOST",
            "value" : var.DB_HOST
          },
          {
            "name" : "DB_NAME",
            "value" : var.DB_NAME
          },
          {
            "name" : "DB_USER",
            "value" : var.DB_USER
          },
          {
            "name" : "DB_PASSWORD",
            "value" : var.DB_PASSWORD
          }
        ],
        "portMappings" : [
          {
            "containerPort" : 8080,
            "hostPort" : 8080
          }
        ]
      }
    ]
  )
}

resource "aws_security_group" "spotify-tiktok-task-sg" {
  name   = "spotify-tiktok-task-sg"
  vpc_id = data.aws_vpc.c7_vpc.id

  ingress {
    protocol    = "tcp"
    from_port   = 8080
    to_port     = 8080
    cidr_blocks = ["0.0.0.0/0"]
    # security_groups = [aws_security_group.spotify-tiktok-alb-sg.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_cluster" "spotify-tiktok-cluster" {
  name = "spotify-tiktok-cluster"
}

resource "aws_ecs_service" "spotify-tiktok-service-dash" {
  name            = "spotify-tiktok-dash-service"
  cluster         = aws_ecs_cluster.spotify-tiktok-cluster.id
  task_definition = aws_ecs_task_definition.spotify-tiktok-dash-app.arn
  desired_count   = var.app_count
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.spotify-tiktok-task-sg.id]
    subnets          = [data.aws_subnet.eu-west-2a-public.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.spotify-tiktok-dash-tg.id
    container_name   = "c7_kejvi_basic"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.spotify-tiktok-listener]
}

output "load_balancer_ip" {
  value = aws_lb.spotify-tiktok-lb.dns_name
}
