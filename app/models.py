from django.db import models

import datetime


# Create your models here.


class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class Category(TimeStamp):
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "%s" % self.name

    def __unicode__(self):
        return self.name


class Channel(TimeStamp):
    title = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    link_m3u8 = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, blank=True, null=True, on_delete=models.CASCADE)
    custom_m3u8 = models.TextField(blank=True, null=True)
    program_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title
