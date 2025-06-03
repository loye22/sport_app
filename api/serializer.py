from rest_framework import serializers
from .models import EventStats , RepostComment , AdditionalOption, Hashtag ,GeoLocation ,Venue, UserProfile , ChatMessage , Post , Comment , Event , Notification ,Repost , Category
from django.contrib.auth.models import User



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
    team = serializers.ChoiceField(choices=['A', 'B'])



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




class EventOverlapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'date', 'start_time', 'end_time']


class CopyEventSerializer(serializers.ModelSerializer):
    date = serializers.DateField()  # Required input for the new date
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'score', 'image', 'category', 'Venue', 'date',
            'start_time', 'end_time', 'description', 'host', 'status',
            'price', 'payment_status', 'max_members', 'cancellation_reason',
            'created_at', 'team_a_members', 'team_b_members'
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
    posts_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id','full_name', 'birth_date', 'profile_picture', 'posts_count', 'followers_count', 'following_count']

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
            'stats',  # Include the stats field
        ]
        


class SearchRequestSerializer(serializers.Serializer):
    search_text = serializers.CharField(required=True, min_length=1)
    category = serializers.CharField(required=False, allow_null=True)
    price_max = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    price_min = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    date = serializers.DateField(required=False, allow_null=True)
    hashtag = serializers.CharField(required=False, allow_null=True)
    

class SearchUserSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'full_name', 'email', 'profile_picture', 'is_following']  # Add 'is_following'

    def get_is_following(self, obj):
        # Get the authenticated user from the request context
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            requester_profile = request.user.userprofile
            return obj in requester_profile.following.all()  # Check if the user is in the requester's following list
        return False
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'content', 'timestamp', 'read_status']

def x():
    pass