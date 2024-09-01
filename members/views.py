from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponse
from .forms import MemberForm, UserUpdateForm, ProfileUpdateForm, UserSignUpForm
from .models import Member, Event, Contribution, Profile
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import io
import xlsxwriter
from django.db.models import Sum
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy

@login_required
def profile(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if p_form.is_valid():
            p_form.save()
            return redirect('profile')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'p_form': p_form}
    return render(request, 'profile.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'update_profile.html', {'form': form})

def register_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = MemberForm()
    return render(request, 'register_member.html', {'form': form})

def member_contribution_chart(request):
    members = Member.objects.all()
    events = Event.objects.all()

    chart_data = []
    for member in members:
        member_data = {'name': f"{member.first_name} {member.last_name}", 'contributions': []}
        for event in events:
            contribution = member.contributions.filter(event=event).first()
            if contribution:
                member_data['contributions'].append(contribution.amount)
            else:
                member_data['contributions'].append(0)
        chart_data.append(member_data)

    return render(request, 'members/contribution_chart.html', {'chart_data': chart_data, 'events': [event.name for event in events]})

def home(request):
    members = Member.objects.all()
    return render(request, 'home.html', {'members': members})

def events_page(request):
    events = Event.objects.all()
    event_data = []

    total_members = Member.objects.count()

    for event in events:
        total_contributed = Contribution.objects.filter(event=event).aggregate(Sum('amount'))['amount__sum'] or 0
        expected_total = total_members * event.required_amount
        percentage_contributed = (total_contributed / expected_total) * 100 if expected_total > 0 else 0

        event_data.append({
            'name': event.name,
            'total_contributed': total_contributed,
            'percentage_contributed': percentage_contributed,
        })

    return render(request, 'events_page.html', {'event_data': event_data})

def members_page(request):
    members = Member.objects.all()
    return render(request, 'members_page.html', {'members': members})

def contributions_page(request):
    selected_event = request.GET.get('event')
    events = Event.objects.all()
    if selected_event:
        contributions = Contribution.objects.filter(event__name=selected_event)
    else:
        contributions = Contribution.objects.all()

    context = {
        'contributions': contributions,
        'events': events,
        'selected_event': selected_event,
    }
    return render(request, 'contributions_page.html', context)

def export_contributions_pdf(request):
    selected_event = request.GET.get('event')
    if selected_event:
        contributions = Contribution.objects.filter(event__name=selected_event)
    else:
        contributions = Contribution.objects.all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Add a title
    title_style = getSampleStyleSheet()['Heading1']
    title_style.alignment = 1  # Center the title
    title = Paragraph("Contributions Report", title_style)
    elements.append(title)

    # Add some space after the title
    elements.append(Spacer(1, 0.5 * inch))

    # Prepare data for the table
    data = [["Member Name", "Event", "Amount", "Status"]]
    for contribution in contributions:
        member_name = f"{contribution.member.surname} {contribution.member.first_name}"
        event_name = contribution.event.name
        amount = f"{contribution.amount} Ksh"
        status = contribution.category
        data.append([member_name, event_name, amount, status])

    # Create the table with a style
    table = Table(data, colWidths=[2 * inch, 2 * inch, 1.5 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='contributions.pdf')

def export_contributions_excel(request):
    selected_event = request.GET.get('event')
    if selected_event:
        contributions = Contribution.objects.filter(event__name=selected_event)
    else:
        contributions = Contribution.objects.all()

    # Create an Excel document
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Write data headers
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
    worksheet.write(0, 0, 'Member Name', header_format)
    worksheet.write(0, 1, 'Event', header_format)
    worksheet.write(0, 2, 'Amount', header_format)
    worksheet.write(0, 3, 'Status', header_format)

    # Write data
    for row_num, contribution in enumerate(contributions, 1):
        worksheet.write(row_num, 0, f"{contribution.member.surname} {contribution.member.first_name}")
        worksheet.write(row_num, 1, contribution.event.name)
        worksheet.write(row_num, 2, f"{contribution.amount} Ksh")
        worksheet.write(row_num, 3, contribution.category)

    workbook.close()

    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=contributions.xlsx'
    return response

def signup(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = UserSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')
    email_template_name = 'registration/password_reset_email.html'
