from django.contrib import admin
from django.contrib.admin import sites
from django.contrib.admin.apps import AdminConfig
from icecream import ic


class MyAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        all_list = super().get_app_list(request)
        # reorder the app list as you like
        users_app = None
        for i in all_list:
            if i["app_label"].lower() == "users":
                users_app = all_list.pop(all_list.index(i))
                break
        if users_app:
            all_list.insert(0, users_app)
        return all_list


class MyAdminConfig(AdminConfig):
    default_site = "core.apps.MyAdminSite"
