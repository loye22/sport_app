"""
URL configuration for apiapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views




dashboard_patterns = [
    # ── Auth ──────────────────────────────────────────────
    path("login/",  views.login_view,  name="login"),
    path("logout/", views.logout_view, name="logout"),
 
    # ── Overview ──────────────────────────────────────────
    path("",         views.overview, name="overview"),
    path("overview/", views.overview, name="overview"),   # alias
 
    # ── Users ─────────────────────────────────────────────
    path("users/",                views.users,       name="users"),
    path("users/<uuid:pk>/",      views.user_detail, name="user_detail"),
    path("users/<uuid:pk>/delete/", views.user_delete, name="user_delete"),
 
    # ── Events ────────────────────────────────────────────
    path("events/",                      views.events,        name="events"),
    path("events/<uuid:pk>/",            views.event_detail,  name="event_detail"),
    path("events/<uuid:pk>/delete/",     views.event_delete,  name="event_delete"),
    path("events/<uuid:pk>/cancel/",     views.event_cancel,  name="event_cancel"),
 
    # ── Posts ─────────────────────────────────────────────
    path("posts/",                      views.posts,          name="posts"),
    path("posts/<uuid:pk>/",            views.post_detail,    name="post_detail"),
    path("posts/<uuid:pk>/delete/",     views.post_delete,    name="post_delete"),
    path("posts/<uuid:pk>/unpublish/",  views.post_unpublish, name="post_unpublish"),

 
    # ── Reports ───────────────────────────────────────────
    path("reports/",                               views.reports,              name="reports"),
    path("reports/post/<uuid:pk>/resolve/",        views.resolve_post_report,  name="resolve_post_report"),
    path("reports/repost/<uuid:pk>/resolve/",      views.resolve_repost_report, name="resolve_repost_report"),
 
    # ── Hashtags ──────────────────────────────────────────
    path("hashtags/",                  views.hashtags,       name="hashtags"),
    path("hashtags/create/",           views.hashtag_create, name="hashtag_create"),
    path("hashtags/<uuid:pk>/delete/", views.hashtag_delete, name="hashtag_delete"),
 
    # ── Categories ────────────────────────────────────────
    path("categories/",                   views.categories,      name="categories"),
    path("categories/create/",            views.category_create,  name="category_create"),
    path("categories/<uuid:pk>/delete/",  views.category_delete, name="category_delete"),

 
    # ── Delete Requests ───────────────────────────────────
    path("delete-requests/",               views.delete_requests,      name="delete_requests"),
    path("delete-requests/<uuid:pk>/process/", views.process_delete_request, name="process_delete_request"),
 
    # ── Additional Options ────────────────────────────────
    path("additional-options/",                views.additional_options,       name="additional_options"),
    path("additional-options/<uuid:pk>/",       views.additional_option_detail, name="additional_option_detail"),
    path("additional-options/<uuid:pk>/delete/", views.additional_option_delete, name="additional_option_delete"),
 
    # ── Venues ────────────────────────────────────────────
    path("venues/",                 views.venues,       name="venues"),
    path("venues/<uuid:pk>/delete/", views.venue_delete, name="venue_delete"),
 
    # ── HTMX partials ─────────────────────────────────────
    path("htmx/user/<uuid:pk>/",  views.htmx_user_row,   name="htmx_user_row"),
    path("htmx/event/<uuid:pk>/", views.htmx_event_card, name="htmx_event_card"),
]

urlpatterns = [
   
    path('', views.home, name='home'),  # Add the root URL pattern
     path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # Add the URL pattern for the api app
    path('accounts/', include('django.contrib.auth.urls')),
    path("", include((dashboard_patterns, "dashboard"), namespace="dashboard")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
