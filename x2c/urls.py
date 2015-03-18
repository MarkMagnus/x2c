from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'')

urlpatterns = patterns('',
    url(r'^convert/', include('convert.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
