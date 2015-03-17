__author__ = 'mark'

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from convert import views

urlpatterns = [
    url(r'^workbook/$', views.workbooks_list),
    url(r'^workbook/(?P<pk>[0-9]+)$', views.workbook_detail),
    url(r'^worksheet/(?P<pk>[0-9]+)$', views.worksheet_detail),
]

urlpatterns = format_suffix_patterns(urlpatterns)