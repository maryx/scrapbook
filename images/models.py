import datetime

from django.utils import timezone
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible # I'm on 2.7
class Images(models.Model):
    date_added = models.DateTimeField('Date Added')
    img_source = models.CharField(max_length=400)
    tags = models.CharField(max_length=200)
    nsfw_probability = models.IntegerField(default=0)

    # This is used in the admin thing too
    def __str__(self):
        return self.img_source

    def is_recent(self):
        return self.date_added >= timezone.now() - datetime.timedelta(days=1)
