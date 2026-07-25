from rest_framework import serializers
from .models import EventStats , Review , RepostComment , AdditionalOption, Hashtag ,GeoLocation ,Venue, UserProfile , ChatMessage , Post , Comment , Event , Notification ,Repost , Category, DeleteRequest
from django.contrib.auth.models import User
from .services.user_activity import get_user_activity_summary


class AdditionalOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalOption
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class GeoLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoLocation
        fields = ['latitude', 'longitude']

class VenueSerializer(serializers.ModelSerializer):
    location = GeoLocationSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    additional_options = AdditionalOptionSerializer(many=True, read_only=True)  # Note: many=True
    created_by = UserProfileSerializer(read_only=True)  # Nested serializer for full user details


    class Meta:
        model = Venue
        fields = '__all__'





class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields =  ('__all__')


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields =  ('__all__')

class PostSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    created_by = UserProfileSerializer(read_only=True)
    reported_by = UserProfileSerializer(read_only=True)
    hashtags = HashtagSerializer(many=True, read_only=True)
    participants = UserProfileSerializer(many=True, read_only=True)
    liked_by = UserProfileSerializer(many=True, read_only=True)
    reposted_by = UserProfileSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField( read_only=True) 
    comment_counter = serializers.SerializerMethodField(read_only=True)
    isitmain = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Post
        fields = ('__all__')

    def get_is_liked(self, obj):
            user = self.context.get('request').user if self.context.get('request') else None
            if user and user.is_authenticated:
                return obj.liked_by.filter(id=user.userprofile.id).exists()
            return False
    def get_comment_counter(self, obj):
        return Comment.objects.filter(post=obj).count()
    
    def get_isitmain(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return False
        user_profile = getattr(request.user, 'userprofile', None)
        if not user_profile:
            return False
        return obj.created_by_id == user_profile.id
    
    
class CommentSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer(read_only=True)
    isLiked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ('__all__')
    def get_isLiked(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.liked_by.filter(id=user.userprofile.id).exists()
        return False


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = '__all__'

    def create(self, validated_data):
        profile_picture_url = validated_data.pop('profile_picture', None)
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        if profile_picture_url:
            user_profile.profile_picture = profile_picture_url
            user_profile.save()
        return user_profile






class EventSerializer(serializers.ModelSerializer):
            host_details = serializers.SerializerMethodField(read_only=True)
            team_a_members = UserProfileSerializer(many=True, read_only=True)
            team_b_members = UserProfileSerializer(many=True, read_only=True)
            team_c_members = UserProfileSerializer(many=True, read_only=True)
            team_d_members = UserProfileSerializer(many=True, read_only=True)
            team_e_members = UserProfileSerializer(many=True, read_only=True)
            team_f_members = UserProfileSerializer(many=True, read_only=True)
            team_g_members = UserProfileSerializer(many=True, read_only=True)
            team_h_members = UserProfileSerializer(many=True, read_only=True)
            #Venue = VenueSerializer(read_only=True)
               # For output: nested venue details
            venue_details = VenueSerializer(source="Venue", read_only=True)
    
            # For input: allow the client to send a venue's PK
            Venue = serializers.PrimaryKeyRelatedField(
                queryset=Venue.objects.filter(status='Available'),
                required=False,
                allow_null=True
            )
            
            # Explicitly include location and popularity fields
            city = serializers.ChoiceField(choices=Event.CITY_CHOICES, required=False)
            latitude = serializers.FloatField(required=False)
            longitude = serializers.FloatField(required=False)
            popularity_counter = serializers.IntegerField(read_only=True)
            
            # Additional image fields for event creation
            image2 = serializers.URLField(required=False, allow_null=True)
            image3 = serializers.URLField(required=False, allow_null=True)
            image4 = serializers.URLField(required=False, allow_null=True)
            
            # Teams number field with validation
            teams_number = serializers.IntegerField(
                min_value=1, 
                max_value=8, 
                required=False,
                default=2
            )

            class Meta:
                model = Event
                fields = ('__all__')
                read_only_fields = ['host']
            def get_host_details(self, obj):
                if obj.host:
                    return {
                        'id': obj.host.id,
                        'full_name': obj.host.full_name,
                        'profile_picture': obj.host.profile_picture  # Assuming this field holds the URL
                    }
                return None
            
            def validate_teams_number(self, value):
                if value is not None and (value < 1 or value > 8):
                    raise serializers.ValidationError("Teams number must be between 1 and 8.")
                return value
            
            def validate(self, data):
                # Validate start_time and end_time
                if 'start_time' in data and 'end_time' in data:
                    if data['start_time'] >= data['end_time']:
                        raise serializers.ValidationError({
                            'end_time': 'End time must be after start time.'
                        })
                return data





class EventSerializerEvent(serializers.ModelSerializer):
            host_details = serializers.SerializerMethodField(read_only=True)
            team_a_members = UserProfileSerializer(many=True, read_only=True)
            team_b_members = UserProfileSerializer(many=True, read_only=True)
            team_c_members = UserProfileSerializer(many=True, read_only=True)
            team_d_members = UserProfileSerializer(many=True, read_only=True)
            team_e_members = UserProfileSerializer(many=True, read_only=True)
            team_f_members = UserProfileSerializer(many=True, read_only=True)
            team_g_members = UserProfileSerializer(many=True, read_only=True)
            team_h_members = UserProfileSerializer(many=True, read_only=True)
            venue_details = VenueSerializer(source="Venue", read_only=True)
    
            Venue = serializers.PrimaryKeyRelatedField(
                queryset=Venue.objects.filter(status='Available'),
                error_messages={
                    'does_not_exist': 'The selected venue does not exist or is not available.',
                    'invalid': 'Please select a valid venue.'
                }
            )

            class Meta:
                model = Event
                fields = ('__all__')
                read_only_fields = ['host']
                error_messages = {
                    'title': {
                        'required': 'Event title is required.',
                        'blank': 'Event title cannot be empty.'
                    },
                    'date': {
                        'required': 'Event date is required.',
                        'invalid': 'Please enter a valid date.'
                    },
                    'start_time': {
                        'required': 'Start time is required.',
                        'invalid': 'Please enter a valid start time.'
                    },
                    'end_time': {
                        'required': 'End time is required.',
                        'invalid': 'Please enter a valid end time.'
                    },
                    'max_members': {
                        'required': 'Maximum number of members is required.',
                        'min_value': 'Maximum members must be at least 2.',
                        'invalid': 'Please enter a valid number for maximum members.'
                    }
                }

            def get_host_details(self, obj):
                try:
                    if obj.host:
                        return {
                            'id': obj.host.id,
                            'full_name': obj.host.full_name,
                            'profile_picture': obj.host.profile_picture.url if obj.host.profile_picture else None
                        }
        
                    return None
                except Exception as e:
                    return {
                        'id': obj.host.id if obj.host else None,
                        'full_name': obj.host.full_name if obj.host else None,
                        'profile_picture': None,
                        'error': 'Unable to load profile picture'
                    }

            def validate(self, data):
                if 'start_time' in data and 'end_time' in data:
                    if data['start_time'] >= data['end_time']:
                        raise serializers.ValidationError({
                            'end_time': 'End time must be after start time.'
                        })
                return data                
            


class JoinEventSerializer(serializers.Serializer):
    #user_id = serializers.UUIDField()
    team = serializers.ChoiceField(choices=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])



class CancelJoinEventSerializer(serializers.Serializer):
    event_id = serializers.UUIDField()
    cancellation_reason = serializers.CharField(max_length=255)



class UnfollowUserSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    user_to_unfollow_id = serializers.UUIDField()

# api/serializers.py


class RepostSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    original_post = PostSerializer(read_only=True)
    hashtags = HashtagSerializer(many=True, read_only=True)
    isLiked = serializers.SerializerMethodField(read_only=True)
    comment_counter = serializers.SerializerMethodField(read_only=True)
    is_saved = serializers.SerializerMethodField(read_only=True)  # <-- Add this line
    isitmain = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Repost
        fields = ('__all__')

    def get_isLiked(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.liked_by.filter(id=user.userprofile.id).exists()
        return False

    def get_comment_counter(self, obj):
        return RepostComment.objects.filter(repost=obj).count()
    
    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_profile = getattr(request.user, 'userprofile', None)
            if user_profile:
                return user_profile.saved_reposts.filter(id=obj.id).exists()
        return False
    
    def get_isitmain(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return False
        user_profile = getattr(request.user, 'userprofile', None)
        if not user_profile:
            return False
        return obj.user_id == user_profile.id




class EventOverlapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'date', 'start_time', 'end_time']


class CopyEventSerializer(serializers.ModelSerializer):
    date = serializers.DateField()  # Required input for the new date
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'score', 'image', 'image2', 'image3', 'image4', 'category', 'Venue', 'date',
            'start_time', 'end_time', 'description', 'host', 'status',
            'price', 'payment_status', 'max_members', 'cancellation_reason',
            'created_at', 'team_a_members', 'team_b_members', 'team_c_members', 'team_d_members',
            'team_e_members', 'team_f_members', 'team_g_members', 'team_h_members'
        ]
        read_only_fields = ['id', 'created_at']  # Auto-generated fields


class RepostCommentSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer(read_only=True)
    isLiked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RepostComment
        fields = '__all__'

    def get_isLiked(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.liked_by.filter(id=user.userprofile.id).exists()
        return False


class UserProfileDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    posts_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    
    # Lightweight user representation for lists
    class UserProfileBasicSerializer(serializers.ModelSerializer):
        username = serializers.CharField(source='user.username', read_only=True)

        class Meta:
            model = UserProfile
            fields = ['id', 'username', 'full_name', 'profile_picture']

    followers = UserProfileBasicSerializer(many=True, read_only=True)
    following = UserProfileBasicSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id','username','full_name', 'birth_date', 'profile_picture', 'posts_count', 'followers_count', 'following_count', 'followers', 'following']

    def get_posts_count(self, obj):
        return Post.objects.filter(created_by=obj).count()

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()
    

class EventStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventStats
        fields = [
            'team_winner',
            'team_a_total_attempts',
            'team_a_attempts_on_target',
            'team_a_fouls_committed',
            'team_a_yellow_cards',
            'team_a_red_cards',
            'team_a_offsides',
            'team_a_corners',
            'team_a_possession',
            'team_b_total_attempts',
            'team_b_attempts_on_target',
            'team_b_fouls_committed',
            'team_b_yellow_cards',
            'team_b_red_cards',
            'team_b_offsides',
            'team_b_corners',
            'team_b_possession',
        ]    

class EventWithStatsSerializer(serializers.ModelSerializer):
    stats = EventStatsSerializer(read_only=True)  # Include the related EventStats data
    team_a_members = UserProfileSerializer(many=True, read_only=True)  # Include full details of Team A members
    team_b_members = UserProfileSerializer(many=True, read_only=True)  # Include full details of Team B members
    team_c_members = UserProfileSerializer(many=True, read_only=True)  # Include full details of Team C members
    team_d_members = UserProfileSerializer(many=True, read_only=True)  # Include full details of Team D members
    team_e_members = UserProfileSerializer(many=True, read_only=True)  # Include full details of Team E members
    team_f_members = UserProfileSerializer(many=True, read_only=True)  # Include full details of Team F members
    team_g_members = UserProfileSerializer(many=True, read_only=True)  # Include full details of Team G members
    team_h_members = UserProfileSerializer(many=True, read_only=True)  # Include full details of Team H members
    category = CategorySerializer(read_only=True)  # Include full details of the category

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'score',
            'status',
            'date',
            'start_time',
            'end_time',
            'description',
            'category',  # Include the category details
            'team_a_members',
            'team_b_members',
            'team_c_members',
            'team_d_members',
            'team_e_members',
            'team_f_members',
            'team_g_members',
            'team_h_members',
            'stats',  # Include the stats field
        ]
        


class SearchRequestSerializer(serializers.Serializer):
    search_text = serializers.CharField(required=True, min_length=1)


# Brief serializer for completed/participated events
class EventCompletedBriefSerializer(serializers.ModelSerializer):
    host = serializers.SerializerMethodField(read_only=True)
    category = serializers.SerializerMethodField(read_only=True)
    venue = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'score',
            'status',
            'date',
            'start_time',
            'end_time',
            'image',
            'host',
            'category',
            'venue',
        ]

    def get_host(self, obj):
        if obj.host:
            return {
                'id': str(obj.host.id),
                'full_name': obj.host.full_name,
                'profile_picture': obj.host.profile_picture,
            }
        return None

    def get_category(self, obj):
        if obj.category:
            return {
                'id': str(obj.category.id),
                'name': obj.category.name,
            }
        return None

    def get_venue(self, obj):
        if obj.Venue:
            return {
                'id': str(obj.Venue.id),
                'title': obj.Venue.title,
                'address': obj.Venue.address,
                'latitude': obj.Venue.latitude,
                'longitude': obj.Venue.longitude,
            }
        return None
    
    

class SearchUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'full_name', 'email', 'profile_picture', 'is_following']

    def get_is_following(self, obj):
        # Get the authenticated user from the request context
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            requester_profile = request.user.userprofile
            return obj in requester_profile.following.all()  # Check if the user is in the requester's following list
        return False
    
# class NotificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Notification
#         fields = ['id', 'content', 'timestamp', 'read_status']


class UserProfileMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'profile_picture']
        

class NotificationSerializer(serializers.ModelSerializer):
    user = UserProfileMiniSerializer(read_only=True)    # receiver
    sender = UserProfileMiniSerializer(read_only=True)  # sender
    following_status = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'user', 'sender', 'content', 'timestamp', 'read_status', 'following_status']

    def get_following_status(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return False
        # If sender is missing, there is no one to follow
        if not getattr(obj, 'sender', None):
            return False
        try:
            requester_profile = request.user.userprofile
        except Exception:
            return False
        return obj.sender in requester_profile.following.all()


def x():
    pass


# Basic profile info serializer
class GeoLocationBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoLocation
        fields = ['id', 'name', 'latitude', 'longitude']


class UserProfileBasicInfoSerializer(serializers.ModelSerializer):
    location = GeoLocationBasicSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'full_name',
            'birth_date',
            'profile_picture',
            'address',
            'location',
        ]


