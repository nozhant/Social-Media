from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from datetime import datetime

from response_management.EMS import *

from message.serializers import *


class ConversationCreate(APIView):
    """Allows user to create new conversation"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        request_json = {
            'users': request.data.get('users_id'),
            'creator': request.user.id
        }

        conversation_serialized = ConversationSerializer(data=request_json, partial=True)
        if not conversation_serialized.is_valid():
            return validate_error(conversation_serialized)

        conversation_serialized.save()

        response_json = {
            'status': True,
            'message': 'successful',
            'data': conversation_serialized.data.get('id')
        }

        return Response(response_json, status=201)


class ConversationList(APIView):
    """Shows List of all conversion that user is sender or recipient"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        conversation_objs = Conversation.objects.filter(users=request.user.id)
        if conversation_objs == []:
            return existence_error('conversation')

        conversation_serialized = ConversationSerializer(conversation_objs, many=True)

        response_json = {
            'status': True,
            "message": "successful",
            'data': conversation_serialized.data
        }

        return Response(response_json, status=200)


class ConversationEdit(APIView):
    """Allows user to Add users to a conversation or remove from it"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):  # add a new user to conversation

        conversation_obj = Conversation.objects.filter(id=request.data.get('conversation_id')).first()
        if conversation_obj is None:
            return existence_error('conversation')

        conversation_serialized = ConversationSerializer(conversation_obj)
        conversation_users = conversation_serialized.data.get('users')
        conversation_creator = conversation_serialized.data.get('creator')

        if request.user.id == conversation_creator:

            conversation_users.append(request.data.get('user_id'))

            # update conversation with new users
            request_json = {
                'users': conversation_users,
            }

            conversation_update_serialized = ConversationSerializer(conversation_obj, data=request_json, partial=True)
            if not conversation_update_serialized.is_valid():
                return validate_error(conversation_update_serialized)
            conversation_update_serialized.save()

            return Response({'status': True, "message": "successful", "data": ''}, status=200)

        else:
            return Response({"status": False, "message": "You are not this conversation's creator", "data": ''}, status=201)

    def patch(self, request):  # remove a user from a conversation

        conversation_obj = Conversation.objects.filter(id=request.data.get('conversation_id')).first()
        if conversation_obj is None:
            return existence_error('conversation')

        conversation_serialized = ConversationSerializer(conversation_obj)
        conversation_users = conversation_serialized.data.get('users')
        conversation_creator = conversation_serialized.data.get('creator')

        if request.user.id == conversation_creator:

            conversation_users.remove(request.data.get('user_id'))

            # update conversation with new users
            request_json = {
                'users': conversation_users,
            }

            conversation_update_serialized = ConversationSerializer(conversation_obj, data=request_json, partial=True)
            if not conversation_update_serialized.is_valid():
                return validate_error(conversation_update_serialized)
            conversation_update_serialized.save()

            return Response({'status': True, "message": "successful", "data": ''}, status=200)

        else:
            return Response({"status": False, "message": "You are not this conversation's creator", "data": ''}, status=201)


class SendMessage(APIView):
    """Allows user to send messages"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):

        request_json = {
            'conversation': request.data.get('conversation_id'),
            'message_creator': request.user.id,
            'body': request.data.get('body'),
            'time': datetime.timestamp(timezone.now())
        }

        conversation_obj = Conversation.objects.filter(id=request.data.get('conversation_id')).first()
        if conversation_obj is None:
            return existence_error('conversation')

        conversation_serialized = ConversationSerializer(conversation_obj)
        conversation_users = conversation_serialized.data.get('users')

        if request.user.id not in conversation_users:
            return Response({'status': False, 'message': 'this conversation is not for you', "data": ''}, status=400)

        message_serialized = MessageSerializer(data=request_json, partial=True)
        if not message_serialized.is_valid():
            return validate_error(message_serialized)
        message_serialized.save()

        # update conversation last message info
        update_json = {
            'last_message_body': request.data.get('body'),
            'last_message': message_serialized.data.get('time')
        }

        conversation_serialized = ConversationSerializer(conversation_obj, data=update_json, partial=True)
        if not conversation_serialized.is_valid():
            return validate_error(conversation_serialized)
        conversation_serialized.save()

        return Response({'status': True, "message": "successful", "data": ''}, status=201)


class ConversationMessages(APIView):
    """List all message in a conversation"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        conversation_id = request.data.get('conversation_id')

        # check is current user joined in conversion
        conversation_obj = Conversation.objects.filter(id=conversation_id)
        if conversation_obj is None:
            return existence_error('conversation')
        conversation_serialized = ConversationSerializer(conversation_obj)
        conversation_users = conversation_serialized.data.get('users')
        if request.user.id not in conversation_users:
            return Response({'status': False, 'message': 'this conversation is not for you'}, status=200)

        # users = Conversation.objects.exclude(user=userId)
        serializer = ConversationSerializer(conversation_obj, many=True)
        return successful_response(serializer.data)


class MessageSeen(APIView):
    """Show unseen  messages and make them seen"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):

        message_objs = Message.objects.filter(conversation=request.data.get('conversation_id')).exclude(
            users_seen=request.user.id)
        if message_objs == []:
            return existence_error('message')

        message_serialized = MessageSerializer(message_objs, many=True)

        for item in message_serialized.data:
            message_obj = Message.objects.filter(id=item['id']).first()
            if message_obj is None:
                return existence_error('message')
            message_obj_serialized = MessageSerializer(message_obj)
            message_users_seen = message_obj_serialized.data.get('users_seen')

            message_users_seen.append(request.user.id)

            #  update message users seen with this new user
            request_json = {
                'users_seen': message_users_seen
            }

            message_update_serialized = MessageSerializer(message_obj, data=request_json, partial=True)
            if not message_update_serialized.is_valid():
                return validate_error(message_update_serialized)
            message_update_serialized.save()

        response_json = {
            'data': message_serialized.data,
            'status': True,
            "message": "successful"
        }
        return Response(response_json, status=200)

