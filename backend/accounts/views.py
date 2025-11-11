from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile
from .serializers import SignupSerializer, ProfileSerializer, ChangePasswordSerializer


def _tokens_for_user(user: User):
	refresh = RefreshToken.for_user(user)
	return {"refresh": str(refresh), "access": str(refresh.access_token)}


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
	serializer = SignupSerializer(data=request.data)
	if serializer.is_valid():
		with transaction.atomic():
			user = serializer.save()
		tokens = _tokens_for_user(user)
		return Response(tokens, status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def profile_view(request):
	profile = request.user.profile
	if request.method == "GET":
		data = ProfileSerializer(profile).data
		return Response(data)

	serializer = ProfileSerializer(profile, data=request.data, partial=True)
	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_account(request):
	request.user.delete()
	return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
	serializer = ChangePasswordSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	old_password = serializer.validated_data["old_password"]
	new_password = serializer.validated_data["new_password"]

	if not request.user.check_password(old_password):
		return Response({"old_password": ["Incorrect password"]}, status=status.HTTP_400_BAD_REQUEST)

	request.user.set_password(new_password)
	request.user.save()
	return Response({"detail": "Password changed successfully"})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def password_reset(request):
	# Stub endpoint for sending reset email
	email = request.data.get("email")
	if not email:
		return Response({"email": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
	# Pretend success
	return Response({"detail": "If an account exists for this email, a reset link was sent."})


