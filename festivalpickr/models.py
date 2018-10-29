from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=254, blank=True, null=True)
    state = models.CharField(max_length=13, blank=True, null=True)
    city = models.CharField(max_length=85, blank=True, null=True)
    zip = models.PositiveIntegerField(blank=True, null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Festival(models.Model):
    name=models.CharField(unique=True,max_length=100,db_index=True)
    price=models.FloatField(blank=True,null=True,validators=[MinValueValidator(0)])
    latitude=models.FloatField(blank=True,null=True,db_index=True)
    longitude=models.FloatField(blank=True,null=True,db_index=True)
    def __str__(self):
        return self.name
class Band(models.Model):
    name=models.CharField(unique=True,max_length=300,db_index=True)
    songkickid=models.BigIntegerField(blank=True,null=True)
    festivals=models.ManyToManyField(Festival,related_name='bands')
    def __str__(self):
        return self.name
