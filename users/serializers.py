from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from users.models import EmailVerificationCode
from django.utils import timezone
import random

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False  # Inactive until verified
        )

        # Remove old codes if exist
        EmailVerificationCode.objects.filter(user=user).delete()

        # Generate new 6-digit code
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        EmailVerificationCode.objects.create(user=user, code=code, created_at=timezone.now())

        # Send code via email
        from django.core.mail import send_mail
        send_mail(
            "Verify Your Account",
            f"Your verification code is: {code}",
            "noreply@example.com",
            [user.email],
            fail_silently=False,
        )

        return user


class EmailCodeConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError("Invalid user.")

        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid or expired token.")

        try:
            code_obj = EmailVerificationCode.objects.get(user=user, code=data['code'])
        except EmailVerificationCode.DoesNotExist:
            raise serializers.ValidationError("Invalid verification code.")

        # Optional expiration check (10 minutes)
        if timezone.now() - code_obj.created_at > timezone.timedelta(minutes=10):
            raise serializers.ValidationError("Verification code has expired.")

        data['user'] = user
        return data


class EmailCodeResendSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError("Invalid user.")

        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid or expired token.")

        # Optional cooldown check (1 min)
        last_code = EmailVerificationCode.objects.filter(user=user).first()
        if last_code and timezone.now() - last_code.created_at < timezone.timedelta(minutes=1):
            seconds_left = 60 - int((timezone.now() - last_code.created_at).total_seconds())
            raise serializers.ValidationError(f"Please wait {seconds_left} seconds before resending the code.")

        data['user'] = user
        return data

    def create_code_and_send(self):
        user = self.validated_data['user']

        # Delete old code
        EmailVerificationCode.objects.filter(user=user).delete()

        # Generate new code
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        EmailVerificationCode.objects.create(user=user, code=code, created_at=timezone.now())

        # Send code via email
        from django.core.mail import send_mail
        send_mail(
            "Your New Verification Code",
            f"Here is your new code: {code}",
            "noreply@example.com",
            [user.email],
            fail_silently=False,
        )
