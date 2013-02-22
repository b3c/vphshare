# Create your views here.
from django.db.models import ObjectDoesNotExist
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.admin.models import User
from workflows.utils import get_state, set_workflow, set_state, do_transition
from permissions.utils import add_local_role
from config import group_manager, SubscriptionRequestWorkflow, pending, accepted, refused, accept_subscription, refuse_subscription
from models import SubscriptionRequest, Study, Institution, AuditLog
from forms import StudyForm


def temp_fix_institution_managers():
    """
        temporary method to grant GroupManager role to institution manager users
    """

    institutions = Institution.objects.all()

    for institution in institutions:
        for manager in institution.managers.all():
            add_local_role(institution, manager, group_manager)
            institution.user_set.add(manager)
            for study in institution.study_set.all():
                add_local_role(study, manager, group_manager)
                study.principals.add(manager)


def join_group_subscription(user, group):
    """
    add to the group object all information about subscriptions
    """
    group.pending_subscriptions = []
    subscriptions = SubscriptionRequest.objects.filter(group=group.pk)
    for subscription in subscriptions:
        if get_state(subscription).name == 'Pending':
            group.pending_subscriptions.append(subscription)
    try:
        subscription = SubscriptionRequest.objects.get(group=group.pk, user=user)
    except ObjectDoesNotExist:
        subscription = None
    if subscription and get_state(subscription).name == 'Pending':
        group.is_subscription_pending = True
    elif subscription and get_state(subscription).name == 'Refused':
        group.is_subscription_refused = True
    

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
            join_group_subscription(request.user, institution)
            if request.user in institution.user_set.all() or request.user in institution.managers.all():
                user_institutions.append(institution)
            else:
                other_institutions.append(institution)
            institution.studies = institution.study_set.all()
            for study in institution.studies:
                join_group_subscription(request.user, study)

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
        group_name = request.POST['group']
        try:
            group = Institution.objects.get(name=group_name)
        except ObjectDoesNotExist:
            group = Study.objects.get(name=group_name)
        user_name = request.POST['user']
        user = User.objects.get(username=user_name)
        subscription = SubscriptionRequest.objects.get(user=user, group=group)

        if request.POST['operation'] == 'accept':
            if do_transition(subscription, accept_subscription, request.user):
                group.user_set.add(user)
        else:
            do_transition(subscription, refuse_subscription, request.user)

    return redirect('/groups')


def subscribe(request):
    """
        create a pending subscription to an institution
    """

    if request.method == 'POST':
        group_name = request.POST['group']
        try:
            group = Institution.objects.get(name=group_name)
        except ObjectDoesNotExist:
            group = Study.objects.get(name=group_name)
        subscription = SubscriptionRequest(user=request.user, group=group)
        subscription.save()
        set_workflow(subscription, SubscriptionRequestWorkflow)
        set_state(subscription, pending)

    return redirect('/groups')


def create_study(request):
    """
        create a new study for the given instution
    """

    if request.method == 'POST':
        form = StudyForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('/groups')
        else:
            institution = Institution.objects.get(pk=request.POST['institution'])
            return render_to_response(
                'scs_groups/createstudy.html',
                {'form': form,
                 'institution': institution},
                RequestContext(request)
            )
    else:
        institution_pk = request.GET['institution']

        institution = Institution.objects.get(pk=institution_pk)
        if not request.user in institution.managers.all():
            return redirect('/groups')

        form = StudyForm(initial={'institution': institution_pk})
        form.Meta.model.institution = institution
        return render_to_response(
            'scs_groups/createstudy.html',
            {'form': form,
             'institution': institution},
            RequestContext(request)
        )