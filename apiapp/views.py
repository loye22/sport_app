# dashboard/views.py
"""
SportSphere Admin Dashboard — Views
====================================
Role hierarchy:
  super_admin       → full access
  moderator         → Posts, Reports, Comments
  event_manager     → Events, Venues, AdditionalOptions
  content_moderator → Posts, Hashtags, Categories
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg, Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

# ─── adjust this import to match your actual app label ───────────────────────
from api.models import (  # noqa – replace "core" with your real app name
    AdditionalOption,
    Category,
    DeleteRequest,
    Event,
    Hashtag,
    Post,
    Repost,
    Review,
    UserProfile,
    Venue,
)


# ─────────────────────────────────────────────────────────────────────────────
# ROLE UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

ROLE_CHOICES = (
    ("super_admin", "Super Admin"),
    ("moderator", "Moderator"),
    ("event_manager", "Event Manager"),
    ("content_moderator", "Content Moderator"),
)

# Map each role to a set of permission keys it holds
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "super_admin": {
        "can_view_users",
        "can_edit_users",
        "can_delete_users",
        "can_view_events",
        "can_edit_events",
        "can_delete_events",
        "can_view_posts",
        "can_edit_posts",
        "can_delete_posts",
        "can_view_reports",
        "can_resolve_reports",
        "can_view_hashtags",
        "can_edit_hashtags",
        "can_delete_hashtags",
        "can_view_categories",
        "can_edit_categories",
        "can_delete_categories",
        "can_view_delete_requests",
        "can_approve_delete_requests",
        "can_view_additional_options",
        "can_edit_additional_options",
        "can_delete_additional_options",
        "can_view_venues",
        "can_edit_venues",
        "can_delete_venues",
    },
    "moderator": {
        "can_view_posts",
        "can_edit_posts",
        "can_delete_posts",
        "can_view_reports",
        "can_resolve_reports",
    },
    "event_manager": {
        "can_view_events",
        "can_edit_events",
        "can_delete_events",
        "can_view_venues",
        "can_edit_venues",
        "can_delete_venues",
        "can_view_additional_options",
        "can_edit_additional_options",
        "can_delete_additional_options",
    },
    "content_moderator": {
        "can_view_posts",
        "can_edit_posts",
        "can_view_hashtags",
        "can_edit_hashtags",
        "can_delete_hashtags",
        "can_view_categories",
        "can_edit_categories",
    },
}

# Every authenticated staff member can always see the overview
_ALWAYS_VISIBLE = {"can_view_overview"}


def get_dashboard_role(user) -> str | None:
    """
    Return the role string for a staff user, or None if not authorised.
    Reads from user.userprofile.dashboard_role  (add this CharField to UserProfile).
    Falls back to 'super_admin' for Django superusers.
    """
    if not user.is_authenticated or not user.is_staff:
        return None
    if user.is_superuser:
        return "super_admin"
    try:
        return user.userprofile.dashboard_role  # type: ignore[attr-defined]
    except Exception:
        return None


def get_perms_map(role: str | None) -> dict[str, bool]:
    """Return a dict of all known permission keys mapped to True/False."""
    granted = ROLE_PERMISSIONS.get(role or "", set()) | _ALWAYS_VISIBLE
    all_keys = set().union(*ROLE_PERMISSIONS.values()) | _ALWAYS_VISIBLE
    return {k: (k in granted) for k in all_keys}


# ─────────────────────────────────────────────────────────────────────────────
# DECORATORS
# ─────────────────────────────────────────────────────────────────────────────


def staff_required(view_func):
    """Redirect non-staff or unauthenticated users to the login page."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("dashboard:login")
        role = get_dashboard_role(request.user)
        if role is None:
            messages.error(request, "You do not have permission to access the dashboard.")
            logout(request)
            return redirect("dashboard:login")
        return view_func(request, *args, **kwargs)

    return wrapper


def permission_required_dashboard(perm_key: str):
    """
    Decorator that checks a dashboard-level permission key.
    Usage:  @permission_required_dashboard('can_delete_events')
    """

    def decorator(view_func):
        @wraps(view_func)
        @staff_required
        def wrapper(request, *args, **kwargs):
            role = get_dashboard_role(request.user)
            perms = get_perms_map(role)
            if not perms.get(perm_key):
                messages.error(request, "You don't have permission to perform this action.")
                return redirect("dashboard:overview")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


