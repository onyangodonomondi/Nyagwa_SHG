from django.db import models
from datetime import date

# Define KENYA_TOWNS as a list of tuples
KENYA_TOWNS = [
    ('Nairobi', 'Nairobi'),
    ('Mombasa', 'Mombasa'),
    ('Kisumu', 'Kisumu'),
    ('Nakuru', 'Nakuru'),
    ('Eldoret', 'Eldoret'),
    # Add more towns as needed
]

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
        default='village'
    )
    town_name = models.CharField(max_length=100, choices=KENYA_TOWNS, null=True, blank=True)
    has_children = models.BooleanField(null=True, blank=True)
    number_of_children = models.PositiveIntegerField(null=True, blank=True)
    date_of_registration = models.DateField(default=date.today, editable=False)

    @property
    def age(self):
        if self.birthdate:
            today = date.today()
            return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        return None

    def __str__(self):
        return f"{self.surname}, {self.first_name} {self.last_name}"

class Child(models.Model):
    member = models.ForeignKey(Member, related_name='children', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    email = models.EmailField(null=True, blank=True)
    whatsapp_number = models.CharField(max_length=15, null=True, blank=True)
    location_type = models.CharField(
        max_length=10,
        choices=[('village', 'Village'), ('town', 'Town')],
        default='village'
    )
    town_name = models.CharField(
        max_length=100,
        choices=KENYA_TOWNS,
        null=True,
        blank=True
    )
    is_member = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.age > 25:
            self.is_member = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

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

    @property
    def required_amount(self):
        return self.event.required_amount

    def __str__(self):
        return f"{self.member} - {self.event}: {self.amount} Ksh"
