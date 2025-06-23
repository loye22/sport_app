from django.db import models
import uuid
from django.db.models import PROTECT
from django.contrib.auth.models import User as AuthUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User






class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField()  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GeoLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255)  # Set a default value

    def __str__(self):
        return f"({self.latitude}, {self.longitude})"


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birth_date = models.DateField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    location = models.ForeignKey(GeoLocation, on_delete=PROTECT, null=True, blank=True)
    profile_picture = models.URLField(null=True, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following_users', blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers_users', blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    address = models.TextField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)   # New field: User latitude
    longitude = models.FloatField(null=True, blank=True)  # New field: User longitude
    average_host_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)




    def __str__(self):
        return self.full_name


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(UserProfile, on_delete=PROTECT, related_name='notifications', default=1)  # Set a default value
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)
    sender = models.ForeignKey(UserProfile, on_delete=PROTECT, related_name='sent_notifications', null=True, blank=True)


    def __str__(self):
        return f"Notification for {self.user.full_name} at {self.timestamp}"

class GroupChat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(UserProfile, related_name='group_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    messages = models.ManyToManyField('ChatMessage', related_name='group_chats', null= False) 
    created_by = models.ForeignKey(UserProfile, on_delete=PROTECT, related_name='created_group_chats')


    
    def __str__(self):
        return self.name


class ChatMessage(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=PROTECT, related_name='sent_messages')
    receiver = models.ForeignKey(UserProfile, on_delete=PROTECT, related_name='received_messages', null=True, blank=True)
    content = models.TextField()
    seenStatus = models.BooleanField(default=False)
    reportStatus = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"



class AdditionalOption(models.Model):
    TYPE_CHOICES = [
        ('referee', 'Referee'),
        ('medical_officer', 'Medical Officer'),
        ('others', 'Others'),  # New option added

    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField()
    image = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.type} "

class Event(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    score = models.CharField(max_length=5 ,null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=PROTECT)
    Venue = models.ForeignKey('Venue', on_delete=PROTECT, limit_choices_to={'status': 'Available'})
    date = models.DateField()
    start_time = models.TimeField(default='09:00')
    end_time = models.TimeField(default='17:00')
    #location = models.ForeignKey(GeoLocation, on_delete=PROTECT, null=True, blank=True)
    description = models.TextField()
    host = models.ForeignKey(UserProfile, on_delete=PROTECT, related_name='hosted_events')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_status = models.BooleanField(default=False)
    max_members = models.PositiveIntegerField(default=0)
    cancellation_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    #additional_options = models.ManyToManyField(AdditionalOption, related_name='events', blank=True)
    team_a_members = models.ManyToManyField(UserProfile, related_name='team_a_members', blank=True)
    team_b_members = models.ManyToManyField(UserProfile, related_name='team_b_members', blank=True)
    event_stats = models.OneToOneField('EventStats', on_delete=PROTECT, null=True, blank=True, related_name='event_detail')
    is_vendor = models.BooleanField(default=False)
    cancellation_period_hours = models.PositiveIntegerField(default=24, help_text="Hours before event when cancellation is allowed")
    removed_players = models.ManyToManyField(UserProfile, related_name='removed_from_events', blank=True)


    def clean(self):
        # Check the total members in both teams
        team_a_count = self.team_a_members.count()
        team_b_count = self.team_b_members.count()
        total_members = team_a_count + team_b_count

        # Check that start_time is not after end_time
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")


        if total_members > self.max_members:
            raise ValidationError(f"Total members in both teams cannot exceed the max members limit of {self.max_members}.")
    def save(self, *args, **kwargs):
        # Call the clean method to validate the model before saving
        self.clean() 
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title
       
 

class EventCancellation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(Event, related_name='cancellations', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, related_name='event_cancellations', on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    cancelled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} cancelled {self.event.title} at {self.cancelled_at}"


class Hashtag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name




class Venue(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Maintenance', 'Maintenance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    price_per_hour = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(999)])
    #location = models.ForeignKey(GeoLocation, on_delete=PROTECT, null=True, blank=True)
    address = models.TextField()
    image = models.URLField(null=True, blank=True)
    description = models.TextField()
    created_by = models.ForeignKey(UserProfile, on_delete=PROTECT, related_name='created_venues')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=PROTECT)  # Ensure null=True
    additional_options = models.ManyToManyField(AdditionalOption, related_name='events', blank=True)
    # you add the lang and lat to the venue model and make them mandatory and give defula value of 1 
    latitude = models.FloatField()   # New field: Venue latitude
    longitude = models.FloatField()  # New field: Venue longitude
    
  



    def __str__(self):
        return self.title


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    activity_name = models.CharField(max_length=255)
    scores = models.CharField(max_length=5)
    possession = models.CharField(max_length=255)
    image = models.URLField(null=True, blank=True)
    fouls = models.CharField(max_length=100) 
    category = models.ForeignKey(Category, on_delete=PROTECT, null=True, blank=True)
    hashtags = models.ManyToManyField(Hashtag, related_name='posts', blank=True)
    created_by = models.ForeignKey(UserProfile, on_delete=PROTECT, related_name='created_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(UserProfile, related_name='participated_posts', blank=True)
    is_published = models.BooleanField(default=True)
    likes = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(UserProfile, related_name='liked_posts', blank=True)
    is_reported = models.BooleanField(default=False)
    report_date = models.DateTimeField(null=True, blank=True)
    reported_by = models.ForeignKey(UserProfile, on_delete=PROTECT, related_name='reported_posts', null=True, blank=True)
    reposted_by = models.ManyToManyField(UserProfile, related_name='reposted_posts', blank=True)
    body_text = models.TextField(null=True, blank=True)
    report_reason = models.TextField(null=True, blank=True)
    share_counter = models.PositiveIntegerField(default=0)





    def __str__(self):
        return self.activity_name


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    post = models.ForeignKey(Post, on_delete=PROTECT, related_name='comments')
    content = models.TextField()
    created_by = models.ForeignKey(UserProfile, on_delete=PROTECT, related_name='created_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(UserProfile, related_name='liked_comments', blank=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)


    def __str__(self):
        return f"Comment by {self.created_by.full_name} on {self.post.activity_name}"
    


class Repost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    original_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reposts')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reposts')
    content = models.TextField(default='Repost')
    image = models.URLField(null=True, blank=True)
    voice = models.URLField(null=True, blank=True)
    hashtags = models.ManyToManyField(Hashtag, related_name='reposts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_reported = models.BooleanField(default=False)
    report_date = models.DateTimeField(null=True, blank=True)
    reported_by = models.ForeignKey(UserProfile, on_delete=PROTECT, related_name='reported_reposts', null=True, blank=True)
    report_reason = models.TextField(null=True, blank=True)
    share_counter = models.PositiveIntegerField(default=0)
    Likes  = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(UserProfile, related_name='liked_reposts', blank=True)

    def __str__(self):
        return f"Repost of {self.original_post.activity_name} by {self.user.full_name}"
    

class StoredImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=20)
    image = models.ImageField()  
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class RepostComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    repost = models.ForeignKey(Repost, on_delete=PROTECT, related_name='comments')
    content = models.TextField()
    created_by = models.ForeignKey(UserProfile, on_delete=PROTECT, related_name='created_repost_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(UserProfile, related_name='liked_repost_comments', blank=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)

    def __str__(self):
        return f"Comment by {self.created_by.full_name} on repost of {self.repost.original_post.activity_name}"
    


class EventStats(models.Model):
    event = models.OneToOneField('Event', on_delete=PROTECT, related_name='stats')

    TEAM_WINNER_CHOICES = [
        ('A', 'Team A'),
        ('B', 'Team B'),
        ('ND', 'Not Determined'),
    ]
    team_winner = models.CharField(max_length=2, choices=TEAM_WINNER_CHOICES, default='ND')

    # Team A Stats
    team_a_total_attempts = models.PositiveIntegerField(default=0)
    team_a_attempts_on_target = models.PositiveIntegerField(default=0)
    team_a_fouls_committed = models.PositiveIntegerField(default=0)
    team_a_yellow_cards = models.PositiveIntegerField(default=0)
    team_a_red_cards = models.PositiveIntegerField(default=0)
    team_a_offsides = models.PositiveIntegerField(default=0)
    team_a_corners = models.PositiveIntegerField(default=0)
    team_a_possession = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    # Team B Stats
    team_b_total_attempts = models.PositiveIntegerField(default=0)
    team_b_attempts_on_target = models.PositiveIntegerField(default=0)
    team_b_fouls_committed = models.PositiveIntegerField(default=0)
    team_b_yellow_cards = models.PositiveIntegerField(default=0)
    team_b_red_cards = models.PositiveIntegerField(default=0)
    team_b_offsides = models.PositiveIntegerField(default=0)
    team_b_corners = models.PositiveIntegerField(default=0)
    team_b_possession = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Stats for {self.event.title}"
    

class NoShow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)  # Add UUID as primary key
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='no_shows')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='no_show_users')
    date = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    host = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='host_reviews')
    reviewer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='given_host_reviews')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='host_reviews')
    rating = models.DecimalField(
        max_digits=3,  # Maximum number of digits, including decimal places
        decimal_places=2,  # Number of decimal places
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]  # Ensure the value is between 1.0 and 5.0
    )