# ─────────────────────────────────────────────────────────────────────────────
# SHARED CONTEXT HELPER
# ─────────────────────────────────────────────────────────────────────────────


def base_context(request, active_section: str = "overview") -> dict:
    """Context variables injected into every dashboard template."""
    role = get_dashboard_role(request.user)
    role_display = dict(ROLE_CHOICES).get(role or "", "Unknown")

    return {
        "active_section": active_section,
        "dashboard_role": role_display,
        "perms_map": get_perms_map(role),
        # Badge counts shown in sidebar
        "pending_reports_count": Post.objects.filter(is_reported=True).count()
        + Repost.objects.filter(is_reported=True).count(),
        "pending_delete_count": DeleteRequest.objects.filter(status="pending").count(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# AUTH VIEWS
# ─────────────────────────────────────────────────────────────────────────────


def login_view(request):
    """Custom login — only allows is_staff users."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard:overview")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            role = get_dashboard_role(user)
            if role is None:
                messages.error(request, "Your account is not authorised to access the admin dashboard.")
            else:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                return redirect(request.GET.get("next") or "dashboard:overview")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "registration/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("dashboard:login")


# ─────────────────────────────────────────────────────────────────────────────
# OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────


@staff_required
def overview(request):
    ctx = base_context(request, "overview")
    ctx.update(
        {
            "total_users": UserProfile.objects.count(),
            "active_events": Event.objects.filter(status="Available").count(),
            "total_posts": Post.objects.count(),
            "avg_rating": Review.objects.aggregate(avg=Avg("rating"))["avg"] or 0,
            "recent_events": Event.objects.select_related("host", "category")
            .order_by("-created_at")[:6],
            "users_this_week": UserProfile.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
            "events_today": Event.objects.filter(date=timezone.now().date()).count(),
        }
    )
    return render(request, "dashboard/overview.html", ctx)


# ─────────────────────────────────────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────────────────────────────────────


@staff_required
@permission_required_dashboard("can_view_users")
def users(request):
    ctx = base_context(request, "users")

    search_q = request.GET.get("q", "").strip()
    gender_f = request.GET.get("gender", "")
    qs = UserProfile.objects.select_related("user").order_by("-created_at")

    if search_q:
        qs = qs.filter(
            Q(full_name__icontains=search_q)
            | Q(email__icontains=search_q)
            | Q(phone_number__icontains=search_q)
        )
    if gender_f:
        qs = qs.filter(gender=gender_f)

    ctx["users"] = qs
    ctx["search_q"] = search_q
    ctx["gender_f"] = gender_f
    return render(request, "dashboard/users.html", ctx)


@staff_required
@permission_required_dashboard("can_view_users")
def user_detail(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    ctx = base_context(request, "users")
    ctx["profile"] = profile
    ctx["hosted_events"] = Event.objects.filter(host=profile).order_by("-created_at")[:10]
    ctx["reviews"] = Review.objects.filter(host=profile).select_related("reviewer")
    return render(request, "dashboard/user_detail.html", ctx)


@staff_required
@permission_required_dashboard("can_delete_users")
@require_POST
def user_delete(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    username = profile.full_name
    profile.user.delete()  # Cascade deletes the profile
    messages.success(request, f"User '{username}' has been deleted.")
    return redirect("dashboard:users")


# ─────────────────────────────────────────────────────────────────────────────
# EVENTS
# ─────────────────────────────────────────────────────────────────────────────


@staff_required
@permission_required_dashboard("can_view_events")
def events(request):
    ctx = base_context(request, "events")

    search_q = request.GET.get("q", "").strip()
    status_f = request.GET.get("status", "")
    city_f = request.GET.get("city", "")

    qs = Event.objects.select_related("host", "category", "Venue").order_by("-created_at")
    if search_q:
        qs = qs.filter(Q(title__icontains=search_q) | Q(host__full_name__icontains=search_q))
    if status_f:
        qs = qs.filter(status=status_f)
    if city_f:
        qs = qs.filter(city=city_f)

    ctx["events"] = qs
    ctx["status_choices"] = Event.STATUS_CHOICES
    ctx["city_choices"] = Event.CITY_CHOICES
    ctx["search_q"] = search_q
    ctx["status_f"] = status_f
    ctx["city_f"] = city_f
    return render(request, "dashboard/events.html", ctx)


@staff_required
@permission_required_dashboard("can_view_events")
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    ctx = base_context(request, "events")
    ctx["event"] = event
    return render(request, "dashboard/event_detail.html", ctx)


@staff_required
@permission_required_dashboard("can_delete_events")
@require_POST
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    title = event.title
    event.delete()
    messages.success(request, f"Event '{title}' has been deleted.")
    return redirect("dashboard:events")


@staff_required
@permission_required_dashboard("can_edit_events")
@require_POST
def event_cancel(request, pk):
    event = get_object_or_404(Event, pk=pk)
    reason = request.POST.get("reason", "Cancelled by admin")
    event.status = "Cancelled"
    event.cancellation_reason = reason
    event.save()
    messages.success(request, f"Event '{event.title}' has been cancelled.")
    return redirect("dashboard:events")


# ─────────────────────────────────────────────────────────────────────────────
# POSTS
# ─────────────────────────────────────────────────────────────────────────────


@staff_required
@permission_required_dashboard("can_view_posts")
def posts(request):
    ctx = base_context(request, "posts")

    search_q = request.GET.get("q", "").strip()
    reported_f = request.GET.get("reported", "")

    qs = Post.objects.select_related("created_by", "category").order_by("-created_at")
    if search_q:
        qs = qs.filter(
            Q(activity_name__icontains=search_q) | Q(created_by__full_name__icontains=search_q)
        )
    if reported_f == "1":
        qs = qs.filter(is_reported=True)

    ctx["posts"] = qs
    ctx["search_q"] = search_q
    ctx["reported_f"] = reported_f
    return render(request, "dashboard/posts.html", ctx)


@staff_required
@permission_required_dashboard("can_view_posts")
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    ctx = base_context(request, "posts")
    ctx["post"] = post
    ctx["comments"] = post.comments.select_related("created_by").order_by("-created_at")
    return render(request, "dashboard/post_detail.html", ctx)


@staff_required

@permission_required_dashboard("can_delete_posts")
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    name = post.activity_name
    post.delete()
    messages.success(request, f"Post '{name}' has been deleted.")
    return redirect("dashboard:posts")


@staff_required
@permission_required_dashboard("can_edit_posts")
@require_POST
def post_unpublish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.is_published = False
    post.save()
    messages.success(request, f"Post '{post.activity_name}' has been unpublished.")
    return redirect("dashboard:posts")


# ─────────────────────────────────────────────────────────────────────────────
# REPORTS
# ─────────────────────────────────────────────────────────────────────────────


@staff_required
@permission_required_dashboard("can_view_reports")
def reports(request):
    ctx = base_context(request, "reports")
    ctx["reported_posts"] = Post.objects.filter(is_reported=True).select_related(
        "created_by", "reported_by"
    ).order_by("-report_date")
    ctx["reported_reposts"] = Repost.objects.filter(is_reported=True).select_related(
        "user", "reported_by", "original_post"
    ).order_by("-report_date")
    return render(request, "dashboard/reports.html", ctx)


@staff_required
@permission_required_dashboard("can_resolve_reports")
@require_POST
def resolve_post_report(request, pk):
    post = get_object_or_404(Post, pk=pk, is_reported=True)
    action = request.POST.get("action")  # "dismiss" or "remove"
    if action == "dismiss":
        post.is_reported = False
        post.report_reason = None
        post.reported_by = None
        post.report_date = None
        post.save()
        messages.success(request, "Report dismissed — post retained.")
    elif action == "remove":
        name = post.activity_name
        post.delete()
        messages.success(request, f"Post '{name}' removed due to report.")
    return redirect("dashboard:reports")


@staff_required
@permission_required_dashboard("can_resolve_reports")
@require_POST
def resolve_repost_report(request, pk):
    repost = get_object_or_404(Repost, pk=pk, is_reported=True)
    action = request.POST.get("action")
    if action == "dismiss":
        repost.is_reported = False
        repost.report_reason = None
        repost.reported_by = None
        repost.report_date = None
        repost.save()
        messages.success(request, "Report dismissed — repost retained.")
    elif action == "remove":
        repost.delete()
        messages.success(request, "Repost removed due to report.")
    return redirect("dashboard:reports")


# ─────────────────────────────────────────────────────────────────────────────
# HASHTAGS
# ─────────────────────────────────────────────────────────────────────────────


@staff_required
@permission_required_dashboard("can_view_hashtags")
def hashtags(request):
    ctx = base_context(request, "hashtags")
    qs = Hashtag.objects.annotate(post_count=Count("posts"), repost_count=Count("reposts")).order_by(
        "-post_count"
    )
    ctx["hashtags"] = qs
    return render(request, "dashboard/hashtags.html", ctx)


@staff_required
@permission_required_dashboard("can_edit_hashtags")
@require_POST
def hashtag_create(request):
    name = request.POST.get("name", "").strip().lstrip("#")
    if not name:
        messages.error(request, "Hashtag name cannot be empty.")
        return redirect("dashboard:hashtags")
    _, created = Hashtag.objects.get_or_create(name=name)
    if created:
        messages.success(request, f"Hashtag #{name} created.")
    else:
        messages.warning(request, f"Hashtag #{name} already exists.")
    return redirect("dashboard:hashtags")


@staff_required
@permission_required_dashboard("can_delete_hashtags")
@require_POST
def hashtag_delete(request, pk):
    tag = get_object_or_404(Hashtag, pk=pk)
    name = tag.name
    tag.delete()
    messages.success(request, f"Hashtag #{name} deleted.")
    return redirect("dashboard:hashtags")


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────────────────────────────────────────────


@staff_required
@permission_required_dashboard("can_view_categories")
def categories(request):
    ctx = base_context(request, "categories")
    ctx["categories"] = Category.objects.annotate(
        event_count=Count("event"), venue_count=Count("venue")
    ).order_by("name")
    return render(request, "dashboard/categories.html", ctx)


@staff_required
@permission_required_dashboard("can_edit_categories")
@require_POST
def category_create(request):
    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "Category name cannot be empty.")
        return redirect("dashboard:categories")

    if Category.objects.filter(name__iexact=name).exists():
        messages.warning(request, f"Category '{name}' already exists.")
        return redirect("dashboard:categories")

    image_file = request.FILES.get("image")
    if not image_file:
        from django.core.files.base import ContentFile
        from PIL import Image
        import io

        img = Image.new('RGB', (200, 200), color='#FBBF24')
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        image_file = ContentFile(img_io.getvalue(), name=f"{name.lower().replace(' ', '_')}_default.png")

    try:
        cat = Category.objects.create(name=name, image=image_file)
        messages.success(request, f"Category '{cat.name}' created successfully.")
    except Exception as e:
        messages.error(request, f"Failed to create category: {str(e)}")

    return redirect("dashboard:categories")



@staff_required
@permission_required_dashboard("can_delete_categories")
@require_POST
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    name = cat.name
    try:
        cat.delete()
        messages.success(request, f"Category '{name}' deleted.")
    except Exception:
        messages.error(request, f"Cannot delete '{name}' — it is linked to existing events or venues.")
    return redirect("dashboard:categories")


# ─────────────────────────────────────────────────────────────────────────────
# DELETE REQUESTS
# ─────────────────────────────────────────────────────────────────────────────


@staff_required
@permission_required_dashboard("can_view_delete_requests")
def delete_requests(request):
    ctx = base_context(request, "delete_requests")
    status_f = request.GET.get("status", "pending")
    qs = DeleteRequest.objects.select_related("user_profile").order_by("-created_at")
    if status_f:
        qs = qs.filter(status=status_f)
    ctx["delete_requests"] = qs
    ctx["status_f"] = status_f
    ctx["status_choices"] = DeleteRequest.STATUS_CHOICES
    return render(request, "dashboard/delete_requests.html", ctx)



@staff_required
@permission_required_dashboard("can_approve_delete_requests")
@require_POST
def process_delete_request(request, pk):
    dr = get_object_or_404(DeleteRequest, pk=pk)
    action = request.POST.get("action")  # "approve" or "reject"
    admin_note = request.POST.get("admin_notes", "")

    if action == "approve":
        dr.status = "approved"
        dr.processed_at = timezone.now()
        dr.admin_notes = admin_note
        dr.save()
        # Removal of the actual user account is now omitted.
        # The delete request is simply marked as approved.
        messages.success(request, f"Delete request for '{dr.user_profile.full_name}' approved (user account was not deleted).")
    elif action == "reject":
        dr.status = "rejected"
        dr.processed_at = timezone.now()
        dr.admin_notes = admin_note
        dr.save()
        messages.success(request, f"Delete request for '{dr.user_profile.full_name}' rejected.")
    else:
        messages.error(request, "Invalid action.")

    return redirect("dashboard:delete_requests")

# @staff_required
# @permission_required_dashboard("can_approve_delete_requests")
# @require_POST
# def process_delete_request(request, pk):
#     dr = get_object_or_404(DeleteRequest, pk=pk)
#     action = request.POST.get("action")  # "approve" or "reject"
#     admin_note = request.POST.get("admin_notes", "")

#     if action == "approve":
#         dr.status = "approved"
#         dr.processed_at = timezone.now()
#         dr.admin_notes = admin_note
#         dr.save()
#         # Delete the actual user account
#         user = dr.user_profile.user
#         user.delete()
#         messages.success(request, f"Delete request approved — account for '{dr.user_profile.full_name}' removed.")
#     elif action == "reject":
#         dr.status = "rejected"
#         dr.processed_at = timezone.now()
#         dr.admin_notes = admin_note
#         dr.save()
#         messages.success(request, f"Delete request for '{dr.user_profile.full_name}' rejected.")
#     else:
#         messages.error(request, "Invalid action.")

#     return redirect("dashboard:delete_requests")


# ─────────────────────────────────────────────────────────────────────────────
# ADDITIONAL OPTIONS
# ─────────────────────────────────────────────────────────────────────────────


@staff_required
@permission_required_dashboard("can_view_additional_options")
def additional_options(request):
    ctx = base_context(request, "additional_options")
    qs = AdditionalOption.objects.select_related("event").order_by("type", "price")
    type_f = request.GET.get("type", "")
    if type_f:
        qs = qs.filter(type=type_f)
    ctx["options"] = qs
    ctx["type_choices"] = AdditionalOption.TYPE_CHOICES
    ctx["type_f"] = type_f
    return render(request, "dashboard/additional_options.html", ctx)


@staff_required
@permission_required_dashboard("can_view_additional_options")
def additional_option_detail(request, pk):
    opt = get_object_or_404(AdditionalOption.objects.select_related("event"), pk=pk)
    ctx = base_context(request, "additional_options")
    ctx["opt"] = opt
    return render(request, "dashboard/additional_option_detail.html", ctx)


@staff_required
@permission_required_dashboard("can_delete_additional_options")
@require_POST
def additional_option_delete(request, pk):
    opt = get_object_or_404(AdditionalOption, pk=pk)
    opt.delete()
    messages.success(request, "Additional option deleted.")
    return redirect("dashboard:additional_options")


# ─────────────────────────────────────────────────────────────────────────────
# VENUES
# ─────────────────────────────────────────────────────────────────────────────


@staff_required
@permission_required_dashboard("can_view_venues")
def venues(request):
    ctx = base_context(request, "venues")

    search_q = request.GET.get("q", "").strip()
    status_f = request.GET.get("status", "")

    qs = Venue.objects.select_related("created_by", "category").order_by("-created_at")
    if search_q:
        qs = qs.filter(Q(title__icontains=search_q) | Q(address__icontains=search_q))
    if status_f:
        qs = qs.filter(status=status_f)

    ctx["venues"] = qs
    ctx["status_choices"] = Venue.STATUS_CHOICES
    ctx["search_q"] = search_q
    ctx["status_f"] = status_f
    return render(request, "dashboard/venues.html", ctx)


@staff_required
@permission_required_dashboard("can_delete_venues")
@require_POST
def venue_delete(request, pk):
    venue = get_object_or_404(Venue, pk=pk)
    title = venue.title
    try:
        venue.delete()
        messages.success(request, f"Venue '{title}' deleted.")
    except Exception:
        messages.error(request, f"Cannot delete '{title}' — it is linked to existing events.")
    return redirect("dashboard:venues")


# ─────────────────────────────────────────────────────────────────────────────
# HTMX PARTIALS  (fast inline updates — no full page reload)
# ─────────────────────────────────────────────────────────────────────────────


@staff_required
def htmx_user_row(request, pk):
    """Return a single updated <tr> after an inline edit."""
    profile = get_object_or_404(UserProfile, pk=pk)
    return render(request, "dashboard/partials/user_row.html", {"profile": profile})


@staff_required
def htmx_event_card(request, pk):
    """Return a single updated event card."""
    event = get_object_or_404(Event, pk=pk)
    return render(request, "dashboard/partials/event_card.html", {"event": event})


# apiapp/views.py
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the home page!")