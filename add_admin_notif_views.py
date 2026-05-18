with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

admin_notif = '''

@staff_member_required
def notifications_admin_count(request):
    notifs = Notification.objects.all().order_by('-date')[:10]
    count = Notification.objects.filter(lu=False).count()
    data = {
        'count': count,
        'notifications': [
            {
                'message': n.message,
                'type': n.type,
                'date': n.date.strftime('%d/%m %H:%M'),
                'lu': n.lu
            }
            for n in notifs
        ]
    }
    return JsonResponse(data)

@staff_member_required
def marquer_notifications_admin_lues(request):
    if request.method == 'POST':
        Notification.objects.filter(lu=False).update(lu=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'methode non autorisee'}, status=405)
'''

content += admin_notif
with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Vues admin notifications ajoutees!')