# Serializer for updating basic profile fields
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'full_name',
            'birth_date',
            'address',
            'profile_picture',
            'latitude',
            'longitude',
        ]


class DeleteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeleteRequest
        fields = ['id', 'reason', 'status', 'created_at', 'processed_at', 'admin_notes']
        read_only_fields = ['id', 'status', 'created_at', 'processed_at', 'admin_notes']


class DeleteRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeleteRequest
        fields = ['reason']





class UserActivitySummarySerializer(serializers.Serializer):
    activityOverview = serializers.SerializerMethodField()
    atAGlance = serializers.SerializerMethodField()
    topActivities = serializers.SerializerMethodField()
    activityPatterns = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    bestAttendance = serializers.SerializerMethodField()

    def _get_data(self, obj):
        if not hasattr(self, '_cached_data'):
            request = self.context.get('request')
            self._cached_data = get_user_activity_summary(obj, request=request)
        return self._cached_data

    def get_activityOverview(self, obj):
        # obj is UserProfile instance
        return self._get_data(obj)['activityOverview']

    def get_atAGlance(self, obj):
        return self._get_data(obj)['atAGlance']

    def get_topActivities(self, obj):
        return self._get_data(obj)['topActivities']

    def get_activityPatterns(self, obj):
        return self._get_data(obj)['activityPatterns']

    def get_statistics(self, obj):
        return self._get_data(obj)['statistics']

    def get_bestAttendance(self, obj):
        return self._get_data(obj)['bestAttendance']


