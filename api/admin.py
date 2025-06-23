from django.contrib import admin
from api.models import Notification ,RepostComment 
from api.models import  Review , NoShow , EventStats  ,EventCancellation ,GeoLocation, UserProfile, GroupChat, ChatMessage, Event, AdditionalOption, Hashtag, Category, Venue, Post, Comment,  Repost , StoredImage
from django.contrib import admin
from unfold.admin import ModelAdmin


# class CustomAdminClass(ModelAdmin):
#     pass


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id' , 'full_name', 'gender', 'birth_date', 'phone_number', 'email', 'location', 'profile_picture', 'created_at', 'address')
    search_fields = ('full_name', 'email', 'phone_number' )
    list_filter = ('gender', 'created_at')
    ordering = ('-created_at',)
    filter_horizontal = ("followers","following", )  # Add this line to display the followers field as a horizontal filter
   


class VenueAdmin(admin.ModelAdmin):
    list_display = ('id' , 'title', 'address', 'image', 'description', 'category', 'created_by', 'status', 'created_at')
    search_fields = ('title', 'address', 'description')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)
    filter_horizontal = ('additional_options',)  # Add this line to display the additional_options field as a horizontal filter



class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date', 'description', 'host', 'status', 'price', 'max_members', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('host' , 'status', 'date', 'created_at')
    ordering = ('-created_at',)
    filter_horizontal = ('team_b_members' , 'team_a_members' , 'removed_players')  # Add this line to display the members field as a horizontal filter


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp')
    search_fields = ('sender__full_name', 'receiver__full_name', 'content')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id' , 'post', 'content', 'created_by', 'created_at')
    search_fields = ('post__title', 'content', 'created_by__full_name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    filter_horizontal = ('liked_by',)  


class PostAdmin(admin.ModelAdmin):
    list_display = ('id' , 'activity_name', 'category', 'created_by', 'is_published', 'likes','is_reported' ,'created_at')
    search_fields = ('activity_name', 'category__name', 'created_by__full_name')
    list_filter = ('is_published', 'created_at' , 'is_reported')
    ordering = ('-created_at',)
    filter_horizontal = ('hashtags', 'liked_by' , 'reposted_by', 'participants')  # Add this line to display the hashtags field as a horizontal filter
    



class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name', 'created_by__full_name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    filter_horizontal = ('members','messages')  # Add this line to display the members field as a horizontal filter


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id' , 'sender', 'user', 'content', 'timestamp', 'read_status')
    search_fields = ('user__full_name', 'content')
    list_filter = ('read_status', 'timestamp')
    ordering = ('-timestamp',)



class GeoLocationAdmin(admin.ModelAdmin):
    list_display = ('id' , 'latitude', 'longitude', 'name', 'description')
    search_fields = ('name', 'description')
    list_filter = ('latitude', 'longitude')
    ordering = ('name',)


class AdditionalOptionAdmin(admin.ModelAdmin):
    list_display = ('id' , 'type', 'price', 'description', 'image')
    search_fields = ('type', 'description')
    list_filter = ('type',)
    ordering = ('type',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id' , 'name', 'image')
    search_fields = ('name',)
    ordering = ('name',)

class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name','id')
    search_fields = ('name',)
    ordering = ('name',)

class RepostAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_post', 'user', 'created_at')
    search_fields = ('original_post__activity_name', 'user__full_name', 'content','hashtags')
    list_filter = ('created_at', 'hashtags')
    ordering = ('-created_at',)
    filter_horizontal = ('hashtags','liked_by')  # Add this line to display the hashtags field as a horizontal filter


class StoredImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'uploaded_at')



# filepath: /home/louie/projectR/apiapp/api/admin.py
class EventCancellationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'reason', 'cancelled_at')
    search_fields = ('event__title', 'user__full_name', 'reason')
    list_filter = ('cancelled_at',)
    ordering = ('-cancelled_at',)

# add repodt vomment 
class RepostCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'repost', 'content', 'created_by', 'created_at', 'likes')
    search_fields = ('content', 'created_by__full_name', 'repost__original_post__activity_name')
    list_filter = ('created_at', 'likes',)
    filter_horizontal = ('liked_by',)  # Add this line to display the likes field as a horizontal filter
    ordering = ('-created_at',)

class EventStatsAdmin(admin.ModelAdmin):
    list_display = ('event', 'team_a_total_attempts', 'team_a_attempts_on_target', 'team_a_fouls_committed', 'team_a_yellow_cards', 'team_a_red_cards', 'team_a_offsides', 'team_a_corners', 'team_a_possession', 'team_b_total_attempts', 'team_b_attempts_on_target', 'team_b_fouls_committed', 'team_b_yellow_cards', 'team_b_red_cards', 'team_b_offsides', 'team_b_corners', 'team_b_possession')
    search_fields = ('event__title',)
    list_filter = ('event',)


class NoShowAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'event', 'date')  # Display these fields in the admin list view
    search_fields = ('user__full_name', 'event__title')  # Enable search by user full name and event title
    list_filter = ('date',)  # Add a filter for the date field
    ordering = ('-date',)  # Order by date in descending order

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('host', 'reviewer', 'event', 'rating')
    search_fields = ('host__full_name', 'reviewer__full_name', 'event__title')
    list_filter = ('rating', 'event')
    ordering = ('-rating',)

admin.site.register(Review, ReviewAdmin)
admin.site.register(NoShow, NoShowAdmin)
admin.site.register(EventStats,EventStatsAdmin)
admin.site.register(RepostComment, RepostCommentAdmin)
admin.site.register(EventCancellation, EventCancellationAdmin)
admin.site.register(Repost, RepostAdmin)
admin.site.register(Notification,NotificationAdmin)
admin.site.register(GeoLocation,GeoLocationAdmin)
admin.site.register(UserProfile , UserProfileAdmin)
admin.site.register(GroupChat , GroupChatAdmin)
admin.site.register(ChatMessage , ChatMessageAdmin)
admin.site.register(Event , EventAdmin)
admin.site.register(AdditionalOption , AdditionalOptionAdmin)
admin.site.register(Hashtag,  HashtagAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Venue,VenueAdmin)
admin.site.register(Post , PostAdmin )
admin.site.register(Comment,CommentAdmin)
admin.site.register(StoredImage, StoredImageAdmin)

# Register your models here.






