from django.contrib import admin
from .models import (
    Utilisateur, Categorie, Materiel, Demande, LigneDemande,
    Emplacement, Restitution, Maintenance, ConversationChat,
    Notification, Reservation, JournalActivite
)

class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'filiere', 'niveau')
    list_filter = ('role', 'filiere')
    search_fields = ('username', 'email')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'type', 'date', 'lu')
    list_filter = ('type', 'lu', 'date')
    search_fields = ('message',)

class JournalActiviteAdmin(admin.ModelAdmin):
    list_display = ('date', 'utilisateur', 'action', 'description')
    list_filter = ('action', 'date')
    search_fields = ('description', 'utilisateur__username')
    readonly_fields = ('date', 'utilisateur', 'action', 'description', 'ip_address', 'demande', 'materiel')

admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Categorie)
admin.site.register(Materiel)
admin.site.register(Demande)
admin.site.register(LigneDemande)
admin.site.register(Emplacement)
admin.site.register(Restitution)
admin.site.register(Maintenance)
admin.site.register(ConversationChat)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Reservation)
admin.site.register(JournalActivite, JournalActiviteAdmin)