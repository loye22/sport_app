from django.shortcuts import render
from rest_framework.generics import ListAPIView
from datetime import datetime, timedelta
from apiapp.settings import DEFAULT_FROM_EMAIL
from .models import Review ,NoShow ,RepostComment , Repost ,AdditionalOption, EventCancellation ,  UserProfile, Category, Post, Comment , Event , Notification , Venue , Hashtag, DeleteRequest
from .serializer import  UserProfileUpdateSerializer, UserProfileBasicInfoSerializer , EventCompletedBriefSerializer , EventSerializerEvent , NotificationSerializer ,SearchUserSerializer ,SearchRequestSerializer, EventWithStatsSerializer ,UserProfileDetailSerializer ,RepostCommentSerializer , EventOverlapSerializer  ,CopyEventSerializer  ,HashtagSerializer ,  CategorySerializer,  CancelJoinEventSerializer ,UserProfileSerializer, VenueSerializer, PostSerializer, CommentSerializer , EventSerializer , JoinEventSerializer , UnfollowUserSerializer, RepostSerializer, DeleteRequestSerializer, DeleteRequestCreateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.db.models import Q
from uuid import UUID
from datetime import datetime 
from django.db import transaction
from django.core.exceptions import ValidationError 
from django.utils import timezone
import uuid
from django.contrib.auth.forms import PasswordResetForm
from rest_framework.permissions import AllowAny
from django.db.models import Avg
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import models 
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.db.models.deletion import ProtectedError




class UserProfileListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        profiles = UserProfile.objects.all()
        serializer = UserProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get the authenticated user's profile
        profile = request.user.userprofile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response([], status=status.HTTP_200_OK)

        user_profiles = (
            UserProfile.objects
            .filter(
                Q(email__icontains=query) |
                Q(user__email__icontains=query) |
                Q(full_name__icontains=query) |
                Q(user__username__icontains=query)
            )
            .select_related('user')
            .order_by('full_name')[:50]
        )

        serializer = SearchUserSerializer(user_profiles, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get the authenticated user's profile
        user_profile = request.user.userprofile

        # Filter events where the user is either the host, or a member of team A or team B
        events = Event.objects.filter(
            Q(host=user_profile) |
            Q(team_a_members=user_profile) |
            Q(team_b_members=user_profile)
        ).distinct()

        serializer = EventSerializerEvent(events, many=True)
        print("serializer.data")
        print(len(serializer.data));
        return Response(serializer.data, status=status.HTTP_200_OK)


class HashtagListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]    
    # Optionally enable authentication
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer

