from django.db import models
from django.contrib.auth.models import AbstractUser
from busstop_project.model_utils.models import TimeStampedModel 

class CustomUser(AbstractUser, TimeStampedModel):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'  # login with username
    REQUIRED_FIELDS = ['email']   # email is required when creating superuser



from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailVerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification code for {self.user.email}"
