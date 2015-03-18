__author__ = 'mark'

from django.conf.urls import url, include
from rest_framework import routers
from convert import views

router = routers.DefaultRouter
router.register(r'file', views.FileViewSet)
router.register(r'file/upload', views.FileUploadView)
router.register(r'conversion', views.ConversionViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth', include('rest_framework.urls', namespace='rest_framework'))
]