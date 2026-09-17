terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "nginx" {
  name = "nginx:alpine"
}

resource "docker_container" "terraform_demo" {
  name  = "kyc-terraform-demo"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = 8082
  }
}