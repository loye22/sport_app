from django.urls import path, include
from django.urls import path
from .views import IncreaseAllViewsAPIView, CreateNewCategoryView ,AddReviewView ,GetUserAverageReviewView ,GetUserAbsenceFlagView ,KickUserFromEventView ,CreateNoShowView ,GetUserEventProfileByIDView ,GetUserEventsByIDView ,GetUserPostsAndRepostsByIDView , GetUserInfoTabStatsByIDView ,GetUserProfileByIDView , PasswordResetRequestView , MarkNotificationsReadView, NotificationListView ,GetFollowersAndFollowingView, GetUserByIDView ,GetCurrentUserIDView ,SearchAPIView ,AllEventsView , UserCategoryStatsView , UserEventProfile ,UserRepostsView , UserPostsView , UserProfileTapDetailView ,ReportRepostView , LikeRepostCommentView ,AddRepostCommentView, LikeRepostView ,RepostCommentListView , RepostListView , AddRepostView , AddCommentView , LikeCommentView, CommentListView , CreatePostAPIView , UserProfileListAPIView , CreateVenueAPIView , MyHostedEventsView, CopyEventView ,CheckDateView,UserProfileDetailView , MyEventsView  ,HashtagListCreateView ,  VenueView,PostView , CommentView , ReportPostView , SignupView , LoginView , FollowUserView , LikePostView , EventView , JoinEventView , CancelJoinEventView , UnfollowUserView  , FileUploadView ,   CategoryListView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
       
            path('postss/', PostView.as_view(), name='post-list'),
            path('comment/', CommentView.as_view(), name='post-list'),
            path('report_post/', ReportPostView.as_view(), name='report-post'),
            path('signup/', SignupView.as_view(), name='signup'),
            path('login/', LoginView.as_view(), name='login'),
            path('follow_user/', FollowUserView.as_view(), name='follow-user'),
            path('unfollow_user/', UnfollowUserView.as_view(), name='unfollow-user'),
            path('like_post/', LikePostView.as_view(), name='like-post'),
            path('events/', EventView.as_view(), name='event-list'),
            path('join_event/', JoinEventView.as_view(), name='join-event'),
            path('cancel_join_event/', CancelJoinEventView.as_view(), name='cancel-join-event'),
            path('addrepost/', AddRepostView.as_view(), name='repost'),
            path('upload-file/', FileUploadView.as_view(), name='upload-file'),
            path('categories/', CategoryListView.as_view(), name='category-list'),
            path('venues/', VenueView.as_view(), name='venue-list'),
            path('hashtags/', HashtagListCreateView.as_view(), name='hashtag-list'),
            path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
            path('my-events/', MyEventsView.as_view(), name='my-events'),
            path('profile/', UserProfileDetailView.as_view(), name='profile-detail'),
            path('checkdateview/', CheckDateView.as_view(), name='check-date'),
            path('copy-event/', CopyEventView.as_view(), name='copy_event'),
            path('my-hosted-events/', MyHostedEventsView.as_view(), name='my-hosted-events'),
            path('venues-create/', CreateVenueAPIView.as_view(), name='create-venue'),
            path('user-profiles/', UserProfileListAPIView.as_view(), name='user-profile-list'),
            path('postscreate/', CreatePostAPIView.as_view(), name='create-post'),
            path('report_post/', ReportPostView.as_view(), name='report-post'),
            path('comments/', CommentListView.as_view(), name='comment-list'),
            path('like_comment/', LikeCommentView.as_view(), name='like-comment'),
            path('add_comment/', AddCommentView.as_view(), name='add-comment'),
            path('reposts/', RepostListView.as_view(), name='repost-list'),
            path('repost_comments/', RepostCommentListView.as_view(), name='repost-comment-list'),
            path('like_repost/', LikeRepostView.as_view(), name='like-repost'),
            path('add_repost_comment/', AddRepostCommentView.as_view(), name='add-repost-comment'),
            path('like_repost_comment/', LikeRepostCommentView.as_view(), name='like-repost-comment'),
            path('report_repost/', ReportRepostView.as_view(), name='report-repost'),
            path('user_profile_detail/', UserProfileTapDetailView.as_view(), name='user-profile-detail'),
            path('user_posts/', UserPostsView.as_view(), name='user-posts'),
            path('user_reposts/', UserRepostsView.as_view(), name='user-reposts'),
            path('user_event_profile/', UserEventProfile.as_view(), name='user-event-profile'),
            path('user_category_stats/', UserCategoryStatsView.as_view(), name='user-category-stats'),
            path('all_events/', AllEventsView.as_view(), name='all-events'),
            path('search/', SearchAPIView.as_view(), name='search'),
            path('get_user_id/', GetCurrentUserIDView.as_view(), name='get-user-id'),
            path('get_user_by_id/<uuid:user_id>/', GetUserByIDView.as_view(), name='get-user-by-id'),
            path('get_followers_and_following/', GetFollowersAndFollowingView.as_view(), name='get-followers-and-following'),
            path('notifications/', NotificationListView.as_view(), name='notification-list'),
            path('notifications/mark-read/', MarkNotificationsReadView.as_view(), name='mark-notifications-read'),
            path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
            path('get_user_profile/', GetUserProfileByIDView.as_view(), name='get-user-profile-by-id'),
            path('get_user_category_stats/', GetUserInfoTabStatsByIDView.as_view(), name='get-user-category-stats'),
            path('get_user_posts_and_reposts/', GetUserPostsAndRepostsByIDView.as_view(), name='get-user-posts-and-reposts'),
            path('get_user_events/', GetUserEventsByIDView.as_view(), name='get-user-events'),
            path('get_user_event_profile/', GetUserEventProfileByIDView.as_view(), name='get-user-event-profile'),
            path('create_no_show/', CreateNoShowView.as_view(), name='create-no-show'),
            path('kick_user_from_event/', KickUserFromEventView.as_view(), name='kick-user-from-event'),
            path('get_user_absence_flag/', GetUserAbsenceFlagView.as_view(), name='get-user-absence-flag'),
            path('get_user_average_review/', GetUserAverageReviewView.as_view(), name='get-user-average-review'),
            path('add_review/', AddReviewView.as_view(), name='add-review'),
            path('add_new_category/', CreateNewCategoryView.as_view(), name='add-new-category'),
            path('increase_all_views/', IncreaseAllViewsAPIView.as_view(), name='increase-all-views'),





















                




























]