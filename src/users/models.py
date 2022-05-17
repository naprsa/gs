from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from uuid import uuid4

from .managers import UserManager
from .model_fields import LowercaseEmailField


class AuthProvider(models.Model):
    CHOICES = ((1, "Apple"), (2, "Google"))
    name = models.CharField("Provider", max_length=50)
    uid = models.TextField("Provider user uid")

    class Meta:
        verbose_name = "AuthProvider"
        verbose_name_plural = "AuthProviders"

    def __str__(self):
        """Unicode representation of AuthProvider."""
        return self.name


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    uid = models.UUIDField(default=uuid4)
    provider = models.ForeignKey(
        AuthProvider,
        verbose_name=_("Auth provider"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
    )
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=False,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        blank=True,
        default="",
    )
    email = LowercaseEmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)
    is_active = models.BooleanField(_("active"), default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        if self.first_name:
            return self.first_name
        else:
            return self.email.split("@")[0]

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)
