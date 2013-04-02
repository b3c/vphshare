# Create your views here.
from django.db.models import ObjectDoesNotExist
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.admin.models import User
from workflows.utils import get_state, set_workflow, set_state, do_transition
from permissions.utils import add_local_role
from config import *
from models import SubscriptionRequest, Study, Institution, AuditLog, VPHShareSmartGroup
from forms import StudyForm, InstitutionForm


def get_group_by_name(name):
    try:
        group = Institution.objects.get(name=name)
    except ObjectDoesNotExist:
        try:
            group = Study.objects.get(name=name)
        except ObjectDoesNotExist:
            group = VPHShareSmartGroup.objects.get(name=name)

    return group


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
    

def list_groups(request):
    """
     Return a views of all available institutions and groups
    """

    temp_fix_institution_managers()

    institutions = []
    user_institutions = []
    other_institutions = []

    user_groups = []
    other_groups = []

    pending_institutions = []

    for institution in Institution.objects.all():
        state = get_state(institution)
        if state is None or state.name == 'Accepted':
            institutions.append(institution)
        else:
            pending_institutions.append(institution)

    if not request.user.is_authenticated():
        other_institutions = institutions
        other_groups = VPHShareSmartGroup.objects.filter(active=True)
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

        for vphgroup in VPHShareSmartGroup.objects.filter(active=True):
            join_group_subscription(request.user, vphgroup)
            if request.user in vphgroup.user_set.all() or request.user in vphgroup.managers.all():
                user_groups.append(vphgroup)
            else:
                other_groups.append(vphgroup)

    return render_to_response(
        'scs_groups/institutions.html',
        {'user_institutions': user_institutions,
         'pending_institutions': pending_institutions,
         'other_institutions': other_institutions,
         'other_groups': other_groups,
         'user_groups': user_groups},
        RequestContext(request)
    )


def manage_subscription(request):
    """
        accept or refuse subscription_pending subscription
    """

    if request.method == 'POST':
        group_name = request.POST['group']
        group = get_group_by_name(group_name)
        user_name = request.POST['user']
        user = User.objects.get(username=user_name)
        subscription = SubscriptionRequest.objects.get(user=user, group=group)

        if request.POST['operation'] == 'accept':
            if do_transition(subscription, subscription_accept_subscription, request.user):
                group.user_set.add(user)
        else:
            do_transition(subscription, subscription_refuse_subscription, request.user)

    return redirect('/groups')


def manage_group_request(request):
    """
        accept or refuse an instution request
    """

    if request.method == 'POST':
        group_name = request.POST['group']
        group = get_group_by_name(group_name)

        if request.POST['operation'] == 'accept':
            do_transition(group, group_accept_subscription, request.user)
        else:
            do_transition(group, group_refuse_subscription, request.user)

    return redirect('/groups')


def subscribe(request):
    """
        create a subscription_pending subscription to an institution
    """

    if request.method == 'POST':
        group_name = request.POST['group']
        group = get_group_by_name(group_name)
        subscription = SubscriptionRequest(user=request.user, group=group)
        subscription.save()
        set_workflow(subscription, SubscriptionRequestWorkflow)
        set_state(subscription, subscription_pending)

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


def create_institution(request):
    """
        submit a request to create an institution
    """

    if request.method == 'POST':
        form = InstitutionForm(request.POST)

        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            set_workflow(group, GroupRequestWorkflow)
            set_state(group, group_pending)
            return redirect('/groups')
        else:
            return render_to_response(
                'scs_groups/createinstitution.html',
                {'form': form},
                RequestContext(request)
            )
    else:

        form = InstitutionForm(initial={'managers': [request.user]})

        return render_to_response(
            'scs_groups/createinstitution.html',
            {'form': form},
            RequestContext(request)
        )


def api_help(request):
    return render_to_response(
    'scs_groups/api.html',
    RequestContext(request)
    )