from django.shortcuts import render, redirect
from .forms import MemberForm
from .models import Member, Event, Contribution
from django.db.models import Sum

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
from django.shortcuts import render
from .models import Contribution

def contributions_page(request):
    contributions = Contribution.objects.all()
    return render(request, 'contributions_page.html', {'contributions': contributions})
