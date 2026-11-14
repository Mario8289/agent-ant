"""CDK entry point for the agent-ant ops scheduler (#96).

Run ``cdk synth``/``cdk diff``/``cdk deploy`` from ``infra/cdk`` (or ``just cdk-*``), passing the
account-specific values with ``-c key=value``. ``accountId`` and ``awsRegion`` set the stack's
``env`` so ``Vpc.from_lookup`` can resolve concrete account/region at synth time; everything else
is read by ``SchedulerStack`` itself.
"""

import aws_cdk as cdk
from scheduler_stack import SchedulerStack

app = cdk.App()

account_id = app.node.try_get_context("accountId")
region = app.node.try_get_context("awsRegion") or "eu-west-2"
env = cdk.Environment(account=account_id, region=region) if account_id else None

SchedulerStack(app, "AgentAntScheduler", env=env)

app.synth()
