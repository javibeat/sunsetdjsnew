from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from .models import Shift, DJ
from django.conf import settings
from datetime import datetime
from django.db.models import Count

def home(request):
    # Reutilizar la lógica de global_calendar
    shifts = Shift.objects.all().order_by('date', 'start_time')
    
    # Definir colores para cada DJ
    dj_colors = {
        'Emre': '#4285F4',
        'Elena': '#EA4335',
        'Batu': '#FBBC05',
        'Yasin': '#34A853',
        'Reda': '#8E24AA',
        'Sergio': '#16A085',
        'Javi': '#41B0F6',
    }
    
    # Preparar datos para el calendario
    shifts_for_calendar = []
    for shift in shifts:
        shifts_for_calendar.append({
            'id': shift.id,
            'dj': shift.dj,
            'venue': shift.venue,
            'date': shift.date.strftime('%Y-%m-%d'),
            'start_time': shift.start_time.strftime('%H:%M'),
            'end_time': shift.end_time.strftime('%H:%M'),
            'is_event': shift.is_event,
            'has_dj': shift.has_dj,
            'comment': shift.comment,
            'color': dj_colors.get(shift.dj.name, '#999999') if shift.dj else '#999999',
        })
    
    return render(request, 'core/home.html', {'shifts': shifts_for_calendar})

def global_calendar(request):
    shifts = Shift.objects.all().order_by('date', 'start_time')
    
    # Definir colores para cada DJ
    dj_colors = {
        'Emre': '#4285F4',
        'Elena': '#EA4335',
        'Batu': '#FBBC05',
        'Yasin': '#34A853',
        'Reda': '#8E24AA',
        'Sergio': '#16A085',
        'Javi': '#41B0F6',
    }
    
    # Preparar datos para el calendario
    shifts_for_calendar = []
    for shift in shifts:
        shifts_for_calendar.append({
            'id': shift.id,
            'dj': shift.dj,
            'venue': shift.venue,
            'date': shift.date.strftime('%Y-%m-%d'),
            'start_time': shift.start_time.strftime('%H:%M'),
            'end_time': shift.end_time.strftime('%H:%M'),
            'is_event': shift.is_event,
            'has_dj': shift.has_dj,
            'comment': shift.comment,
            'color': dj_colors.get(shift.dj.name, '#999999') if shift.dj else '#999999',
        })
    
    return render(request, 'core/calendar.html', {'shifts': shifts_for_calendar, 'view_type': 'Global'})

def dj_calendar(request, dj_id):
    shifts = Shift.objects.filter(dj__id=dj_id).order_by('date', 'start_time')
    return render(request, 'core/calendar.html', {'shifts': shifts, 'view_type': 'Personal'})


# Vista de login para DJs
def login_view(request):
    djs = DJ.objects.all().order_by('name')
    if request.method == 'POST':
        dj_id = request.POST.get('dj_id')
        email = request.POST.get('email')
        try:
            dj = DJ.objects.get(id=dj_id)
            if dj.email is None:
                dj.email = email
            elif dj.email != email:
                return render(request, 'core/login.html', {
                    'djs': djs,
                    'error': 'This email does not match our records.'
                })
            token = get_random_string(32)
            dj.token = token
            dj.save()
            # Enviar correo con el enlace de login
            send_mail(
                subject='Your Sunset DJs Login Link',
                message=f'Hi {dj.name},\n\nClick the link below to access your dashboard:\n\n{settings.SITE_URL}/verify/{token}/\n\nSee you soon!',
                from_email='javibeat@gmail.com',
                recipient_list=[dj.email],
                fail_silently=False,
            )
            return render(request, 'core/login.html', {
                'djs': djs,
                'message': 'Login link sent to your email (simulated).'
            })
        except DJ.DoesNotExist:
            return render(request, 'core/login.html', {
                'djs': djs,
                'error': 'DJ not found.'
            })
    return render(request, 'core/login.html', {'djs': djs})

def verify_token_view(request, token):
    try:
        dj = DJ.objects.get(token=token)
        dj.is_verified = True
        dj.token = None
        dj.save()
        request.session['dj_id'] = dj.id
        return redirect(f'/dj/{dj.id}/dashboard/')
    except DJ.DoesNotExist:
        return render(request, 'core/login.html', {
            'djs': DJ.objects.all(),
            'error': 'Invalid or expired login link.'
        })


