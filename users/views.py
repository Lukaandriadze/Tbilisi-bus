from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from datetime import timedelta
import random

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import status, response

from users.models import CustomUser, EmailVerificationCode
from users.serializers import RegisterSerializer, EmailCodeResendSerializer, EmailCodeConfirmSerializer
from users.tasks import send_email_async


class UserLoginView(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("/")
            else:
                return render(
                    request,
                    "login.html",
                    {"error_message": "მომხმარებელი არაა აქტიური. გთხოვთ დაადასტურეთ თქვენი ელ-ფოსტა."},
                )
        return render(
            request,
            "login.html",
            {"error_message": "მომხმარებლის სახელი ან პაროლი არასწორია."},
        )


class UserRegisterView(View):
    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
        }
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            self.send_verification_code(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            return redirect(f'/confirm_code/{uid}/{token}/')
        return render(request, "register.html", {"errors": serializer.errors})

    def send_verification_code(self, user):
        existing_code = EmailVerificationCode.objects.filter(user=user).first()
        if existing_code and (timezone.now() - existing_code.created_at) < timedelta(minutes=10):
            return

        code = str(random.randint(100000, 999999))
        EmailVerificationCode.objects.update_or_create(
            user=user, defaults={"code": code, "created_at": timezone.now()}
        )
        subject = "Your verification code"
        message = f"Hello {user.username}, your verification code is {code}"
        send_email_async.delay(subject, message, user.email)


class EmailConfirmView(View):
    def get(self, request, uidb64=None, token=None):
        context = {"validlink": False}
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                context.update({
                    "validlink": True,
                    "uidb64": uidb64,
                    "token": token
                })
        except (CustomUser.DoesNotExist, ValueError, TypeError):
            pass

        return render(request, "confirm_code.html", context)

    def post(self, request, uidb64=None, token=None):
        code = request.POST.get("code")
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
            evc = EmailVerificationCode.objects.get(user=user)

            if evc.code == code and default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                evc.delete()
                login(request, user)
                return redirect("/")
            else:
                raise ValueError("Invalid code or token")

        except (CustomUser.DoesNotExist, EmailVerificationCode.DoesNotExist, ValueError):
            return render(
                request,
                "confirm_code.html",
                {
                    "error_message": "ვერიფიკაციის კოდი არასწორია ან ვალიდაცია ვერ გაიარა",
                    "validlink": True,
                    "uidb64": uidb64,
                    "token": token,
                },
            )


class EmailVerificationViewSet(GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = None

    def send_verification_code(self, user):
        existing_code = EmailVerificationCode.objects.filter(user=user).first()
        if existing_code and (timezone.now() - existing_code.created_at) < timedelta(minutes=1):
            return

        code = str(random.randint(100000, 999999))
        EmailVerificationCode.objects.update_or_create(
            user=user, defaults={"code": code, "created_at": timezone.now()}
        )
        subject = "Your verification code"
        message = f"Hello {user.username}, your verification code is {code}"
        send_email_async.delay(subject, message, user.email)

    @action(
        detail=False,
        methods=["POST"],
        url_path="resend_code",
        serializer_class=EmailCodeResendSerializer,
    )
    def resend_code(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        existing_code = EmailVerificationCode.objects.filter(user=user).first()
        if existing_code:
            time_diff = timezone.now() - existing_code.created_at
            if time_diff < timedelta(minutes=1):
                wait_seconds = 60 - int(time_diff.total_seconds())
                return response.Response(
                    {"detail": f"დაელოდე {wait_seconds} წამი, ხელახლა გასაგზავნად"},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        self.send_verification_code(user)
        return response.Response({"message": "ვერიფიკაციის კოდი ხელახლა გაიგზავნა"})

    @action(
        detail=False,
        methods=["POST"],
        url_path="confirm_code",
        serializer_class=EmailCodeConfirmSerializer,
    )
    def confirm_code(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        user.is_active = True
        user.save()
        EmailVerificationCode.objects.filter(user=user).delete()

        return response.Response(
            {"message": "მომხმარებელი წარმატებით გააქტიურდა"},
            status=status.HTTP_200_OK,
        )


def index(request):
    return render(request, 'index.html')
