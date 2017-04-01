from django.db import models
from reuserat.users.models import User




class FAQCategory(models.Model):
    name = models.CharField(max_length=80)
    priority = models.IntegerField(default=100)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('-priority',)


class FAQ(models.Model):
    category = models.ManyToManyField(FAQCategory)
    question =  models.CharField(max_length=250)
    answer = models.CharField(max_length=1000)
    priority = models.IntegerField(default=100)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # Increase the text box size for answer field

    def __str__(self):
        return self.question

    class Meta:
        ordering = ('-priority',)
