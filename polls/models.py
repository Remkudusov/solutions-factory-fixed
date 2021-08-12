from django.db import models
from django.contrib.postgres.fields import ArrayField

class Poll(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    start_date = models.DateField()
    finish_date = models.DateField()

    def __str__(self):
        return self.name

class Question(models.Model):
    id = models.AutoField(primary_key=True)
    poll_id = models.IntegerField()
    text = models.CharField(max_length=500)
    type = models.IntegerField(choices=[(0, "text"), (1, "one in some"), (2, "some in some")]) # 0 - text answer, 1 - choose one variant, 2 - choose some variants

    def __str__(self):
        return self.text

class Variant(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.IntegerField()
    question_id = models.IntegerField()
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text

class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    question_id = models.IntegerField()
    user_id = models.IntegerField(null=True)
    variants_numbers = ArrayField(models.IntegerField(), null=True, blank=True)
    text = models.CharField(null=True, max_length=500, blank=True)

    def __str__(self):
        return str(self.question_id)