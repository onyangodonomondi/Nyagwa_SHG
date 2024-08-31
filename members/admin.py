from django.contrib import admin
from .models import Member, Event, Contribution
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.db import models
import csv
from django.core.mail import send_mail
from django import forms
from io import TextIOWrapper
from django.contrib import messages

# Customizing the Django admin interface
admin.site.site_header = "NYAGWA SHG"
admin.site.site_title = "Your Group Name Portal"
admin.site.index_title = "Welcome to Your Group Name Administration Portal"

# 1. Filter Contributions Based on Contribution Status
class ContributionCategoryFilter(admin.SimpleListFilter):
    title = 'Contribution Status'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        return [
            ('fully', 'Fully Contributed'),
            ('partially', 'Partially Contributed'),
            ('none', 'No Contribution'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'fully':
            return queryset.filter(amount__gte=models.F('event__required_amount'))
        if self.value() == 'partially':
            return queryset.filter(amount__gt=0, amount__lt=models.F('event__required_amount'))
        if self.value() == 'none':
            return queryset.filter(amount=0)

# 2. Export Contributions to PDF
def export_contributions_to_pdf(modeladmin, request, queryset):
    contributions_html = render_to_string('admin/contributions_pdf.html', {'contributions': queryset})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="contributions.pdf"'
    pisa_status = pisa.CreatePDF(contributions_html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + contributions_html + '</pre>')
    return response

export_contributions_to_pdf.short_description = "Export Selected Contributions to PDF"

# 3. Export Members to CSV
def export_members_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="members.csv"'
    writer = csv.writer(response)
    writer.writerow(['Surname', 'First Name', 'Last Name', 'Phone Number', 'Email', 'WhatsApp Number', 'Location Type', 'Town Name', 'Date of Registration'])

    for member in queryset:
        writer.writerow([member.surname, member.first_name, member.last_name, member.phone_number, member.email, member.whatsapp_number, member.location_type, member.town_name, member.date_of_registration])

    return response

export_members_to_csv.short_description = "Export Selected Members to CSV"

# 4. Send Email to Selected Members
def send_email_to_members(modeladmin, request, queryset):
    for member in queryset:
        send_mail(
            'Subject here',
            'Here is the message.',
            'from@example.com',
            [member.email],
            fail_silently=False,
        )
    modeladmin.message_user(request, "Emails sent successfully.")

send_email_to_members.short_description = "Send Email to Selected Members"

# 5. Form for CSV upload
class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()

# 6. Admin action to upload members via CSV
def upload_members_csv(modeladmin, request, queryset):
    if 'csv_file' in request.FILES:
        csv_file = request.FILES['csv_file']
        csv_file = TextIOWrapper(csv_file.file, encoding='utf-8')
        reader = csv.DictReader(csv_file)

        for row in reader:
            try:
                Member.objects.create(
                    surname=row['surname'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    phone_number=row['phone_number'],
                    email=row['email'],
                    whatsapp_number=row['whatsapp_number'],
                    location_type=row['location_type'],
                    town_name=row['town_name'],
                    date_of_registration=row['date_of_registration']
                )
            except Exception as e:
                messages.error(request, f"Error adding member {row['surname']}: {e}")
        messages.success(request, "CSV file imported successfully.")
    else:
        messages.error(request, "Please upload a CSV file.")

upload_members_csv.short_description = "Upload members from CSV"

# 7. Admin configuration for Contribution model
@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'event', 'amount', 'get_required_amount', 'category')
    list_filter = ('event', ContributionCategoryFilter)
    ordering = ('member__surname', 'member__first_name', 'member__last_name')
    actions = [export_contributions_to_pdf]

    def member_name(self, obj):
        return f"{obj.member.surname}, {obj.member.first_name} {obj.member.last_name}"
    member_name.admin_order_field = 'member__surname'

    def get_required_amount(self, obj):
        return obj.event.required_amount
    get_required_amount.short_description = 'Required Amount'

    def category(self, obj):
        if obj.amount >= obj.event.required_amount:
            return 'Fully Contributed'
        elif 0 < obj.amount < obj.event.required_amount:
            return 'Partially Contributed'
        else:
            return 'No Contribution'
    category.short_description = 'Contribution Status'

# 8. Admin configuration for Member model
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('surname', 'first_name', 'last_name', 'phone_number', 'email', 'whatsapp_number', 'location_type', 'town_name', 'date_of_registration')
    ordering = ('surname', 'first_name', 'last_name')
    search_fields = ('surname', 'first_name', 'last_name')
    list_filter = ('surname',)
    actions = [export_members_to_csv, send_email_to_members, upload_members_csv]

    def get_changelist_form(self, request, **kwargs):
        kwargs.setdefault('form', CSVUploadForm)
        return super().get_changelist_form(request, **kwargs)

# 9. Admin configuration for Event model
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'required_amount')
