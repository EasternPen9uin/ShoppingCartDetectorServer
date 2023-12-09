"""
URL configuration for SCD_Backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from auth_app.views import func_login, func_logout, func_change_password, func_reset_password, func_make_new_user, func_get_all_user, func_who_am_i
from yolo.views import getPic, getNextPic, getPrevPic, searchPage, deleteImage 
from rest_framework import routers
router = routers.SimpleRouter()

urlpatterns = [
    path('api/auth/login', func_login),
    path('api/auth/logout', func_logout),
    path('api/auth/changepw', func_change_password),
    path('api/auth/resetpw', func_reset_password),
    path('api/auth/makeuser', func_make_new_user),
    path('api/auth/getalluser', func_get_all_user),
    path('api/auth/getme', func_who_am_i),
    path('api/yolo/getpic', getPic),
    path('api/yolo/getnextpic', getNextPic),
    path('api/yolo/getprevpic', getPrevPic),
    path('api/yolo/searchpage', searchPage),
    path('api/yolo/deleteimage', deleteImage),
]