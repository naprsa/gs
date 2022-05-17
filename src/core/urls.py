from django.contrib import admin
import debug_toolbar
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from users.api.v1.api import TokenLogin
from .settings.common.apple import apple_verification
from .views import terms_of_use_view, privacy_policy_view


admin.site.site_header = "Gift Solitaire"
admin.site.index_title = "Gift Solitaire Administration"
admin.site.site_title = "Gift Solitaire"

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("apple-app-site-association", apple_verification),
    path("admin", admin.site.urls),
    path("terms-of-use", terms_of_use_view),
    path("privacy-policy", privacy_policy_view),
    path("api/auth/token/login/", TokenLogin.as_view()),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.authtoken")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/print/", include("print.urls", namespace="print")),
    path("api/v1/decks/", include("game.api.v1.urls", namespace="api-game-v1")),
    path("api/v2/decks/", include("game.api.v2.urls", namespace="api-game-v2")),
    path("api/v1/orders/", include("orders.api.v1.urls", namespace="api-orders-v1")),
    path("api/v2/orders/", include("orders.api.v2.urls", namespace="api-orders-v2")),
    path("api/v1/office/", include("office.api.v1.urls", namespace="api-office-v1")),
    path("api/v1/print/", include("print.api.v1.urls", namespace="api-print-v1")),
    path("api/v1/users/", include("users.api.v1.urls", namespace="api-users-v1")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path("__debug__", include(debug_toolbar.urls))]


# in prod need to switch off swagger urls!!!
urlpatterns += [
    url(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    url(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    url(
        r"^redoc/$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
