
from itertools import count
from venv import logger
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum, Count
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from property.serializers import UnitSerializer
from utils.permissions import IsAdminOrPropertyManager
from .serializers import PaymentSerializer
import logging
import decimal

from a_users import models
from property.models import Property, Unit
from tenant.models import Payment

from .serializers import CustomUserSerializer,  RegisterSerializer, LoginSerializer
from utils.permissions import IsAdminOrPropertyManager
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    # Optimize the query to avoid N+1 problem
    user = models.CustomUser.objects.select_related().prefetch_related(
        'tenant_profile__unit__property'
    ).get(id=request.user.id)
    
    serializer = CustomUserSerializer(user)
    return Response(serializer.data, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payments(request):
    try:
        user = request.user
        logger.debug(f"Fetching payments for user {user.email}")

        # Filter payments based on user role
        if user.role == 'admin':
            payments = Payment.objects.all()
        else:
            payments = Payment.objects.filter(
                models.Q(unit__property__owner=user) | models.Q(unit__property__manager=user)
            )

        serializer = PaymentSerializer(payments, many=True)
        logger.info(f"Retrieved {len(serializer.data)} payments for user {user.email}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error retrieving payments for user {user.email}: {str(e)}")
        return Response(
            {"detail": f"Failed to retrieve payments: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdminOrPropertyManager])
def update_unit_rent(request, unit_id):
    try:
        user = request.user
        logger.debug(f"Updating unit rent for unit_id={unit_id} by user {user.email}")

        # Fetch unit
        unit = Unit.objects.get(id=unit_id)
        
        # Check permissions
        if user.role != 'admin' and unit.property.owner != user and unit.property.manager != user:
            return Response(
                {"detail": "You do not have permission to update this unit."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update rent
        rent = request.data.get('rent')
        if rent is None:
            return Response(
                {"detail": "Rent value is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            unit.rent = float(rent)
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid rent value. Must be a number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        unit.save()
        serializer = UnitSerializer(unit)
        logger.info(f"Updated unit rent for unit_id={unit_id} to {unit.rent} by user {user.email}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Unit.DoesNotExist:
        logger.error(f"Unit not found for unit_id={unit_id}")
        return Response(
            {"detail": "Unit not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error updating unit rent for unit_id={unit_id}: {str(e)}")
        return Response(
            {"detail": f"Failed to update unit rent: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": CustomUserSerializer(user).data,
            "message": "User registered successfully"
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            refresh['username'] = user.username
            refresh['role'] = user.role
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': CustomUserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)