# Vista del dashboard para el DJ
def dj_dashboard_view(request, dj_id):
    try:
        dj = DJ.objects.get(id=dj_id)
        if request.session.get('dj_id') != dj.id:
            return redirect('login')
        shifts = Shift.objects.filter(dj=dj).order_by('date', 'start_time')
        venue_colors = {
            'Drift': '#007aff',
            'Aura': '#10b981',
            'Azure': '#6366f1',
            'Ammos': '#f59e0b',
        }
        shifts_for_calendar = []
        from .models import Notification
        notifications = Notification.objects.filter(dj=dj).order_by('-created_at')[:5]
        for shift in shifts:
            color = venue_colors.get(shift.venue, '#999999')
            shifts_for_calendar.append({
                'id': shift.id,
                'venue': shift.venue,
                'date': shift.date.strftime('%Y-%m-%d'),
                'start_time': shift.start_time.strftime('%H:%M'),
                'end_time': shift.end_time.strftime('%H:%M'),
                'is_event': shift.is_event,
                'has_dj': shift.has_dj,
                'comment': shift.comment,
                'color': color,
            })
        return render(request, 'core/dashboard.html', {
            'dj': dj,
            'shifts': shifts_for_calendar,
            'notifications': notifications
        })
    except DJ.DoesNotExist:
        return redirect('login')



from django.contrib import messages

def insert_shift_view(request):
    from datetime import datetime

    djs = DJ.objects.all().order_by('name')
    venues = ['Drift', 'Aura', 'Azure', 'Ammos']

    # Extraer mes y año del query string (?month=2025-05)
    month_str = request.GET.get('month')
    if month_str:
        try:
            current_month = datetime.strptime(month_str, "%Y-%m").date()
        except ValueError:
            current_month = datetime.now().date()
    else:
        current_month = datetime.now().date()

    current_year = current_month.year
    current_month_num = current_month.month

    if request.method == 'POST':
        dj_id = request.POST.get('dj')
        venue = request.POST.get('venue')
        dates = request.POST.get('dates', '').split(',')
        # Horarios como listas
        start_hours = request.POST.getlist('start_hour[]')
        start_minutes = request.POST.getlist('start_minute[]')
        start_ampms = request.POST.getlist('start_ampm[]')
        end_hours = request.POST.getlist('end_hour[]')
        end_minutes = request.POST.getlist('end_minute[]')
        end_ampms = request.POST.getlist('end_ampm[]')
        # Evento y comentario (si aplica)
        is_event = request.POST.get('is_event') == 'on'
        has_dj = request.POST.get('has_dj') == 'on'
        comment = request.POST.get('comment', '').strip()

        try:
            dj = DJ.objects.get(id=dj_id)
        except DJ.DoesNotExist:
            dj = None

        created_count = 0

        for date_str in dates:
            date_str = date_str.strip()
            if not date_str:
                continue
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                continue

            for i in range(len(start_hours)):
                # Horas y minutos a 24h
                try:
                    sh = int(start_hours[i])
                    sm = int(start_minutes[i])
                    eh = int(end_hours[i])
                    em = int(end_minutes[i])
                    sh += 12 if start_ampms[i] == 'pm' and sh != 12 else 0
                    eh += 12 if end_ampms[i] == 'pm' and eh != 12 else 0
                    sh = 0 if start_ampms[i] == 'am' and sh == 12 else sh
                    eh = 0 if end_ampms[i] == 'am' and eh == 12 else eh
                except (ValueError, IndexError):
                    continue

                Shift.objects.create(
                    dj=dj,
                    venue=venue,
                    date=date_obj,
                    start_time=f"{sh:02d}:{sm:02d}",
                    end_time=f"{eh:02d}:{em:02d}",
                    is_event=is_event,
                    has_dj=has_dj,
                    comment=comment if is_event else ''
                )
                created_count += 1
                if request.session.get('dj_id') == dj.id:
                    Notification.objects.create(dj=dj, message=f"Shift added: {venue} on {date_obj} ({sh:02d}:{sm:02d} - {eh:02d}:{em:02d})")

        shifts = Shift.objects.all().order_by('-date')
        # Definir colores para cada DJ
        dj_colors = {
            'Emre': '#4285F4',
            'Elena': '#EA4335',
            'Batu': '#FBBC05',
            'Yasin': '#34A853',
            'Reda': '#8E24AA',
            'Sergio': '#16A085',
            'Javi': '#41B0F6',  # Cambiado de #F39C12 a #9C27B0
        }
        shifts_for_calendar = []
        for shift in shifts:
            shifts_for_calendar.append({
                'id': shift.id,
                'dj': shift.dj.name if shift.dj else 'Sin DJ',
                'venue': shift.venue,
                'date': shift.date.strftime('%Y-%m-%d'),
                'start_time': shift.start_time.strftime('%H:%M'),
                'end_time': shift.end_time.strftime('%H:%M'),
                'is_event': shift.is_event,
                'has_dj': shift.has_dj,
                'comment': shift.comment,
                'color': dj_colors.get(shift.dj.name, '#999999') if shift.dj else '#999999',
            })
        return render(request, 'core/shift_form.html', {
            'djs': djs,
            'venues': venues,
            'shifts': shifts_for_calendar,
            'success_message': f"{created_count} shifts/events added successfully."
        })

    # Obtener los shifts para mostrar en el calendario admin (puedes filtrar por DJ o mostrar todos)
    shifts = Shift.objects.all().order_by('-date')
    dj_colors = {
        'Emre': '#4285F4',
        'Elena': '#EA4335',
        'Batu': '#FBBC05',
        'Yasin': '#34A853',
        'Reda': '#8E24AA',
        'Sergio': '#16A085',
        'Javi': '#41B0F6',
    }
    shifts_for_calendar = []
    for shift in shifts:
        shifts_for_calendar.append({
            'id': shift.id,
            'dj': shift.dj.name if shift.dj else 'Sin DJ',
            'venue': shift.venue,
            'date': shift.date.strftime('%Y-%m-%d'),
            'start_time': shift.start_time.strftime('%H:%M'),
            'end_time': shift.end_time.strftime('%H:%M'),
            'is_event': shift.is_event,
            'has_dj': shift.has_dj,
            'comment': shift.comment,
            'color': dj_colors.get(shift.dj.name, '#999999') if shift.dj else '#999999',
        })

    dj_summary = []
    for dj in djs:
        count = Shift.objects.filter(
            dj=dj,
            date__year=current_month.year,
            date__month=current_month.month
        ).count()
        dj_summary.append({'name': dj.name, 'count': count})

    return render(request, 'core/shift_form.html', {
        'djs': djs,
        'venues': venues,
        'shifts': shifts_for_calendar,
        'dj_summary': dj_summary,
        'current_month': current_month.strftime('%Y-%m'),
    })


