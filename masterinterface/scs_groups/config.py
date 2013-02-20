from workflows.models import Workflow, State, Transition, WorkflowPermissionRelation, StatePermissionRelation
from permissions.models import Permission, Role

# WORKFLOW DEFINITION
SubscriptionRequestWorkflow, created = Workflow.objects.get_or_create(name="SubscriptionRequestWorkflow")

# roles
group_manager, created = Role.objects.get_or_create(name='GroupManager')

# states
pending, created = State.objects.get_or_create(name="Pending", workflow=SubscriptionRequestWorkflow)
accepted, created = State.objects.get_or_create(name="Accepted", workflow=SubscriptionRequestWorkflow)
refused, created = State.objects.get_or_create(name="Refused", workflow=SubscriptionRequestWorkflow)

# permissions
can_accept, created = Permission.objects.get_or_create(name="Can accept subscription", codename="can_accept_subscription")
can_refuse, created = Permission.objects.get_or_create(name="Can refuse subscription", codename="can_refuse_subscription")

# transitions
accept_subscription, created = Transition.objects.get_or_create(name="Accept subscription", workflow=SubscriptionRequestWorkflow, destination=accepted)
refuse_subscription, created = Transition.objects.get_or_create(name="Refuse subscription", workflow=SubscriptionRequestWorkflow, destination=refused)

pending.transitions.add(accept_subscription)
pending.transitions.add(refuse_subscription)
accepted.transitions.add(refuse_subscription)
refused.transitions.add(accept_subscription)

# initial state
SubscriptionRequestWorkflow.initial_state = pending

# Add all permissions which are managed by the workflow
WorkflowPermissionRelation.objects.get_or_create(workflow=SubscriptionRequestWorkflow, permission=can_accept)
WorkflowPermissionRelation.objects.get_or_create(workflow=SubscriptionRequestWorkflow, permission=can_refuse)

# Add permissions for the single states
StatePermissionRelation.objects.get_or_create(state=pending, permission=can_accept, role=group_manager)
StatePermissionRelation.objects.get_or_create(state=pending, permission=can_refuse, role=group_manager)
StatePermissionRelation.objects.get_or_create(state=refused, permission=can_accept, role=group_manager)
StatePermissionRelation.objects.get_or_create(state=accepted, permission=can_refuse, role=group_manager)

SubscriptionRequestWorkflow.save(force_update=True)
