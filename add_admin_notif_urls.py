with open('Gestion_emprunt_materiels_SI/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'notifications_admin' not in content:
    content = content.replace(
        "path('notifications/lues/', views.marquer_notifications_lues, name='marquer_notifications_lues'),",
        "path('notifications/lues/', views.marquer_notifications_lues, name='marquer_notifications_lues'),\n    path('notifications/admin/', views.notifications_admin_count, name='notifications_admin_count'),\n    path('notifications/admin/lues/', views.marquer_notifications_admin_lues, name='marquer_notifications_admin_lues'),"
    )
    with open('Gestion_emprunt_materiels_SI/urls.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('URLs admin notifications ajoutees!')
