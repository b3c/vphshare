from django.conf.urls import patterns, url, include
from django.contrib import admin
from masterinterface.scs.views import *
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns(
    'scs.views',
    url(r'^$', 'home' ),
    url(r'^about/$', TemplateView.as_view(template_name='scs/about.html')),
    url(r'^login/$', login , name='login'),
    url(r'^registration/$', registration , name='registration'),
    url(r'^reset_password_form/$', reset_password , name='registration'),
    url(r'^contacts/$', contacts ,  name='contacts'),
    url(r'^help/$', help ,  name='help'),
    url(r'^beta_programme/$', beta_programme,  name='beta_programme'),
    url(r'^data/$', data ,  name='data'),
    url(r'^data/search-data/$', search_data ,  name='search-data'),
    url(r'^data/upload-data/$', upload_data ,  name='upload-data'),
    url(r'^data/browse/$', browse_data_az, name="browse_data_az"),
    url(r'^workflows/search-workflow/$', search_workflow ,  name='search-workflow'),
    url(r'^profile/$',profile, name='profile'),
    url(r'^login-error/$', login_error , name='login_error'),
    url(r'^services/$', services ,name='services'),
    url(r'^test/$', test , name='test'),
    url(r'^400/$', page400 , name='bad_request'),
    url(r'^403/$', page403 , name='bad_request'),
    url(r'^404/$', page404 , name='bad_request'),
    url(r'^500/$', page500 , name='bad_request'),
    url(r'^users_admin/$', users_access_admin , name='users_access_admin'),
    url(r'^hide_notification/$', hide_notification, name="hide_notification"),
    # manage-data modal services
    url(r'^delete_tag/$', delete_tag_service,  name='delete-tag'),
    url(r'^update_tag/$', add_tag_service,  name='update-tag'),
    url(r'^update_description/$', edit_description_service,  name='update-description'),
    url(r'^search/$', search, name="search"),
    url(r'^search_results/$', search_service, name="search_results"),
    url(r'^help/api/$', 'api_help'),

)

