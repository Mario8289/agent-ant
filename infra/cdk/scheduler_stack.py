"""The agent-ant ops scheduler: EventBridge Scheduler -> ECS Fargate one-off tasks (#96).

``retry-sms``, ``retry-extractions`` and ``purge`` are scripts, not self-scheduling. App Runner
(D-020) has no native cron, so they run as one-off Fargate tasks on the same container image,
triggered by EventBridge Scheduler. There is one task definition per script because EventBridge
Scheduler's ECS target cannot override a container's command — the command is baked into the
task definition.

Account-specific values come from CDK context (``-c key=value``) so nothing secret or
environment-specific is committed here. See ``README.md`` and ``docs/10-manual-steps.md`` for the
list of keys and the deploy command.
"""

from typing import Any

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_scheduler as scheduler
from aws_cdk import aws_scheduler_targets as targets
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct

# Default cadence for the retry scripts. A failed send/extraction should not sit failed for long,
# but every minute is noisy; five minutes is the handoff's recommendation (#96).
DEFAULT_RETRY_RATE_MINUTES = 5

# The purge runs daily, off-peak (03:00 UTC). Outbound ``to``/``body`` age past 30 days otherwise
# (D-021, D-025).
PURGE_CRON = "0 3 * * ? *"


class SchedulerStack(cdk.Stack):
    """The scheduled ops tasks: retry-sms, retry-extractions (every ~5 min) and purge (daily)."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        image_uri = self._require("imageUri")
        database_url_secret_arn = self._require("databaseUrlSecretArn")
        twilio_auth_token_secret_arn = self._require("twilioAuthTokenSecretArn")
        twilio_account_sid = self._require("twilioAccountSid")
        twilio_from_number = self._require("twilioFromNumber")
        vpc_id = self._require("vpcId")

        business_name = self._optional("businessName")
        public_base_url = self._optional("publicBaseUrl")
        llm_provider = self._optional("llmProvider") or "bedrock"
        llm_model = self._optional("llmModel") or "eu.anthropic.claude-sonnet-4-6"
        aws_region = self._optional("awsRegion") or "eu-west-2"
        retry_rate_minutes = int(self._optional("retryRateMinutes") or DEFAULT_RETRY_RATE_MINUTES)

        # Shared IAM. The execution role pulls the image and reads the two secrets; the task role
        # lets retry-extractions call Bedrock. Both are assumed by ECS, not by the scheduler.
        execution_role = iam.Role(
            self,
            "ExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="Pulls the image, reads secrets and writes logs for the scheduled ops tasks",
        )
        execution_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AmazonECSTaskExecutionRolePolicy"
            )
        )
        database_url_secret = secretsmanager.Secret.from_secret_complete_arn(
            self, "DatabaseUrl", secret_complete_arn=database_url_secret_arn
        )
        twilio_auth_token_secret = secretsmanager.Secret.from_secret_complete_arn(
            self, "TwilioAuthToken", secret_complete_arn=twilio_auth_token_secret_arn
        )
        database_url_secret.grant_read(execution_role)
        twilio_auth_token_secret.grant_read(execution_role)

        task_role = iam.Role(
            self,
            "TaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="Grants the scheduled tasks access to Bedrock for extraction retries",
        )
        task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:Converse",
                    "bedrock:ConverseStream",
                ],
                # The Bedrock spend guard (SCP, docs/10) is the hard limit; narrow this to the
                # locked model's ARN at the same time as the App Runner instance role (D-016).
                resources=["*"],
            )
        )

        environment = {
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO",
            "TWILIO_ACCOUNT_SID": twilio_account_sid,
            "TWILIO_FROM_NUMBER": twilio_from_number,
            "BUSINESS_NAME": business_name,
            "PUBLIC_BASE_URL": public_base_url,
            "LLM_PROVIDER": llm_provider,
            "LLM_MODEL": llm_model,
            "AWS_REGION": aws_region,
        }
        # Drop unset optional values (``_optional`` returns "") so the container does not get
        # empty ``BUSINESS_NAME``/``PUBLIC_BASE_URL`` — unset falls back to the app's defaults.
        environment = {key: value for key, value in environment.items() if value}
        secrets = {
            "DATABASE_URL": ecs.Secret.from_secrets_manager(database_url_secret),
            "TWILIO_AUTH_TOKEN": ecs.Secret.from_secrets_manager(twilio_auth_token_secret),
        }

        # One cluster, one set of roles, three task definitions. The VPC is looked up (not imported)
        # so public subnets can be selected by type: the task must live in a public subnet to reach
        # Twilio, Supabase and AWS APIs without NAT (see README).
        vpc = ec2.Vpc.from_lookup(self, "Vpc", vpc_id=vpc_id)
        cluster = ecs.Cluster(self, "OpsCluster", vpc=vpc)

        retry_sms = self._task_definition(
            "retry-sms",
            ["python", "scripts/retry_sms.py"],
            image_uri,
            environment,
            secrets,
            execution_role,
            task_role,
        )
        retry_extractions = self._task_definition(
            "retry-extractions",
            ["python", "scripts/retry_extractions.py"],
            image_uri,
            environment,
            secrets,
            execution_role,
            task_role,
        )
        purge = self._task_definition(
            "purge",
            ["python", "scripts/purge_old_data.py"],
            image_uri,
            environment,
            secrets,
            execution_role,
            task_role,
        )

        def target(task_definition: ecs.FargateTaskDefinition) -> targets.EcsRunFargateTask:
            # Public subnet + a public IP so the task can reach Twilio, Supabase and AWS APIs;
            # the VPC's default security group allows the outbound calls. Move to private subnets
            # + NAT + VPC endpoints before this carries real traffic.
            return targets.EcsRunFargateTask(
                cluster,
                task_definition=task_definition,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                assign_public_ip=True,
            )

        scheduler.Schedule(
            self,
            "RetrySms",
            schedule=scheduler.ScheduleExpression.rate(cdk.Duration.minutes(retry_rate_minutes)),
            target=target(retry_sms),
        )
        scheduler.Schedule(
            self,
            "RetryExtractions",
            schedule=scheduler.ScheduleExpression.rate(cdk.Duration.minutes(retry_rate_minutes)),
            target=target(retry_extractions),
        )
        scheduler.Schedule(
            self,
            "Purge",
            schedule=scheduler.ScheduleExpression.expression(PURGE_CRON),
            target=target(purge),
        )

    def _task_definition(
        self,
        name: str,
        command: list[str],
        image_uri: str,
        environment: dict[str, str],
        secrets: dict[str, ecs.Secret],
        execution_role: iam.Role,
        task_role: iam.Role,
    ) -> ecs.FargateTaskDefinition:
        family = f"agent-ant-{name}"
        task_definition = ecs.FargateTaskDefinition(
            self,
            f"{''.join(part.title() for part in name.split('-'))}Task",
            family=family,
            cpu=256,
            memory_limit_mib=512,
            execution_role=execution_role,
            task_role=task_role,
        )
        task_definition.add_container(
            "app",
            image=ecs.ContainerImage.from_registry(image_uri),
            command=command,
            environment=environment,
            secrets=secrets,
            logging=ecs.LogDrivers.aws_logs(stream_prefix=family),
        )
        return task_definition

    def _require(self, key: str) -> str:
        value = self._optional(key)
        if not value:
            raise ValueError(
                f"missing required CDK context: pass -c {key}=... (see docs/10-manual-steps.md)"
            )
        return value

    def _optional(self, key: str) -> str:
        value = self.node.try_get_context(key)
        return "" if value is None else str(value)
