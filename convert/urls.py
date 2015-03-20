__author__ = 'mark'

from django.conf.urls import url, include
from rest_framework import routers
from convert.views import FileViewSet, ConversionViewSet, FileUploadView

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'file', FileViewSet)
router.register(r'conversion', ConversionViewSet)

urlpatterns = [url(r'^', include(router.urls)),
               url(r'upload', FileUploadView.as_view()),
               url(r'^api-auth', include('rest_framework.urls', namespace='rest_framework'))]
