# Create your views here.
from django.db.models import ObjectDoesNotExist
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.admin.models import User
from workflows.utils import get_state, set_workflow, set_state, do_transition
from permissions.utils import add_local_role
from config import group_manager, SubscriptionRequestWorkflow, pending, accepted, refused, accept_subscription, refuse_subscription
from models import SubscriptionRequest, Study, Institution, AuditLog


def temp_fix_institution_managers():
    """
        temporary method to grant GroupManager role to institution manager users
    """

    institutions = Institution.objects.all()

    for institution in institutions:
        for manager in institution.managers.all():
            add_local_role(institution, manager, group_manager)


def list_institutions(request):
    """
     Return a views of all available institutions
    """

    temp_fix_institution_managers()

    institutions = Institution.objects.all()
    user_institutions = []
    other_institutions = []

    if not request.user.is_authenticated():
        other_institutions = institutions
    else:
        for institution in institutions:
            institution.subscribers = institution.user_set.all()
            if request.user in institution.managers.all():
                institution.is_manager = True
                institution.pending_subscriptions = []
                subscriptions = SubscriptionRequest.objects.filter(group=institution.pk)
                for subscription in subscriptions:
                    if get_state(subscription).name == 'Pending':
                        institution.pending_subscriptions.append(subscription)

            if institution.name in request.user.groups.all() or getattr(institution, 'is_manager', False):
                # if has_local_role(request.user, group_manager, institution):
                #    institution.ismanager = True
                user_institutions.append(institution)
            else:
                try:
                    subscription = SubscriptionRequest.objects.get(group=institution.pk, user=request.user)
                except ObjectDoesNotExist:
                    subscription = None
                if subscription and get_state(subscription).name == 'Pending':
                    institution.is_subscription_pending = True
                elif subscription and get_state(subscription).name == 'Refused':
                    institution.is_subscription_refused = True
                other_institutions.append(institution)

    return render_to_response(
        'scs_groups/institutions.html',
        {'user_institutions': user_institutions,
         'other_institutions': other_institutions},
        RequestContext(request)
    )


def manage_subscription(request):
    """
        accept or refuse pending subscription
    """

    if request.method == 'POST':
        institution_name = request.POST['institution']
        institution = Institution.objects.get(name=institution_name)
        user_name = request.POST['user']
        user = User.objects.get(username=user_name)
        subscription = SubscriptionRequest(user=user, group=institution)

        if request.POST['operation'] == 'accept':
            if do_transition(subscription, accept_subscription, request.user):
                institution.user_set.add(user)
        else:
            do_transition(subscription, refuse_subscription, request.user)

    return redirect('/groups')


def subscribe_to_institution(request):
    """
        create a pending subscription to an institution
    """

    if request.method == 'POST':
        institution_name = request.POST['institution']
        institution = Institution.objects.get(name=institution_name)
        subscription = SubscriptionRequest(user=request.user, group=institution)
        subscription.save()
        set_workflow(subscription, SubscriptionRequestWorkflow)
        set_state(subscription, pending)

    return redirect('/groups')
