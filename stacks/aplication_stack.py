import time

from aws_cdk import (
    # Duration,
    Stack,
    aws_ecs_patterns as ecs_patterns,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ecr as ecr,
)
from constructs import Construct

class ApplicationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
                
        docker_tag = self.node.try_get_context("docker_tag")
        mongodb_uri = self.node.try_get_context("mongodb_uri")

        # Creamos la VPC
        vpc = ec2.Vpc(
            self,
            "EcsClusterVpc",
            max_azs=2,
        )

        # Se crea el cluster
        cluster = ecs.Cluster(
            self,
            "EcsCluster",
            vpc=vpc,
        )
        
        # Se define un rol
        ecs_task_role = iam.Role(
            self,
            "EcsTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="Grant access to multiple AWS services",
        )

        # Conexion al repositorio en ECR
        ecr_repository = ecr.Repository.from_repository_name(
            self,
            "EcrRepository",
            "demo-fastapi-mongodb-1",
        )

        # Se sube la ultima version de la imagen 
        ecr_image = ecs.ContainerImage.from_ecr_repository(
            ecr_repository,
            docker_tag, #El tag hara un cambio cada ves que queramos deployar el repositorio
        )

        # Definimos la imagen para el contenedor
        fargate_cluster = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "EcsFargateService",
            cluster=cluster,
            memory_limit_mib=1024,
            cpu=512,
            desired_count=1,    
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecr_image,  
                task_role=ecs_task_role,
                environment={
                    "MONGODB_URI": mongodb_uri
                }
            ),
        )

        fargate_cluster.target_group.configure_health_check(
            path="/healthcheck"
        )
