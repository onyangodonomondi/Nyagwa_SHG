from django.shortcuts import render, redirect
from .forms import MemberForm, ChildForm
from .models import Member, Event, Contribution

def register_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            if member.has_children:
                for _ in range(member.number_of_children):
                    # Collect child details for each child
                    child_form = ChildForm(request.POST)
                    if child_form.is_valid():
                        child = child_form.save(commit=False)
                        child.member = member
                        child.save()
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