class VenueView(APIView):
    # Optionally enable authentication
    permission_classes = [IsAuthenticated]    
    def get(self, request, *args, **kwargs):
        venues = Venue.objects.filter(status='Available')
        serializer = VenueSerializer(venues, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = VenueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        # Check if a file is included in the request
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'File missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the file using Django's default storage system.
        # Files will be saved under the "uploads/" directory.
        file_path = default_storage.save(f'uploads/{file_obj.name}', file_obj)
        
        # Optionally, you can return the file path or any other info
        return Response({'message': 'File uploaded successfully', 'file_path': file_path}, status=status.HTTP_201_CREATED)

    

class PostView(APIView):
        permission_classes = [IsAuthenticated] ## uncomment this in production 
        def get(self, request, *args, **kwargs):
            posts = Post.objects.filter(is_reported=False , is_published=True )
            serializer = PostSerializer(posts , many=True, context={'request': request})  
            return Response(serializer.data)

        # def post(self, request, *args, **kwargs):
        #         serializer = PostSerializer(data=request.data)
        #         if serializer.is_valid():
        #             serializer.save()
        #             return Response(serializer.data, status=status.HTTP_201_CREATED)
        #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class ReportPostView(APIView):
    permission_classes = [IsAuthenticated] ## uncomment this in production 
    def post(self, request, *args, **kwargs):
        post_id = request.data.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
            post.is_reported = True
            post.save()
            return Response({'status': 'Post reported successfully'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        

class CommentView(APIView):
        permission_classes = [IsAuthenticated] ## uncomment this in production 
        def get(self, request, *args, **kwargs):
            comments = Comment.objects.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        def post(self, request, *args, **kwargs):
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        
            


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': str(user.userprofile.id)  

            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
        

# class FollowUserView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def post(self, request, *args, **kwargs):
#         user_to_follow_id = request.data.get('user_to_follow_id')
#         sender_id = request.data.get('sender_id')

#         if not user_to_follow_id:
#             return Response({'error': 'user_to_follow_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
#         if not sender_id:
#             return Response({'error': 'sender_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             sender = UserProfile.objects.get(id=sender_id)
#         except UserProfile.DoesNotExist:
#             return Response({'error': 'Sender not found.'}, status=status.HTTP_404_NOT_FOUND)

#         try:
#             user_to_follow = UserProfile.objects.get(id=user_to_follow_id)
#         except UserProfile.DoesNotExist:
#             return Response({'error': 'User to follow not found.'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         try:
#             sender.following.add(user_to_follow)
#             user_to_follow.followers.add(sender)
            
#             # Send notification to the user being followed, with sender info
#             Notification.objects.create(
#                 user=user_to_follow,
#                 sender=sender,
#                 content=f"{sender.full_name} has followed you."
#             )
            
#             return Response({'status': 'User followed successfully'}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': f'Unable to follow user: {str(e)}'},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user_to_follow_id = request.data.get('user_to_follow_id')

        if not user_to_follow_id:
            return Response({'error': 'user_to_follow_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sender = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'Sender (authenticated user) not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_to_follow = UserProfile.objects.get(id=user_to_follow_id)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User to follow not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            sender.following.add(user_to_follow)
            user_to_follow.followers.add(sender)
            
            # Send notification to the user being followed, with sender info
            Notification.objects.create(
                user=user_to_follow,
                sender=sender,
                content=f"{sender.full_name} has followed you."
            )
            
            return Response({'status': 'User followed successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Unable to follow user: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LikePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = request.data.get('post_id')

        try:
            # Get the authenticated user's profile
            user = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        if user in post.liked_by.all():
            # User has already liked the post, so unlike it
            post.liked_by.remove(user)
            post.likes -= 1
            post.save()
            return Response({'status': 'Post unliked successfully'}, status=status.HTTP_200_OK)
        else:
            # User has not liked the post yet, so like it
            post.liked_by.add(user)
            post.likes += 1
            post.save()
            return Response({'status': 'Post liked successfully'}, status=status.HTTP_200_OK)



class EventView(APIView):
    permission_classes = [IsAuthenticated]  # Enable authentication
    def get(self, request, *args, **kwargs):
        # Get all available events without excluding joined events
        events = Event.objects.filter(status='Available')
        
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(host=request.user.userprofile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JoinEventView(APIView):
    permission_classes = [IsAuthenticated]  # Enable in production

    def post(self, request, *args, **kwargs):
        serializer = JoinEventSerializer(data=request.data)
        if serializer.is_valid():
            event_id = request.data.get('event_id')
            team = serializer.validated_data.get('team')

            # Use the authenticated user's profile
            try:
                user = request.user.userprofile
            except UserProfile.DoesNotExist:
                return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

            try:
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the event is available
            if event.status != 'Available':
                return Response({'error': 'Event is not available for joining'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user is already a member of the event
            if (user in event.team_a_members.all() or user in event.team_b_members.all() or 
                user in event.team_c_members.all() or user in event.team_d_members.all() or
                user in event.team_e_members.all() or user in event.team_f_members.all() or
                user in event.team_g_members.all() or user in event.team_h_members.all()):
                return Response({'error': 'User has already joined the event'}, status=status.HTTP_400_BAD_REQUEST)

            # Add the user to the specified team
            if team == 'A':
                event.team_a_members.add(user)
            elif team == 'B':
                event.team_b_members.add(user)
            elif team == 'C':
                event.team_c_members.add(user)
            elif team == 'D':
                event.team_d_members.add(user)
            elif team == 'E':
                event.team_e_members.add(user)
            elif team == 'F':
                event.team_f_members.add(user)
            elif team == 'G':
                event.team_g_members.add(user)
            elif team == 'H':
                event.team_h_members.add(user)
            else:
                return Response({'error': 'Invalid team specified'}, status=status.HTTP_400_BAD_REQUEST)

            # Send notification to the host
            Notification.objects.create(
                user=event.host,
                content=f"{user.full_name} has joined your event {event.title}."
            )

            event.save()
            return Response({'status': 'User joined the event successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

   

class CompleteEventView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        event_id = request.data.get('event_id')
        
        if not event_id:
            return Response({'error': 'event_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the authenticated user is the host of the event
        if request.user.userprofile != event.host:
            return Response({'error': 'Only the event host can mark the event as completed'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the event is currently available
        if event.status != 'Available':
            return Response({'error': f'Event is already {event.status.lower()}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark the event as completed
        event.status = 'Completed'
        event.save()
        
        return Response({
            'status': 'Event marked as completed successfully',
            'event_id': str(event.id),
            'event_title': event.title,
            'new_status': event.status
        }, status=status.HTTP_200_OK)


class GetEventView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, event_id, *args, **kwargs):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateEventView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, event_id, *args, **kwargs):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the authenticated user is the host of the event
        if request.user.userprofile != event.host:
            return Response({'error': 'Only the event host can update the event'}, status=status.HTTP_403_FORBIDDEN)
        
        # Use the same serializer as create event
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'Event updated successfully',
                'event': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelJoinEventView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = CancelJoinEventSerializer(data=request.data)
        if serializer.is_valid():
            event_id = serializer.validated_data.get('event_id')
            cancellation_reason = serializer.validated_data.get('cancellation_reason')

            try:
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

            # Use the authenticated user's profile
            try:
                user = request.user.userprofile
            except UserProfile.DoesNotExist:
                return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check that the user is a member of the event
            if user not in event.team_a_members.all() and user not in event.team_b_members.all():
                return Response({'error': 'User is not a member of the event'}, status=status.HTTP_400_BAD_REQUEST)

            # Remove the user from the event teams if present
            if user in event.team_a_members.all():
                event.team_a_members.remove(user)
            if user in event.team_b_members.all():
                event.team_b_members.remove(user)

            # Create a cancellation record for this event
            EventCancellation.objects.create(
                event=event,
                user=user,
                reason=cancellation_reason
            )

            # Optionally, send a notification to the event host
            Notification.objects.create(
                user=event.host,
                content=f"{user.full_name} has cancelled joining your event {event.title}. Reason: {cancellation_reason}"
            )

            event.save()
            return Response({'status': 'User cancelled joining the event successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnfollowUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # Only get user_to_unfollow_id from the POST data
        user_to_unfollow_id = request.data.get('user_to_unfollow_id')
        
        if not user_to_unfollow_id:
            return Response({'error': 'user_to_unfollow_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get logged in user's profile directly from request.user
            user = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'Logged in user profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Get the profile of the user to unfollow by its ID
            user_to_unfollow = UserProfile.objects.get(id=user_to_unfollow_id)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User to unfollow not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            user.following.remove(user_to_unfollow)
            user_to_unfollow.followers.remove(user)
            return Response({'status': 'User unfollowed successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Unable to unfollow user: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddRepostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        original_post_id = request.data.get('original_post_id')
        content = request.data.get('content', 'Repost')
        voice = request.data.get('voice', None)
        image = request.data.get('image', None)
        hashtags = request.data.get('hashtags', [])

        if not original_post_id:
            return Response({'error': 'original_post_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            original_post = Post.objects.get(id=original_post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Original post not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        # Process hashtags
        hashtag_objects = []
        for tag in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag)
            hashtag_objects.append(hashtag)

        repost = Repost.objects.create(
            original_post=original_post,
            content=content,
            voice=voice,
            image=image,
            user=user
        )

        repost.hashtags.set(hashtag_objects)
        repost.save()

        serializer = RepostSerializer(repost, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)    




 


class CheckDateView(APIView):
    def post(self, request):
        try:
            # Get data from request
            venue_id = request.data.get('venue_id')
            start_time = request.data.get('start_time')  # Expected format: "HH:MM"
            end_time = request.data.get('end_time')      # Expected format: "HH:MM"

            # Validate input
            if not all([venue_id, start_time, end_time]):
                return Response(
                    {"error": "Missing required fields (venue_id, start_time, end_time)"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Convert string times to datetime.time objects
            try:
                start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            except ValueError:
                return Response(
                    {"error": "Invalid time format. Use HH:MM"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate time logic
            if start_time_obj >= end_time_obj:
                return Response(
                    {"error": "Start time must be before end time"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if venue exists and is available
            try:
                venue = Venue.objects.get(id=venue_id, status='Available')
            except Venue.DoesNotExist:
                return Response(
                    {"error": "Venue not found or not available"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Query for all overlapping events for this venue
            overlapping_events = Event.objects.filter(
                Venue=venue ,
                 status='Available'
            ).filter(
                Q(start_time__lt=end_time_obj) & Q(end_time__gt=start_time_obj)
            )

            serializer = EventOverlapSerializer(overlapping_events, many=True)
            return Response({
                "venue": venue.title,
                "start_time": start_time,
                "end_time": end_time,
                "overlapping_events": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




 

class CopyEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the event ID and new date from the request
        event_id = request.data.get('event_id')
        new_date = request.data.get('date')  # Expecting "YYYY-MM-DD"
        if not event_id or not new_date:
            return Response({"error": "event_id and date are required"},
                            status=status.HTTP_400_BAD_REQUEST)
        
                
        # Validate and convert event_id to UUID
        try:
            event_id_uuid = UUID(str(event_id))
        except ValueError:
            return Response({"error": "Invalid event_id format"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the authenticated user's profile
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"},
                            status=status.HTTP_404_NOT_FOUND)
        
        # Manually fetch the original event, ensuring it belongs to the authenticated user
        try:
            original_event = Event.objects.get(id=event_id, host=user_profile)
        except Event.DoesNotExist:
            return Response({"error": "Event not found or not owned by the user"},
                            status=status.HTTP_404_NOT_FOUND)
        
        # Prepare data for the new event by copying details from the original
        new_event_data = {
            'title': original_event.title,
            'score': None,  # Reset
            'image': original_event.image,
            'category': original_event.category,
            'Venue': original_event.Venue,
            'date': new_date,  # User-provided new date
            'start_time': original_event.start_time,
            'end_time': original_event.end_time,
            'description': original_event.description,
            'host': user_profile,  # Set host as the UserProfile instance
            'status': 'Available',  # Reset status
            'price': original_event.price,
            'payment_status': False,  # Reset
            'max_members': original_event.max_members,
            'cancellation_reason': None,  # Reset
        }
        
        # Create the new event instance using the prepared data
        new_event = Event.objects.create(**new_event_data)
        
        # Copy ManyToMany relationships from the original event
        if original_event.team_a_members.exists():
            new_event.team_a_members.set(original_event.team_a_members.all())
        if original_event.team_b_members.exists():
            new_event.team_b_members.set(original_event.team_b_members.all())
        
        # Serialize the new event for the response
        serializer = CopyEventSerializer(new_event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)





class MyHostedEventsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            hosted_events = Event.objects.filter(host=user_profile,status='Completed')
            serializer = EventSerializer(hosted_events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class CreateVenueAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        # Map request data
        data = {
            'title': request.data.get('title'),
            'description': request.data.get('description'),
            'price_per_hour': request.data.get('pricePerHour'),
            'latitude': request.data.get('latitude'),
            'longitude': request.data.get('longitude'),
            'address': request.data.get('address'),
            'image': request.data.get('image'),
            'category': request.data.get('category'),
            'additional_options': request.data.get('additionalOptions', []),  # Default to empty list
        }
        # Validate all fields are present (excluding additional_options since it's optional)
        required_fields = [
            'title', 'description', 'price_per_hour', 'latitude',
            'longitude', 'address', 'image', 'category'
        ]
        missing_fields = [field for field in required_fields if data[field] is None]
        if missing_fields:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Validate price_per_hour is a number and within range
        try:
            data['price_per_hour'] = float(data['price_per_hour'])
            if not (0 <= data['price_per_hour'] <= 999):
                return Response(
                    {'error': 'Price per hour must be between 0 and 999'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Price per hour must be a valid number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Validate latitude and longitude are numbers
        try:
            data['latitude'] = float(data['latitude'])
            data['longitude'] = float(data['longitude'])
        except (ValueError, TypeError):
            return Response(
                {'error': 'Latitude and longitude must be valid numbers'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Start transaction
        try:
            with transaction.atomic():
                # Get and validate category
                try:
                    category = Category.objects.get(id=data['category'])
                except Category.DoesNotExist:
                    return Response(
                        {'error': 'Invalid category ID'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Handle additional options (optional)
                additional_options = []
                if data['additional_options']:  # Only process if additional_options are provided
                    if not isinstance(data['additional_options'], list):
                        return Response(
                            {'error': 'Additional options must be a list'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    required_option_fields = ['type', 'price', 'description', 'image']
                    for option_data in data['additional_options']:
                        # Check all required fields in additional options
                        missing_option_fields = [
                            field for field in required_option_fields
                            if field not in option_data or option_data[field] is None
                        ]
                        if missing_option_fields:
                            return Response(
                                {'error': f'Missing required fields in additional option: {", ".join(missing_option_fields)}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        # Validate price is a number
                        try:
                            price = float(option_data['price'])
                            if price < 0:
                                return Response(
                                    {'error': 'Additional option price cannot be negative'},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                        except (ValueError, TypeError):
                            return Response(
                                {'error': 'Additional option price must be a valid number'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        option = AdditionalOption(
                            type=option_data['type'],
                            price=price,
                            description=option_data['description'],
                            image=option_data['image']
                        )
                        option.full_clean()
                        additional_options.append(option)
                    # Save all additional options if any were provided
                    if additional_options:
                        AdditionalOption.objects.bulk_create(additional_options)
                # Create venue
                venue = Venue(
                    title=data['title'],
                    description=data['description'],
                    price_per_hour=data['price_per_hour'],
                    latitude=data['latitude'],
                    longitude=data['longitude'],
                    address=data['address'],
                    image=data['image'],
                    status='Available',
                    created_by=request.user.userprofile,  # Adjust based on your user model
                    category=category
                )
                venue.full_clean()  # Run model validation
                venue.save()
                # Assign additional options to the venue if any were provided
                if additional_options:
                    venue.additional_options.set(additional_options)
                # Serialize and return the response
                serializer = VenueSerializer(venue)
                return Response({
                    'message': 'Venue created successfully',
                    'venue': serializer.data
                }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create venue: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )





class CreatePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # List of required fields
        required_fields = [
            "activity_name",
            "scores",
            "possession",
            "image",
            "fouls",
            "body_text",
            "category_id",
            "hashtag_ids",
            "selected_friends_ids"
        ]
        missing_fields = [field for field in required_fields if not request.data.get(field)]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract fields from the request data
        activity_name = request.data.get("activity_name")
        scores = request.data.get("scores")
        possession = request.data.get("possession")
        image = request.data.get("image")
        image2 = request.data.get("image2")
        image3 = request.data.get("image3")
        image4 = request.data.get("image4")
        fouls = request.data.get("fouls")
        body_text = request.data.get("body_text")
        category_id = request.data.get("category_id")
        hashtag_ids = request.data.get("hashtag_ids")
        selected_friends_ids = request.data.get("selected_friends_ids")
        extra_title_1 = request.data.get("extra_title_1")
        extra_value_1 = request.data.get("extra_value_1")
        extra_title_2 = request.data.get("extra_title_2")
        extra_value_2 = request.data.get("extra_value_2")

        # Validate optional short fields length if provided (<= 10 chars)
        short_fields = {
            "extra_title_1": extra_title_1,
            "extra_value_1": extra_value_1,
            "extra_title_2": extra_title_2,
            "extra_value_2": extra_value_2,
        }
        for field_name, field_value in short_fields.items():
            if field_value is not None:
                if not isinstance(field_value, str):
                    return Response({"error": f"{field_name} must be a string."}, status=status.HTTP_400_BAD_REQUEST)
                if len(field_value) > 10:
                    return Response({"error": f"{field_name} must be at most 10 characters."}, status=status.HTTP_400_BAD_REQUEST)

        # Look up the Category instance
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the current user's profile
        try:
            created_by = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "User profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate hashtag_ids – it must be a list of valid IDs
        if not isinstance(hashtag_ids, list):
            return Response(
                {"error": "hashtag_ids must be provided as a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        hashtags = Hashtag.objects.filter(id__in=hashtag_ids)
        if hashtags.count() != len(hashtag_ids):
            return Response(
                {"error": "One or more hashtag IDs are invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate selected_friends_ids – it must be a list of valid IDs
        if not isinstance(selected_friends_ids, list):
            return Response(
                {"error": "selected_friends_ids must be provided as a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        friends = UserProfile.objects.filter(id__in=selected_friends_ids)
        if friends.count() != len(selected_friends_ids):
            return Response(
                {"error": "One or more selected friends IDs are invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the Post instance (without many-to-many fields)
        post = Post.objects.create(
            activity_name=activity_name,
            scores=scores,
            possession=possession,
            image=image,
            image2=image2,
            image3=image3,
            image4=image4,
            fouls=fouls,
            body_text=body_text,
            category=category,
            created_by=created_by,
            extra_title_1=extra_title_1,
            extra_value_1=extra_value_1,
            extra_title_2=extra_title_2,
            extra_value_2=extra_value_2,
        )

        # Set many-to-many relationships
        post.hashtags.set(hashtags)
        post.participants.set(friends)

        # Serialize and return the newly created post using the existing PostSerializer
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id, *args, **kwargs):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdatePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, post_id, *args, **kwargs):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        # Owner check
        try:
            current_user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

        if post.created_by != current_user_profile:
            return Response({"error": "You are not allowed to edit this post."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        # Optional short fields length validation
        for key in ["extra_title_1", "extra_value_1", "extra_title_2", "extra_value_2"]:
            if key in data and data.get(key) is not None:
                value = data.get(key)
                if not isinstance(value, str):
                    return Response({"error": f"{key} must be a string."}, status=status.HTTP_400_BAD_REQUEST)
                if len(value) > 10:
                    return Response({"error": f"{key} must be at most 10 characters."}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare prospective values (use provided values, else current ones)
        prospective = {
            "activity_name": data.get("activity_name", post.activity_name),
            "body_text": data.get("body_text", post.body_text),
            "image": data.get("image", post.image),
            "image2": data.get("image2", getattr(post, "image2", None)),
            "image3": data.get("image3", getattr(post, "image3", None)),
            "image4": data.get("image4", getattr(post, "image4", None)),
            "fouls": data.get("fouls", post.fouls),
            "scores": data.get("scores", post.scores),
            "possession": data.get("possession", post.possession),
            "extra_title_1": data.get("extra_title_1", getattr(post, "extra_title_1", None)),
            "extra_value_1": data.get("extra_value_1", getattr(post, "extra_value_1", None)),
            "extra_title_2": data.get("extra_title_2", getattr(post, "extra_title_2", None)),
            "extra_value_2": data.get("extra_value_2", getattr(post, "extra_value_2", None)),
        }

        # Apply simple fields to instance now (after basic validation below)
        for field, value in prospective.items():
            setattr(post, field, value)

        # Determine category (provided or existing)
        if "category_id" in data:
            if data.get("category_id"):
                try:
                    category = Category.objects.get(id=data.get("category_id"))
                except Category.DoesNotExist:
                    return Response({"error": "Category not found."}, status=status.HTTP_400_BAD_REQUEST)
                post.category = category
            else:
                post.category = None

        # Determine hashtags (provided or existing)
        if "hashtag_ids" in data:
            hashtag_ids = data.get("hashtag_ids")
            if not isinstance(hashtag_ids, list):
                return Response({"error": "hashtag_ids must be provided as a list."}, status=status.HTTP_400_BAD_REQUEST)
            hashtags_qs = Hashtag.objects.filter(id__in=hashtag_ids)
            if hashtags_qs.count() != len(hashtag_ids):
                return Response({"error": "One or more hashtag IDs are invalid."}, status=status.HTTP_400_BAD_REQUEST)
            prospective_hashtag_ids = list(hashtags_qs.values_list("id", flat=True))
        else:
            prospective_hashtag_ids = list(post.hashtags.values_list("id", flat=True))

        # Update participants if provided
        if "selected_friends_ids" in data:
            selected_friends_ids = data.get("selected_friends_ids")
            if not isinstance(selected_friends_ids, list):
                return Response({"error": "selected_friends_ids must be provided as a list."}, status=status.HTTP_400_BAD_REQUEST)
            friends = UserProfile.objects.filter(id__in=selected_friends_ids)
            if friends.count() != len(selected_friends_ids):
                return Response({"error": "One or more selected friends IDs are invalid."}, status=status.HTTP_400_BAD_REQUEST)
            post.participants.set(friends)

        # Business validations on resulting state
        # 1) Require at least one image among image/image2/image3/image4
        images_after = [prospective.get("image"), prospective.get("image2"), prospective.get("image3"), prospective.get("image4")]
        has_any_image = any(bool(str(img).strip()) for img in images_after if img is not None) or any(
            bool(str(getattr(post, f, "") or "").strip()) for f in ["image", "image2", "image3", "image4"]
        )
        if not has_any_image:
            return Response({"error": "At least one image (image/image2/image3/image4) is required."}, status=status.HTTP_400_BAD_REQUEST)

        # 2) Require non-empty activity_name and body_text
        if not isinstance(post.activity_name, str) or not post.activity_name.strip():
            return Response({"error": "activity_name is required and cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(post.body_text, str) or not post.body_text.strip():
            return Response({"error": "body_text is required and cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        # 3) Require category present
        if post.category is None:
            return Response({"error": "category_id is required and must be valid."}, status=status.HTTP_400_BAD_REQUEST)

        # 4) Require at least one hashtag
        if not prospective_hashtag_ids:
            return Response({"error": "At least one hashtag is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Persist hashtag changes if provided
        if "hashtag_ids" in data:
            post.hashtags.set(Hashtag.objects.filter(id__in=prospective_hashtag_ids))

        post.save()

        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, post_id, *args, **kwargs):
        return self.put(request, post_id, *args, **kwargs)


class DeletePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id, *args, **kwargs):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            current_user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

        if post.created_by != current_user_profile:
            return Response({"error": "You are not allowed to delete this post."}, status=status.HTTP_403_FORBIDDEN)

        post.delete()
        return Response({"status": "Post deleted successfully"}, status=status.HTTP_200_OK)

class ReportPostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = request.data.get('post_id')
        report_reason = request.data.get('report_reason')

        if not post_id or not report_reason:
            return Response({'error': 'post_id and report_reason are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        post.is_reported = True
        post.report_reason = report_reason
        post.report_date = timezone.now()
        post.save()

        return Response({'status': 'Post reported successfully'}, status=status.HTTP_200_OK)




class CommentListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = request.data.get('post_id')

        if not post_id:
            return Response({'error': 'post_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try: 
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(post=post, parent_comment__isnull=True).order_by('created_at')
        comments_data = self.get_comments_with_replies(comments,request)
        return Response(comments_data, status=status.HTTP_200_OK)

    def get_comments_with_replies(self, comments , request):
        comments_data = []
        for comment in comments:
            comment_data = CommentSerializer(comment, context={'request': request}).data
            replies = Comment.objects.filter(parent_comment=comment).order_by('created_at')
            comment_data['replies'] = self.get_comments_with_replies(replies,request)
            comments_data.append(comment_data)
        return comments_data
    
class LikeCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        comment_id = request.data.get('comment_id')

        try:
            # Get the authenticated user's profile
            user = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

        if user in comment.liked_by.all():
            # User has already liked the comment, so unlike it
            comment.liked_by.remove(user)
            comment.likes -= 1
            comment.save()
            return Response({'status': 'Comment unliked successfully'}, status=status.HTTP_200_OK)
        else:
            # User has not liked the comment yet, so like it
            comment.liked_by.add(user)
            comment.likes += 1
            comment.save()
            return Response({'status': 'Comment liked successfully'}, status=status.HTTP_200_OK)



class AddCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = request.data.get('post_id')
        content = request.data.get('content')
        parent_comment_id = request.data.get('parent_comment_id', None)

        if not post_id or not content:
            return Response({'error': 'post_id and content are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        parent_comment = None
        if parent_comment_id:
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id)
            except Comment.DoesNotExist:
                return Response({'error': 'Parent comment not found'}, status=status.HTTP_404_NOT_FOUND)

        comment = Comment.objects.create(
            post=post,
            content=content,
            created_by=user,
            parent_comment=parent_comment
        )

        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RepostListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        reposts = Repost.objects.filter(is_reported=False)
        serializer = RepostSerializer(reposts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RepostCommentListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        repost_id = request.data.get('repost_id')

        if not repost_id:
            return Response({'error': 'repost_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try: 
            repost = Repost.objects.get(id=repost_id)
        except Repost.DoesNotExist:
            return Response({'error': 'Repost not found'}, status=status.HTTP_404_NOT_FOUND)

        comments = RepostComment.objects.filter(repost=repost, parent_comment__isnull=True).order_by('created_at')
        comments_data = self.get_comments_with_replies(comments, request)
        return Response(comments_data, status=status.HTTP_200_OK)

    def get_comments_with_replies(self, comments, request):
        comments_data = []
        for comment in comments:
            comment_data = RepostCommentSerializer(comment, context={'request': request}).data
            replies = RepostComment.objects.filter(parent_comment=comment).order_by('created_at')
            comment_data['replies'] = self.get_comments_with_replies(replies, request)
            comments_data.append(comment_data)
        return comments_data


class LikeRepostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        repost_id = request.data.get('repost_id')

        try:
            # Get the authenticated user's profile
            user = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            repost = Repost.objects.get(id=repost_id)
        except Repost.DoesNotExist:
            return Response({'error': 'Repost not found'}, status=status.HTTP_404_NOT_FOUND)

        if user in repost.liked_by.all():
            # User has already liked the repost, so unlike it
            repost.liked_by.remove(user)
            repost.Likes -= 1
            repost.save()
            return Response({'status': 'Repost unliked successfully'}, status=status.HTTP_200_OK)
        else:
            # User has not liked the repost yet, so like it
            repost.liked_by.add(user)
            repost.Likes += 1
            repost.save()
            return Response({'status': 'Repost liked successfully'}, status=status.HTTP_200_OK)

class AddRepostCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        repost_id = request.data.get('repost_id')
        content = request.data.get('content')
        parent_comment_id = request.data.get('parent_comment_id', None)

        if not repost_id or not content:
            return Response({'error': 'repost_id and content are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            repost = Repost.objects.get(id=repost_id)
        except Repost.DoesNotExist:
            return Response({'error': 'Repost not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        parent_comment = None
        if parent_comment_id:
            try:
                parent_comment = RepostComment.objects.get(id=parent_comment_id)
            except RepostComment.DoesNotExist:
                return Response({'error': 'Parent comment not found'}, status=status.HTTP_404_NOT_FOUND)

        comment = RepostComment.objects.create(
            repost=repost,
            content=content,
            created_by=user,
            parent_comment=parent_comment
        )

        serializer = RepostCommentSerializer(comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LikeRepostCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        comment_id = request.data.get('comment_id')

        if not comment_id:
            return Response({'error': 'comment_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the authenticated user's profile
            user = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            comment = RepostComment.objects.get(id=comment_id)
        except RepostComment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

        if user in comment.liked_by.all():
            # User has already liked the comment, so unlike it
            comment.liked_by.remove(user)
            comment.likes -= 1
            comment.save()
            return Response({'status': 'Comment unliked successfully'}, status=status.HTTP_200_OK)
        else:
            # User has not liked the comment yet, so like it
            comment.liked_by.add(user)
            comment.likes += 1
            comment.save()
            return Response({'status': 'Comment liked successfully'}, status=status.HTTP_200_OK)


class ReportRepostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        repost_id = request.data.get('repost_id')
        report_reason = request.data.get('report_reason')

        if not repost_id or not report_reason:
            return Response({'error': 'repost_id and report_reason are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            repost = Repost.objects.get(id=repost_id)
        except Repost.DoesNotExist:
            return Response({'error': 'Repost not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        repost.is_reported = True
        repost.report_reason = report_reason
        repost.report_date = timezone.now()
        repost.reported_by = user
        repost.save()

        return Response({'status': 'Repost reported successfully'}, status=status.HTTP_200_OK)


class UserProfileTapDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileDetailSerializer(user_profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)


        posts = Post.objects.filter(created_by=user_profile ,is_reported=False , is_published=True)
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRepostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        reposts = Repost.objects.filter(user=user_profile, is_reported=False)
        serializer = RepostSerializer(reposts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserEventProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=404)

        # Filter events where the user is in Team A or Team B and the event is completed
        events = Event.objects.filter(
            status='Completed'
        ).filter(
            Q(team_a_members=user_profile) | Q(team_b_members=user_profile)
        ).distinct()  # Ensure no duplicate events

        # Serialize the events
        serializer = EventWithStatsSerializer(events, many=True, context={'request': request})
        return Response(serializer.data, status=200)



class UserCategoryStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=404)

        # Filter completed events where the user is in Team A or Team B and the event has EventStats
        events = Event.objects.filter(
            status='Completed',
            event_stats__isnull=False  # Ensure the event has related EventStats
        ).filter(
            Q(team_a_members=user_profile) | Q(team_b_members=user_profile)
        ).distinct()

        # Initialize a dictionary to store stats grouped by category
        category_stats = {}

        for event in events:
            category = event.category
            if category.id not in category_stats:
                category_stats[category.id] = {
                    'category': category.name,
                    'category_image': category.image.url if category.image else None,
                    'win': 0,
                    'loss': 0,
                    'matches': 0
                }

            # Increment matches
            category_stats[category.id]['matches'] += 1

            # Determine if the user won or lost
            if event.event_stats:
                if event.event_stats.team_winner == 'A' and user_profile in event.team_a_members.all():
                    category_stats[category.id]['win'] += 1
                elif event.event_stats.team_winner == 'B' and user_profile in event.team_b_members.all():
                    category_stats[category.id]['win'] += 1
                else:
                    category_stats[category.id]['loss'] += 1

        # Convert the stats dictionary to a list
        stats_list = list(category_stats.values())

        return Response(stats_list, status=200)

class AllEventsView(APIView):
    permission_classes = [IsAuthenticated]  # Enable authentication

    def get(self, request, *args, **kwargs):
        # Retrieve all events from the database
        events = Event.objects.all()

        # Serialize the events
        serializer = EventSerializer(events, many=True, context={'request': request})

        # Return the serialized data
        return Response(serializer.data, status=200)

class CompletedParticipatedEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        # Events where status is Completed and user is host or in any team
        events = Event.objects.filter(status='Completed').filter(
            Q(host=user_profile) |
            Q(team_a_members=user_profile) |
            Q(team_b_members=user_profile) |
            Q(team_c_members=user_profile) |
            Q(team_d_members=user_profile) |
            Q(team_e_members=user_profile) |
            Q(team_f_members=user_profile) |
            Q(team_g_members=user_profile) |
            Q(team_h_members=user_profile)
        ).distinct().order_by('-date', '-start_time')[:30]

        serializer = EventCompletedBriefSerializer(events, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class SearchAPIView(APIView):
    def post(self, request):
        # Validate the incoming data
        serializer = SearchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data
        data = serializer.validated_data
        search_text = data['search_text'].strip()
        category = data.get('category')
        price_max = data.get('price_max')
        price_min = data.get('price_min')
        date = data.get('date')
        hashtag = data.get('hashtag')

        # Search Users - Use user__username (from related User model) and full_name
        user_qs = UserProfile.objects.filter(
            Q(user__username__icontains=search_text) |  # Access username via the User model
            Q(full_name__icontains=search_text)
        )

        # Search Posts
        post_qs = Post.objects.filter(
            Q(activity_name__icontains=search_text) |
            Q(body_text__icontains=search_text)
        ).select_related('category', 'created_by', 'reported_by').prefetch_related(
            'hashtags', 'participants', 'liked_by', 'reposted_by'
        ).order_by('-views')
        if category:
            post_qs = post_qs.filter(category__id=category)
        if hashtag:
            post_qs = post_qs.filter(hashtags__name=hashtag)

        # Search Events
        event_qs = Event.objects.filter(
            Q(title__icontains=search_text) |
            Q(description__icontains=search_text)
        ).select_related('category', 'Venue', 'host').prefetch_related(
            'team_a_members', 'team_b_members'
        ).order_by('-popularity_counter')
        if category:
            event_qs = event_qs.filter(category__id=category)
        if price_max is not None:
            event_qs = event_qs.filter(price__lte=price_max)  # Filtering on Event.price
        if price_min is not None:
            event_qs = event_qs.filter(price__gte=price_min)  # Filtering on Event.price
        if date:
            event_qs = event_qs.filter(date=date)

        # Serialize the results with request context
        context = {'request': request}
        users_data = SearchUserSerializer(user_qs, many=True, context=context).data
        posts_data = PostSerializer(post_qs, many=True, context=context).data
        events_data = EventSerializer(event_qs, many=True, context=context).data

        # Combine results
        response_data = {
            "users": users_data,
            "posts": posts_data,
            "events": events_data
        }

        return Response(response_data, status=status.HTTP_200_OK)


class GetCurrentUserIDView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, *args, **kwargs):
        user_profile = request.user.userprofile  # Access the UserProfile linked to the authenticated user
        serializer = UserProfileSerializer(user_profile, context={'request': request})
        # Return the serialized user details
        return Response(serializer.data, status=200)


class GetCurrentUsernameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({"username": user.username}, status=status.HTTP_200_OK)


class GetUserByIDView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, user_id, *args, **kwargs):
        # Try to retrieve the user profile by ID
        user_profile = UserProfile.objects.filter(id=user_id).first()

        # If the user is not found, return a 404 response
        if not user_profile:
            return Response({"error": "User not found."}, status=404)

        # Serialize the user profile
        serializer = UserProfileSerializer(user_profile, context={'request': request})

        # Return the serialized user details
        return Response(serializer.data, status=200)


class ProfileBasicInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=404)

        serializer = UserProfileBasicInfoSerializer(user_profile, context={'request': request})
        return Response(serializer.data, status=200)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=404)

        # View-level validation
        data = request.data
        allowed_fields = {'full_name', 'birth_date', 'address', 'profile_picture', 'latitude', 'longitude'}
        provided_keys = {key for key in data.keys() if key in allowed_fields}
        if not provided_keys:
            return Response({'error': 'No fields provided to update.'}, status=400)

        def is_empty(value):
            if value is None:
                return True
            if isinstance(value, str) and value.strip() == "":
                return True
            return False

        # Validate non-empty for provided string/date fields
        for field_name in ['full_name', 'address', 'profile_picture', 'birth_date']:
            if field_name in data and is_empty(data.get(field_name)):
                return Response({field_name: ['This field may not be empty.']}, status=400)

        # Validate latitude/longitude if present
        for field_name in ['latitude', 'longitude']:
            if field_name in data:
                value = data.get(field_name)
                if is_empty(value):
                    return Response({field_name: ['This field may not be empty.']}, status=400)
                try:
                    float(value)
                except (TypeError, ValueError):
                    return Response({field_name: ['A valid number is required.']}, status=400)

        serializer = UserProfileUpdateSerializer(user_profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class DeleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Attempt deletion; many relations are PROTECT and may block deletion
        try:
            # Optionally also delete the associated auth user after profile deletion
            auth_user = user_profile.user
            user_profile.delete()
            # If profile deletion succeeded, also delete the auth user
            auth_user.delete()
            return Response({"status": "Profile deleted successfully"}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({
                "error": "Cannot delete profile due to existing related objects. Remove or reassign related data first."
            }, status=status.HTTP_400_BAD_REQUEST)

class GetFollowersAndFollowingView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, *args, **kwargs):
        # Get the authenticated user's profile
        user_profile = request.user.userprofile

        # Get followers and following
        followers = user_profile.followers.all()  # Assuming 'followers' is a related_name for the ManyToManyField
        following = user_profile.following.all()  # Assuming 'following' is a related_name for the ManyToManyField

        # Serialize the data
        followers_data = UserProfileSerializer(followers, many=True, context={'request': request}).data
        following_data = UserProfileSerializer(following, many=True, context={'request': request}).data

        # Return the response
        return Response({
            "followers": followers_data,
            "following": following_data
        }, status=200)
    

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        #notifications = Notification.objects.filter(user=user_profile).order_by('-timestamp')
        notifications = Notification.objects.filter(user=user_profile, sender__isnull=False).order_by('-timestamp')
        serializer = NotificationSerializer(notifications, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class MarkNotificationsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        notification_id = request.data.get('notification_id')
        if not notification_id:
            return Response({'error': 'notification_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate if notification_id is a valid UUID string
        try:
            uuid_obj = uuid.UUID(str(notification_id))
        except ValueError:
            return Response({'error': 'Invalid notification_id format'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            notification = Notification.objects.get(id=notification_id, user=user_profile)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

        if notification.read_status:
            return Response({'status': 'Notification already marked as read'}, status=status.HTTP_200_OK)

        notification.read_status = True
        notification.save()
        return Response({'status': 'Notification marked as read'}, status=status.HTTP_200_OK)
    


class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        form = PasswordResetForm(data={'email': email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=True,
                from_email=DEFAULT_FROM_EMAIL,
                email_template_name='registration/password_reset_email.html',
                subject_template_name='registration/password_reset_subject.txt',
            )
            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': form.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email exists in the database
        if not User.objects.filter(email=email).exists():
            return Response({'error': 'This email address is not associated with any account.'}, status=status.HTTP_400_BAD_REQUEST)

        form = PasswordResetForm(data={'email': email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=True,
                from_email=DEFAULT_FROM_EMAIL,
                email_template_name='registration/password_reset_email.html',
                subject_template_name='registration/password_reset_subject.txt',
                extra_email_context={'base_url': 'accounts'},  # Ensure correct base path
            )
            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': form.errors}, status=status.HTTP_400_BAD_REQUEST)


class GetUserProfileByIDView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract the user ID from the request data
        user_id = request.data.get('user_id')

        # Validate that the user_id is provided
        if not user_id:
            return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the user_id is a valid UUID
        try:
            uuid_obj = uuid.UUID(user_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid User ID format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user profile by the provided user ID
        try:
            user_profile = UserProfile.objects.get(id=uuid_obj)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the user profile
        serializer = UserProfileDetailSerializer(user_profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetUserInfoTabStatsByIDView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract the user ID from the request data
        user_id = request.data.get('user_id')

        # Validate that the user_id is provided
        if not user_id:
            return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the user_id is a valid UUID
        try:
            uuid_obj = uuid.UUID(user_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid User ID format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user profile by the provided user ID
        try:
            user_profile = UserProfile.objects.get(id=uuid_obj)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Filter completed events where the user is in Team A or Team B and the event has EventStats
        events = Event.objects.filter(
            status='Completed',
            event_stats__isnull=False  # Ensure the event has related EventStats
        ).filter(
            Q(team_a_members=user_profile) | Q(team_b_members=user_profile)
        ).distinct()

        # Initialize a dictionary to store stats grouped by category
        category_stats = {}

        for event in events:
            category = event.category
            if category.id not in category_stats:
                category_stats[category.id] = {
                    'category': category.name,
                    'category_image': category.image.url if category.image else None,
                    'win': 0,
                    'loss': 0,
                    'matches': 0
                }

            # Increment matches
            category_stats[category.id]['matches'] += 1

            # Determine if the user won or lost
            if event.event_stats:
                if event.event_stats.team_winner == 'A' and user_profile in event.team_a_members.all():
                    category_stats[category.id]['win'] += 1
                elif event.event_stats.team_winner == 'B' and user_profile in event.team_b_members.all():
                    category_stats[category.id]['win'] += 1
                else:
                    category_stats[category.id]['loss'] += 1

        # Convert the stats dictionary to a list
        stats_list = list(category_stats.values())

        return Response(stats_list, status=status.HTTP_200_OK)


class GetUserPostsAndRepostsByIDView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract the user ID from the request data
        user_id = request.data.get('user_id')

        # Validate that the user_id is provided
        if not user_id:
            return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the user_id is a valid UUID
        try:
            uuid_obj = uuid.UUID(user_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid User ID format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user profile by the provided user ID
        try:
            user_profile = UserProfile.objects.get(id=uuid_obj)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch posts created by the user
        posts = Post.objects.filter(created_by=user_profile, is_reported=False, is_published=True)
        posts_serializer = PostSerializer(posts, many=True, context={'request': request})

        # Fetch reposts created by the user
        reposts = Repost.objects.filter(user=user_profile, is_reported=False)
        reposts_serializer = RepostSerializer(reposts, many=True, context={'request': request})

        # Combine the results
        response_data = {
            'posts': posts_serializer.data,
            'reposts': reposts_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

class GetUserEventsByIDView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract the user ID from the request data
        user_id = request.data.get('user_id')

        # Validate that the user_id is provided
        if not user_id:
            return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the user_id is a valid UUID
        try:
            uuid_obj = uuid.UUID(user_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid User ID format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user profile by the provided user ID
        try:
            user_profile = UserProfile.objects.get(id=uuid_obj)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch events where the user is the host or a member of Team A or Team B
        events = Event.objects.filter(
            Q(host=user_profile) |
            Q(team_a_members=user_profile) |
            Q(team_b_members=user_profile)
        ).distinct()

        # Serialize the events
        serializer = EventSerializer(events, many=True, context={'request': request})

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class GetUserEventsByIDView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract the user ID from the request data
        user_id = request.data.get('user_id')

        # Validate that the user_id is provided
        if not user_id:
            return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the user_id is a valid UUID
        try:
            uuid_obj = uuid.UUID(user_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid User ID format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user profile by the provided user ID
        try:
            user_profile = UserProfile.objects.get(id=uuid_obj)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch events where the user is the host or a member of Team A or Team B
        events = Event.objects.filter(
            Q(host=user_profile) |
            Q(team_a_members=user_profile) |
            Q(team_b_members=user_profile)
        ).distinct()

        # Serialize the events
        serializer = EventSerializer(events, many=True, context={'request': request})

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class GetUserEventProfileByIDView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract the user ID from the request data
        user_id = request.data.get('user_id')

        # Validate that the user_id is provided
        if not user_id:
            return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the user_id is a valid UUID
        try:
            uuid_obj = uuid.UUID(user_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid User ID format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user profile by the provided user ID
        try:
            user_profile = UserProfile.objects.get(id=uuid_obj)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Filter events where the user is in Team A or Team B and the event is completed
        events = Event.objects.filter(
            status='Completed'
        ).filter(
            Q(team_a_members=user_profile) | Q(team_b_members=user_profile)
        ).distinct()  # Ensure no duplicate events

        # Serialize the events
        serializer = EventWithStatsSerializer(events, many=True, context={'request': request})

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)      


class CreateNoShowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract user_id and event_id from the request data
        user_id = request.data.get('user_id')
        event_id = request.data.get('event_id')

        # Validate that both user_id and event_id are provided
        if not user_id or not event_id:
            return Response({'error': 'Both user_id and event_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that user_id is a valid UUID
        try:
            user_uuid = uuid.UUID(user_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid user_id format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that event_id is a valid UUID
        try:
            event_uuid = uuid.UUID(event_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid event_id format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user profile
        try:
            user_profile = UserProfile.objects.get(id=user_uuid)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch the event
        try:
            event = Event.objects.get(id=event_uuid)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the authenticated user is the host of the event
        if request.user.userprofile != event.host:
            return Response({'error': 'Only the host can perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if a NoShow record already exists for the given user and event
        if NoShow.objects.filter(user=user_profile, event=event).exists():
            return Response({'error': 'NoShow record already exists for this user and event.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the NoShow record
        no_show = NoShow.objects.create(user=user_profile, event=event)

        # Return a success response
        return Response({'message': 'NoShow record created successfully.', 'id': str(no_show.id)}, status=status.HTTP_201_CREATED)


class KickUserFromEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract user_id and event_id from the request data
        user_id = request.data.get('user_id')
        event_id = request.data.get('event_id')

        # Validate that both user_id and event_id are provided
        if not user_id or not event_id:
            return Response({'error': 'Both user_id and event_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that user_id is a valid UUID
        try:
            user_uuid = uuid.UUID(user_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid user_id format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that event_id is a valid UUID
        try:
            event_uuid = uuid.UUID(event_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid event_id format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user profile
        try:
            user_profile = UserProfile.objects.get(id=user_uuid)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch the event
        try:
            event = Event.objects.get(id=event_uuid)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the authenticated user is the host of the event
        if request.user.userprofile != event.host:
            return Response({'error': 'Only the host can perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        # Remove the user from Team A and Team B
        if user_profile in event.team_a_members.all():
            event.team_a_members.remove(user_profile)
        if user_profile in event.team_b_members.all():
            event.team_b_members.remove(user_profile)

        # Add the user to the removed_players list
        event.removed_players.add(user_profile)

        # Save the event
        event.save()

        # Return a success response
        return Response({'message': f'User {user_profile.full_name} has been removed from the event and added to the removed players list.'}, status=status.HTTP_200_OK)


class GetUserAbsenceFlagView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract user_id from the request data
        user_id = request.data.get('user_id')

        # Validate that user_id is provided
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that user_id is a valid UUID
        try:
            user_uuid = uuid.UUID(user_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid user_id format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user profile
        try:
            user_profile = UserProfile.objects.get(id=user_uuid)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Calculate the date 30 days ago
        thirty_days_ago = datetime.now() - timedelta(days=30)

        # Count the number of absences for the user in the last 30 days
        absence_count = NoShow.objects.filter(user=user_profile, date__gte=thirty_days_ago).count()

        # Determine the flag based on the absence count
        if absence_count == 0:
            flag = "Green"  # No absences → active/engaged
        elif 4 <= absence_count <= 6:
            flag = "Yellow"  # Between 4 and 6 absences
        elif absence_count > 6:
            flag = "Red"  # More than 6 absences
        else:
            flag = "Green"  # Default to Green if no absences

        # Return the flag
        return Response({'user_id': str(user_profile.id), 'flag': flag}, status=status.HTTP_200_OK)

class GetUserAverageReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract user_id from the request data
        user_id = request.data.get('user_id')

        # Validate that user_id is provided
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that user_id is a valid UUID
        try:
            user_uuid = uuid.UUID(user_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid user_id format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user profile
        try:
            user_profile = UserProfile.objects.get(id=user_uuid)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch all reviews for the user as a host
        reviews = Review.objects.filter(host=user_profile)

        # Calculate the average rating and count the number of reviews
        if reviews.exists():
            average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
            review_count = reviews.count()
        else:
            average_rating = 0  # Default to 0 if no reviews exist
            review_count = 0  # Default to 0 if no reviews exist

        # Return the average rating and review count
        return Response({
            'user_id': str(user_profile.id),
            'average_rating': round(average_rating, 2),
            'review_count': review_count
        }, status=status.HTTP_200_OK)
    
class AddReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract data from the request
        user_id = request.data.get('user_id')  # Reviewer
        event_id = request.data.get('event_id')
        host_id = request.data.get('host_id')
        rating = request.data.get('rating')

        # Validate that all required fields are provided
        if not all([user_id, event_id, host_id, rating]):
            return Response({'error': 'user_id, event_id, host_id, and rating are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that user_id, event_id, and host_id are valid UUIDs
        try:
            user_uuid = uuid.UUID(user_id, version=4)
            event_uuid = uuid.UUID(event_id, version=4)
            host_uuid = uuid.UUID(host_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid UUID format for user_id, event_id, or host_id.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the reviewer (user)
        try:
            reviewer = UserProfile.objects.get(id=user_uuid)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Reviewer not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch the event
        try:
            event = Event.objects.get(id=event_uuid)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch the host
        try:
            host = UserProfile.objects.get(id=host_uuid)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Host not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Validate the rating
        try:
            rating = float(rating)
            if not (1.0 <= rating <= 5.0):
                return Response({'error': 'Rating must be between 1.0 and 5.0.'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Rating must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a review already exists for this user, event, and host
        if Review.objects.filter(reviewer=reviewer, event=event, host=host).exists():
            return Response({'error': 'A review for this user, event, and host already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the review
        try:
            review = Review.objects.create(
                host=host,
                reviewer=reviewer,
                event=event,
                rating=rating
            )
            return Response({'message': 'Review added successfully.', 'review_id': str(review.id)}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        




class CreateNewCategoryView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def post(self, request, *args, **kwargs):
        # Check if name is provided
        if 'name' not in request.data or not request.data['name']:
            return Response(
                {'error': 'Category name is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Create a copy of the data to modify
        data = request.data.copy()
        
        # If no image is provided, create a default image
        if 'image' not in data:
            # Create a simple text file as a default image
            from django.core.files.base import ContentFile
            from PIL import Image
            import io
            
            # Create a blank image
            img = Image.new('RGB', (100, 100), color='white')
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            
            # Create a ContentFile from the image
            data['image'] = ContentFile(img_io.getvalue(), name='default_category.png')
            
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IncreaseAllViewsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Increment views for all posts
        Post.objects.all().update(views=models.F('views') + 1)
        # Increment views for all reposts
        Repost.objects.all().update(views=models.F('views') + 1)
        return Response({'status': 'All post and repost views incremented by 1.'}, status=status.HTTP_200_OK)


class SavePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        post_id = request.data.get('post_id')

        if not post_id:
            return Response({'error': 'post_id is required.'}, status=status.HTTP_400_BAD_REQUEST)


        # Validate UUID format
        try:
            uuid.UUID(post_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid post_id format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Toggle save status
        if user_profile.saved_posts.filter(id=post_id).exists():
            # Post is already saved, so unsave it
            user_profile.saved_posts.remove(post)
            return Response({'status': 'Post unsaved successfully.'}, status=status.HTTP_200_OK)
        else:
            # Post is not saved, so save it
            user_profile.saved_posts.add(post)
            return Response({'status': 'Post saved successfully.'}, status=status.HTTP_200_OK)


class SaveRepostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        repost_id = request.data.get('repost_id')

        if not repost_id:
            return Response({'error': 'repost_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUID format
        try:
            uuid.UUID(repost_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid repost_id format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            repost = Repost.objects.get(id=repost_id)
        except Repost.DoesNotExist:
            return Response({'error': 'Repost not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Toggle save status
        if user_profile.saved_reposts.filter(id=repost_id).exists():
            # Repost is already saved, so unsave it
            user_profile.saved_reposts.remove(repost)
            return Response({'status': 'Repost unsaved successfully.'}, status=status.HTTP_200_OK)
        else:
            # Repost is not saved, so save it
            user_profile.saved_reposts.add(repost)
            return Response({'status': 'Repost saved successfully.'}, status=status.HTTP_200_OK)






class CheckEmailExistsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        # Check in both User and UserProfile (in case of different registration logic)
        user_exists = User.objects.filter(email=email).exists()
        userprofile_exists = False
        try:
            from .models import UserProfile
            userprofile_exists = UserProfile.objects.filter(email=email).exists()
        except Exception:
            pass
        exists = user_exists or userprofile_exists
        return Response({'exists': exists}, status=status.HTTP_200_OK)



class GetSavedItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        saved_posts = user_profile.saved_posts.filter(is_reported=False, is_published=True)
        saved_reposts = user_profile.saved_reposts.filter(is_reported=False)

        post_serializer = PostSerializer(saved_posts, many=True, context={'request': request})
        repost_serializer = RepostSerializer(saved_reposts, many=True, context={'request': request})

        return Response({
            'post': post_serializer.data,
            'repost': repost_serializer.data
        }, status=status.HTTP_200_OK)


class DeleteRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Create a delete request for the authenticated user's profile
        """
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user already has a pending delete request
        existing_request = DeleteRequest.objects.filter(
            user_profile=user_profile, 
            status='pending'
        ).first()
        
        if existing_request:
            return Response({
                "error": "You already have a pending delete request. Please wait for it to be processed."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = DeleteRequestCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Create the delete request
            delete_request = serializer.save(user_profile=user_profile)
            
            # Return the full delete request data
            response_serializer = DeleteRequestSerializer(delete_request)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """
        Get the authenticated user's delete request status
        """
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

        delete_request = DeleteRequest.objects.filter(user_profile=user_profile).first()
        
        if not delete_request:
            return Response({"message": "No delete request found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DeleteRequestSerializer(delete_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


def relationStatus(uuid_param, request):
    """
    Check if the authenticated sender is following the user with the given UUID.
    
    Args:
        uuid_param: UUID of the target user to check
        request: Django request object (must have authenticated user)
    
    Returns:
        bool: True if sender is following the user with the given UUID, False otherwise
    """
    try:
        # Get the authenticated sender from the request
        sender = request.user.userprofile
    except (AttributeError, UserProfile.DoesNotExist):
        # Return False if user is not authenticated or profile doesn't exist
        return False
    
    try:
        # Convert uuid_param to UUID if it's a string
        if isinstance(uuid_param, str):
            target_uuid = UUID(uuid_param)
        else:
            target_uuid = uuid_param
        
        # Get the target user profile
        target_user = UserProfile.objects.get(id=target_uuid)
        
        # Check if the sender is following the target user
        return target_user in sender.following.all()
    except (UserProfile.DoesNotExist, ValueError, TypeError):
        # Return False if user doesn't exist or UUID is invalid
        return False


class RelationStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Check if the authenticated user is following the user with the given UUID.
        
        Expected request body:
        {
            "user_id": "uuid-string"
        }
        """
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate UUID format
        try:
            UUID(user_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid user_id format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use the relationStatus function
        is_following = relationStatus(user_id, request)
        
        return Response({
            'user_id': user_id,
            'is_following': is_following
        }, status=status.HTTP_200_OK)


class AmITheEventHostView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Check if the authenticated user is the host of the event with the given event ID.
        
        Expected request body:
        {
            "event_id": "uuid-string"
        }
        """
        event_id = request.data.get('event_id')
        
        if not event_id:
            return Response({'error': 'event_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate UUID format
        try:
            event_uuid = UUID(event_id, version=4)
        except ValueError:
            return Response({'error': 'Invalid event_id format. Must be a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get the authenticated sender from the request
            sender = request.user.userprofile
        except (AttributeError, UserProfile.DoesNotExist):
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Get the event
            event = Event.objects.get(id=event_uuid)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the sender is the host of the event
        is_host = sender == event.host
        
        return Response({
            'event_id': event_id,
            'is_host': is_host
        }, status=status.HTTP_200_OK)


def index(request):
    pass 