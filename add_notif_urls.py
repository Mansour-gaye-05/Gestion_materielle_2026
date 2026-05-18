with open('Gestion_emprunt_materiels_SI/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'notifications_count' not in content:
    content = content.replace(
        "path('chatbot/message/', views.chatbot_message, name='chatbot_message'),",
        "path('chatbot/message/', views.chatbot_message, name='chatbot_message'),\n    path('notifications/count/', views.notifications_count, name='notifications_count'),\n    path('notifications/lues/', views.marquer_notifications_lues, name='marquer_notifications_lues'),"
    )
    with open('Gestion_emprunt_materiels_SI/urls.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('URLs notifications ajoutees!')