# Delete shift API view
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Notification

@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def delete_shift_view(request, shift_id):
    try:
        shift = Shift.objects.get(id=shift_id)
        if request.session.get('dj_id') == shift.dj.id:
            Notification.objects.create(dj=shift.dj, message=f"Shift deleted: {shift.venue} on {shift.date} ({shift.start_time} - {shift.end_time})")
        shift.delete()
        return JsonResponse({'success': True})
    except Shift.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Shift not found'}, status=404)


# Vista para obtener el resumen de shifts por DJ en formato JSON
from django.views.decorators.http import require_GET

@require_GET
def get_dj_summary_view(request):
    from datetime import datetime
    month = request.GET.get('month')
    year = request.GET.get('year')

    if month and year:
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return JsonResponse({'error': 'Invalid month or year'}, status=400)
    else:
        now = datetime.now()
        month = now.month
        year = now.year

    djs = DJ.objects.all()
    summary = []
    for dj in djs:
        count = Shift.objects.filter(
            dj=dj,
            date__year=year,
            date__month=month
        ).count()
        summary.append({'name': dj.name, 'count': count})

    return JsonResponse({'dj_summary': summary})


def hr_view(request):
    from datetime import datetime
    
    # Obtener todos los shifts y DJs
    shifts = Shift.objects.all().order_by('date', 'start_time')
    djs = DJ.objects.all().order_by('name')
    venues = ['Drift', 'Aura', 'Azure', 'Ammos']
    
    # Definir colores para cada DJ
    dj_colors = {
        'Emre': '#4285F4',
        'Elena': '#EA4335',
        'Batu': '#FBBC05',
        'Yasin': '#34A853',
        'Reda': '#8E24AA',
        'Sergio': '#16A085',
        'Javi': '#41B0F6',
    }
    
    # Preparar datos para el calendario
    shifts_for_calendar = []
    for shift in shifts:
        shifts_for_calendar.append({
            'id': shift.id,
            'dj': shift.dj,
            'venue': shift.venue,
            'date': shift.date.strftime('%Y-%m-%d'),
            'start_time': shift.start_time.strftime('%H:%M'),
            'end_time': shift.end_time.strftime('%H:%M'),
            'is_event': shift.is_event,
            'has_dj': shift.has_dj,
            'comment': shift.comment,
            'color': dj_colors.get(shift.dj.name, '#999999') if shift.dj else '#999999',
        })
    
    # Calcular resumen de DJs para el mes actual
    current_month = datetime.now().date()
    dj_summary = []
    for dj in djs:
        count = Shift.objects.filter(
            dj=dj,
            date__year=current_month.year,
            date__month=current_month.month
        ).count()
        dj_summary.append({'name': dj.name, 'count': count})
    
    return render(request, 'core/hr.html', {
        'shifts': shifts_for_calendar,
        'djs': djs,
        'venues': venues,
        'dj_summary': dj_summary,
        'current_month': current_month.strftime('%Y-%m'),
    })