# ==============================================
# NEW SERIALIZERS FOR EVENT DATA V2 API
# ==============================================

class EventDataV2CategorySerializer(serializers.ModelSerializer):
    """Category serializer for Event Data V2"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


class EventDataV2VenueSerializer(serializers.ModelSerializer):
    """Venue serializer for Event Data V2"""
    class Meta:
        model = Venue
        fields = ['id', 'title', 'address', 'image', 'latitude', 'longitude', 'price_per_hour']


class EventDataV2HostSerializer(serializers.ModelSerializer):
    """Host serializer for Event Data V2"""
    class Meta:
        model = UserProfile
        fields = [
            'id', 'full_name', 'email', 'profile_picture', 
            'average_host_rating', 'phone_number'
        ]


class EventDataV2TeamMemberSerializer(serializers.ModelSerializer):
    """Team member serializer for Event Data V2"""
    user_id = serializers.UUIDField(source='id')
    name = serializers.CharField(source='full_name')
    image_url = serializers.CharField(source='profile_picture')
    is_host = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['user_id', 'name', 'image_url', 'is_host']
    
    def get_is_host(self, obj):
        event = self.context.get('event')
        if event and hasattr(event, 'host'):
            return event.host.id == obj.id
        return False


class EventDataV2TeamSerializer(serializers.Serializer):
    """Team serializer for Event Data V2"""
    team_name = serializers.CharField()
    members = serializers.SerializerMethodField()
    member_count = serializers.IntegerField()
    
    def get_members(self, obj):
        members = obj.get('members', [])
        event = self.context.get('event')
        return EventDataV2TeamMemberSerializer(
            members, 
            many=True, 
            context={'event': event}
        ).data


class EventDataV2ParticipantSummarySerializer(serializers.Serializer):
    """Participant summary serializer for Event Data V2"""
    total_joined = serializers.IntegerField()
    max_allowed = serializers.IntegerField()
    display = serializers.CharField()
    spots_remaining = serializers.IntegerField()


class EventDataV2ReviewSerializer(serializers.ModelSerializer):
    """Review serializer for Event Data V2"""
    review_id = serializers.UUIDField(source='id')
    reviewer_name = serializers.CharField(source='reviewer.full_name')
    reviewer_image_url = serializers.CharField(source='reviewer.profile_picture')
    event_title = serializers.CharField(source='event.title')
    title = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'review_id', 'title', 'rating', 'comment',
            'reviewer_name', 'reviewer_image_url',
            'image_1', 'image_2', 'image_3', 'event_title'
        ]
    
    def get_title(self, obj):
        if obj.comment:
            words = obj.comment.split()[:5]
            return ' '.join(words) + '...' if len(words) == 5 else obj.comment[:50]
        return f"Review - {obj.rating} stars"



class EventDataV2StatsSerializer(serializers.ModelSerializer):
    """Event Stats serializer for Event Data V2"""
    # Add the status field from the Event model
    game_status = serializers.SerializerMethodField()
    
    class Meta:
        model = EventStats
        fields = [
            'id', 'team_winner', 
            'team_a_total_attempts', 'team_a_attempts_on_target',
            'team_a_fouls_committed', 'team_a_yellow_cards', 
            'team_a_red_cards', 'team_a_offsides', 'team_a_corners',
            'team_a_possession',
            'team_b_total_attempts', 'team_b_attempts_on_target',
            'team_b_fouls_committed', 'team_b_yellow_cards',
            'team_b_red_cards', 'team_b_offsides', 'team_b_corners',
            'team_b_possession',
            'game_status'  # Add this field
        ]
    
    def get_game_status(self, obj):
        # Get the status from the related Event model
        if hasattr(obj, 'event_detail'):  # event_detail is the related_name in Event model
            return obj.event_detail.status
        return None

class EventDataV2EventDetailSerializer(serializers.ModelSerializer):
    """Main Event detail serializer for Event Data V2"""
    category = EventDataV2CategorySerializer(read_only=True)
    venue = EventDataV2VenueSerializer(source='Venue', read_only=True)
    host = EventDataV2HostSerializer(read_only=True)
    teams = serializers.SerializerMethodField()
    participant_summary = serializers.SerializerMethodField()
    # Remove status from here - we'll get it from event_stats
    # status is no longer included in this serializer
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'image', 'image2', 
            'image3', 'image4', 'score', 'category', 'venue',
            'date', 'start_time', 'end_time', 'city',  # status removed from here
            'price', 'payment_status', 'max_members', 'teams_number',
            'host', 'teams', 'participant_summary', 'created_at'
        ]
    
    def get_teams(self, obj):
        team_fields = [
            ('team_a_members', 'Team A'),
            ('team_b_members', 'Team B'),
            ('team_c_members', 'Team C'),
            ('team_d_members', 'Team D'),
            ('team_e_members', 'Team E'),
            ('team_f_members', 'Team F'),
            ('team_g_members', 'Team G'),
            ('team_h_members', 'Team H'),
        ]
        
        teams_data = []
        for field_name, team_label in team_fields:
            members = getattr(obj, field_name).all()
            if members.exists():
                teams_data.append({
                    'team_name': team_label,
                    'members': members,
                    'member_count': members.count()
                })
        
        return EventDataV2TeamSerializer(
            teams_data, 
            many=True, 
            context={'event': obj}
        ).data
    
    def get_participant_summary(self, obj):
        total_joined = 0
        team_fields = [
            'team_a_members', 'team_b_members', 'team_c_members',
            'team_d_members', 'team_e_members', 'team_f_members',
            'team_g_members', 'team_h_members'
        ]
        
        for field in team_fields:
            total_joined += getattr(obj, field).count()
        
        max_allowed = obj.max_members
        
        return {
            'total_joined': total_joined,
            'max_allowed': max_allowed,
            'display': f"{total_joined}/{max_allowed}",
            'spots_remaining': max_allowed - total_joined
        }



class EventDataV2Serializer(serializers.Serializer):
    """Main response serializer for Event Data V2 API"""
    event = EventDataV2EventDetailSerializer()
    reviews = EventDataV2ReviewSerializer(many=True)
    event_stats = EventDataV2StatsSerializer()


