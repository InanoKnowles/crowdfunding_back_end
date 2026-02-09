from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Fundraiser(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal = models.IntegerField()
    image = models.URLField()
    is_open = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)

    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="owned_fundraisers",
    )

    def __str__(self):
        return self.title

    def total_pledged(self):
        return self.pledges.aggregate(total=Sum("amount"))["total"] or 0

    def is_deadline_passed(self):
        return self.deadline is not None and timezone.now() >= self.deadline

    def is_goal_reached(self):
        return self.total_pledged() >= self.goal

    def is_accepting_pledges(self):
        return self.is_open and not self.is_deadline_passed() and not self.is_goal_reached()

    def days_left(self):
        if self.deadline is None:
            return None
        delta = self.deadline - timezone.now()
        return max(delta.days, 0)

    def refresh_open_status(self, save=True):
        should_close = self.is_goal_reached() or self.is_deadline_passed()
        if should_close and self.is_open:
            self.is_open = False
            if save:
                self.save(update_fields=["is_open"])
            return True
        return False


class Pledge(models.Model):
    amount = models.IntegerField()
    fundraiser = models.ForeignKey(
        Fundraiser,
        on_delete=models.CASCADE,
        related_name="pledges",
    )
    supporter = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="pledges",
    )
    anonymous = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} to {self.fundraiser}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.fundraiser.refresh_open_status(save=True)


class Comment(models.Model):
    fundraiser = models.ForeignKey(
        Fundraiser,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="comments",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    content = models.TextField()
    anonymous = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:30]
