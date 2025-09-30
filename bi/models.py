from django.db import models
from django.contrib.auth.models import User
# Create your models here.

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"user_{instance.user.username}.{ext}"
    return f'avatars/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            this = Profile.objects.get(id=self.id)
            if this.avatar and this.avatar != self.avatar:
                this.avatar.delete(save=False)  # elimina la anterior
        except Profile.DoesNotExist:
            pass
        super().save(*args, **kwargs)