with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

notif_view = '''

# ==================== NOTIFICATIONS TEMPS REEL ====================

@login_required
def notifications_count(request):
    count = Notification.objects.filter(
        demande__utilisateur=request.user,
        lu=False
    ).count()
    notifications = Notification.objects.filter(
        demande__utilisateur=request.user
    ).order_by('-date')[:5]
    data = {
        'count': count,
        'notifications': [
            {
                'message': n.message,
                'type': n.type,
                'date': n.date.strftime('%d/%m %H:%M'),
                'lu': n.lu
            }
            for n in notifications
        ]
    }
    return JsonResponse(data)

@login_required
def marquer_notifications_lues(request):
    if request.method == 'POST':
        Notification.objects.filter(
            demande__utilisateur=request.user,
            lu=False
        ).update(lu=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'methode non autorisee'}, status=405)
'''

content += notif_view
with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Vues notifications ajoutees!')
