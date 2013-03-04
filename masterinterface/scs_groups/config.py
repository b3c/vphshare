from workflows.models import Workflow, State, Transition, WorkflowPermissionRelation, StatePermissionRelation
from permissions.models import Permission, Role

# GROUP SUBSCRIPTION WORKFLOW DEFINITION
SubscriptionRequestWorkflow, created = Workflow.objects.get_or_create(name="SubscriptionRequestWorkflow")

# roles
group_manager, created = Role.objects.get_or_create(name='GroupManager')

# states
subscription_pending, created = State.objects.get_or_create(name="Pending", workflow=SubscriptionRequestWorkflow)
subscription_accepted, created = State.objects.get_or_create(name="Accepted", workflow=SubscriptionRequestWorkflow)
subscription_refused, created = State.objects.get_or_create(name="Refused", workflow=SubscriptionRequestWorkflow)

# permissions
subscription_can_accept, created = Permission.objects.get_or_create(name="Can accept subscription", codename="can_accept_subscription")
subscription_can_refuse, created = Permission.objects.get_or_create(name="Can refuse subscription", codename="can_refuse_subscription")

# transitions
subscription_accept_subscription, created = Transition.objects.get_or_create(name="Accept subscription", workflow=SubscriptionRequestWorkflow, destination=subscription_accepted)
subscription_refuse_subscription, created = Transition.objects.get_or_create(name="Refuse subscription", workflow=SubscriptionRequestWorkflow, destination=subscription_refused)

subscription_pending.transitions.add(subscription_accept_subscription)
subscription_pending.transitions.add(subscription_refuse_subscription)
subscription_accepted.transitions.add(subscription_refuse_subscription)
subscription_refused.transitions.add(subscription_accept_subscription)

# initial state
SubscriptionRequestWorkflow.initial_state = subscription_pending

# Add all permissions which are managed by the workflow
WorkflowPermissionRelation.objects.get_or_create(workflow=SubscriptionRequestWorkflow, permission=subscription_can_accept)
WorkflowPermissionRelation.objects.get_or_create(workflow=SubscriptionRequestWorkflow, permission=subscription_can_refuse)

# Add permissions for the single states
StatePermissionRelation.objects.get_or_create(state=subscription_pending, permission=subscription_can_accept, role=group_manager)
StatePermissionRelation.objects.get_or_create(state=subscription_pending, permission=subscription_can_refuse, role=group_manager)
StatePermissionRelation.objects.get_or_create(state=subscription_refused, permission=subscription_can_accept, role=group_manager)
StatePermissionRelation.objects.get_or_create(state=subscription_accepted, permission=subscription_can_refuse, role=group_manager)

SubscriptionRequestWorkflow.save(force_update=True)

# GROUP/INSTITUTION WORKFLOW DEFINITION
GroupRequestWorkflow, created = Workflow.objects.get_or_create(name="GroupRequestWorkflow")

# states
group_pending, created = State.objects.get_or_create(name="Pending", workflow=GroupRequestWorkflow)
group_accepted, created = State.objects.get_or_create(name="Accepted", workflow=GroupRequestWorkflow)
group_refused, created = State.objects.get_or_create(name="Refused", workflow=GroupRequestWorkflow)

# transitions
group_accept_subscription, created = Transition.objects.get_or_create(name="Accept group request", workflow=GroupRequestWorkflow, destination=group_accepted)
group_refuse_subscription, created = Transition.objects.get_or_create(name="Refuse group request", workflow=GroupRequestWorkflow, destination=group_refused)

group_pending.transitions.add(group_accept_subscription)
group_pending.transitions.add(group_refuse_subscription)
group_accepted.transitions.add(group_refuse_subscription)
group_refused.transitions.add(group_accept_subscription)

# initial state
GroupRequestWorkflow.initial_state = group_pending

GroupRequestWorkflow.save(force_update=True)