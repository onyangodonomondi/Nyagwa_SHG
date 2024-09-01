from django.shortcuts import render, redirect
from .forms import MemberForm
from .models import Member, Event, Contribution
from django.db.models import Sum
import io
from django.http import FileResponse, HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import xlsxwriter

def register_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # Redirect to a success page after saving
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
        # Calculate total contributed amount for this event
        total_contributed = Contribution.objects.filter(event=event).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Calculate the total expected amount if all members had contributed
        expected_total = total_members * event.required_amount
        
        # Calculate the percentage of contributions
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

    # Create a PDF document
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "Contributions Report")

    y = 720
    for contribution in contributions:
        p.drawString(100, y, f"{contribution.member.surname} {contribution.member.first_name} - {contribution.event.name} - {contribution.amount} Ksh - {contribution.category}")
        y -= 20
    
    p.showPage()
    p.save()

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
    worksheet.write(0, 0, 'Member Name')
    worksheet.write(0, 1, 'Event')
    worksheet.write(0, 2, 'Amount')
    worksheet.write(0, 3, 'Status')

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
