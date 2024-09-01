from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

KENYA_TOWNS = [
    ('Nairobi', 'Nairobi'),
    ('Mombasa', 'Mombasa'),
    ('Kisumu', 'Kisumu'),
    ('Nakuru', 'Nakuru'),
    ('Eldoret', 'Eldoret'),
    # Add more towns as needed
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    phone_number = models.CharField(max_length=15, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True)
    location_type = models.CharField(max_length=50, blank=True, choices=[('Village', 'Village'), ('Town', 'Town')])
    town_name = models.CharField(max_length=100, blank=True, choices=KENYA_TOWNS)
    has_children = models.BooleanField(default=False)
    number_of_children = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def age(self):
        if self.birthdate:
            today = date.today()
            return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        return None

class Member(models.Model):
    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    birthdate = models.DateField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    location_type = models.CharField(
        max_length=10,
        choices=[('village', 'Village'), ('town', 'Town')],
        default='Unknown'
    )
    town_name = models.CharField(max_length=100, null=True, blank=True)
    has_children = models.BooleanField(null=True, blank=True)
    number_of_children = models.PositiveIntegerField(null=True, blank=True)
    date_of_registration = models.DateField(default=date.today, editable=False, null=True)

    def age(self):
        if self.birthdate:
            today = date.today()
            return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        return None

    age.short_description = 'Age'  # This gives a name to the column in the admin

    def __str__(self):
        return f"{self.surname}, {self.first_name} {self.last_name}"
class Event(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    required_amount = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)

    def __str__(self):
        return self.name

class Contribution(models.Model):
    member = models.ForeignKey(Member, related_name='contributions', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='contributions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_member_status()

    def update_member_status(self):
        contributions = self.member.contributions.filter(event__date__gte=self.member.date_of_registration)
        if contributions.exists():
            total_contributed = sum(contrib.amount for contrib in contributions)
            required_total = sum(contrib.event.required_amount for contrib in contributions)

            if total_contributed >= required_total:
                self.member.status = 'Super Member'
            elif total_contributed > 0:
                self.member.status = 'Active Member'
            else:
                self.member.status = 'Dormant Member'
        else:
            self.member.status = 'Dormant Member'
        self.member.save()

    @property
    def category(self):
        if self.amount >= self.event.required_amount:
            return 'Fully Contributed'
        elif 0 < self.amount < self.event.required_amount:
            return 'Partially Contributed'
        else:
            return 'No Contribution'

    def __str__(self):
        return f"{self.member} - {self.event}: {self.amount} Ksh"
