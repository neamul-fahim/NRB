from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, OtpVerification, RegistrationProfile, JobProfile
from .serializers import OtpVerificationSerializer, AuthSerializer, CustomUserModelSerializer, RegistrationProfileSerializer, JobProfileSerializer
from .utility import send_email, get_token_from_request, country_code, designations


class OtpVerificationView(APIView):

    def post(self, request):  # email,password,is_client/is_freelancer
        raw_user_data = request.data
        try:
            # checking if user has already registered
            user = CustomUser.objects.get(email=raw_user_data['email'])

            return Response({'message': "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            try:
                instance = OtpVerification.objects.get(
                    email=raw_user_data['email'])
                serializer = OtpVerificationSerializer(
                    instance=instance, data=raw_user_data)
            except:
                serializer = OtpVerificationSerializer(data=raw_user_data)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "OTP sent"}, status=status.HTTP_200_OK)


class UserAccountView(APIView):

    def post(self, request, *args, **kwargs):  # email,otp
        raw_user_data = request.data

        try:
            instance = OtpVerification.objects.get(
                email=raw_user_data['email'])
            if instance.otp == raw_user_data['otp']:
                instance = CustomUser.objects.model(
                    email=instance.email,
                    password=instance.password,
                    is_client=instance.is_client,
                )
                instance.save()
                message = 'You have signed up to ipsita'
                send_email(instance.email, message)
                return Response({"message": "Signed up"}, status=status.HTTP_200_OK)
            else:
                return Response("Otp didn't match", status=status.HTTP_400_BAD_REQUEST)

        except OtpVerification.DoesNotExist:
            return Response("Otp verification is not complete", status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request):  # token
        """get the user by token"""
        token = get_token_from_request(request)

        if token is None:
            return Response('Invalid token', status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = Token.objects.get(key=token).user
            print(f"---------------user 1---------------{user}")
        except Token.DoesNotExist:
            return Response('Invalid Token', status=status.HTTP_401_UNAUTHORIZED)

        user_data = {
            'email': user.email,
            'is_client': user.is_client,
            'is_freelancer': user.is_freelancer,
        }
        return Response(user_data, status=status.HTTP_200_OK)

    def patch(self, request):  # email,password
        token = get_token_from_request(request)
        raw_user_data = request.data

        if token is None:
            return Response('Invalid token', status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = Token.objects.get(key=token).user
            print(f"---------------user 1---------------{user}")
        except Token.DoesNotExist:
            return Response('Invalid Token', status=status.HTTP_401_UNAUTHORIZED)

        try:
            CustomUser.objects.get(email=raw_user_data['email'])
            return Response('User already exists', status=status.HTTP_400_BAD_REQUEST)
        except:
            serializer = CustomUserModelSerializer(
                instance=user, data=raw_user_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response('Login info updated', status=status.HTTP_200_OK)


class CreateTokenView(APIView):
    """create and get token on user login"""

    def post(self, request, *args, **kwargs):  # email,password

        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        Token.objects.filter(user=user).delete()

        # Create a new token
        token = Token.objects.create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class RegistrationAndJobProfileView(APIView):
    """register signed up users"""

    def post(self, request):
        token = get_token_from_request(request)
        raw_user_data = request.data

        if token is None:
            return Response('Invalid token', status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = Token.objects.get(key=token).user
            print(f"---------------user 1---------------{user}")
        except Token.DoesNotExist:
            return Response('Invalid Token', status=status.HTTP_401_UNAUTHORIZED)
        raw_user_data['user'] = user.pk
        reg_serializer = RegistrationProfileSerializer(data=raw_user_data)
        reg_serializer.is_valid(raise_exception=True)
        job_serializer = JobProfileSerializer(data=raw_user_data)
        job_serializer.is_valid(raise_exception=True)
        reg_serializer.save()
        job_serializer.save()

        return Response('registration complete', status=status.HTTP_200_OK)


class RegistrationProfileView(APIView):
    def post(self, request):
        token = get_token_from_request(request)

        if token is None:
            return Response('No token', status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = Token.objects.get(key=token).user
            print(f"---------------user 1---------------{user}")
        except Token.DoesNotExist:
            return Response('Invalid Token', status=status.HTTP_401_UNAUTHORIZED)
        print(f'-------------token---------- {user.pk}')

        try:
            user_profile = RegistrationProfile.objects.get(user=user)
            print(
                f"-------------------------user_profile------------------{user_profile}")
            serializer = RegistrationProfileSerializer(user_profile)
            serialized_data = serializer.data

            return Response({'exists': True, 'response': serialized_data}, status=status.HTTP_200_OK)
        except:
            return Response({'exists': False, 'response': 'registration in not complete'}, status=status.HTTP_200_OK)


class JobProfileView(APIView):
    def get(self, request):
        token = get_token_from_request(request)

        if token is None:
            return Response('Invalid token', status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = Token.objects.get(key=token).user
            print(f"---------------user 1---------------{user}")
        except Token.DoesNotExist:
            return Response('Invalid Token', status=status.HTTP_401_UNAUTHORIZED)
        print(f'-------------token---------- {user.pk}')

        try:
            job_instance = JobProfile.objects.filter(user=user)
            print(
                f"-------------------------user_profile------------------{job_instance}")
            serializer = JobProfileSerializer(job_instance, many=True)
            serialized_data = serializer.data

            return Response(serialized_data, status=status.HTTP_200_OK)
        except RegistrationProfile.DoesNotExist:
            return Response('Profile does not exist', status=status.HTTP_404_NOT_FOUND)


class ProfilePicUploadView(APIView):
    def patch(self, request):
        token = get_token_from_request(request)

        if token is None:
            return Response('Invalid token', status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = Token.objects.get(key=token).user
            print(f"---------------user 1---------------{user}")
        except Token.DoesNotExist:
            return Response('Invalid Token', status=status.HTTP_401_UNAUTHORIZED)
        print(f'-------------token---------- {user.pk}')

        try:
            instance = RegistrationProfile.objects.get(user=user)
            serializer = RegistrationProfileSerializer(
                instance=instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"response": "Image uploaded"}, status=status.HTTP_200_OK)
        except:
            return Response({"reaponse": "Please complete registration"}, status=status.HTTP_400_BAD_REQUEST)


class CountryCodeView(APIView):
    def get(self, request):
        country_name = []
        name_code = {}
        print("-------------")

        countries = country_code()
        print("-----------------------------------")
        for country in countries:
            name = country[0]
            code = country[1]
            country_name.append(name)
            name_code[name] = code
            print(
                f"-----------country ----------{name} ------- {name_code[name]}")

        return Response({"country_name": country_name, "name_code": name_code}, status=status.HTTP_200_OK)


class Designations(APIView):
    def get(self, request):
        des = designations()
        return Response({"designations": des}, status=status.HTTP_200_OK)
