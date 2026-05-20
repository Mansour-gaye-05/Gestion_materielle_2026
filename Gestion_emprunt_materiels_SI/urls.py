from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from gestion import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Pages principales
    path('', views.accueil, name='accueil'),
    path('catalogue/', views.catalogue, name='catalogue'),

    # Espace administrateur
    path('dashboard/', views.dashboard, name='dashboard'),
    path('demandes/', views.gestion_demandes, name='gestion_demandes'),
    path('demande/<int:demande_id>/valider/', views.valider_demande, name='valider_demande'),
    path('maintenance/', views.gestion_maintenance, name='gestion_maintenance'),
    path('maintenance/ajouter/', views.ajouter_maintenance, name='ajouter_maintenance'),
    path('maintenance/<int:maintenance_id>/resoudre/', views.resoudre_maintenance, name='resoudre_maintenance'),
    path('catalogue/gestion/', views.gestion_catalogue, name='gestion_catalogue'),
    path('materiel/ajouter/', views.ajouter_materiel, name='ajouter_materiel'),
    path('materiel/<int:materiel_id>/modifier/', views.modifier_materiel, name='modifier_materiel'),
    path('materiel/<int:materiel_id>/supprimer/', views.supprimer_materiel, name='supprimer_materiel'),
    path('utilisateurs/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('utilisateur/<int:user_id>/role/', views.modifier_role, name='modifier_role'),

    # Exports
    path('journal/', views.journal_activite, name='journal_activite'),
    path('export/excel/', views.export_statistiques_excel, name='export_excel'),
    path('export/pdf/', views.export_rapport_pdf, name='export_pdf'),

    # Cartographie
    path('carte/', views.carte_materiels, name='carte_materiels'),

    # Authentification
    path('connexion/', views.connexion, name='connexion'),
    path('mot-de-passe-oublie/', views.mot_de_passe_oublie, name='mot_de_passe_oublie'),
    path('connexion-admin/', views.connexion_admin, name='connexion_admin'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),

    # Espace étudiant
    path('inscription/', views.inscription, name='inscription'),
    path('espace_etudiant/', views.espace_etudiant, name='espace_etudiant'),
    path('nouvelle_demande/', views.nouvelle_demande, name='nouvelle_demande'),
    path('mes_demandes/', views.mes_demandes, name='mes_demandes'),
    path('demande/<int:demande_id>/detail/', views.detail_demande, name='detail_demande'),
    path('profil/', views.profil_etudiant, name='profil_etudiant'),
    path('profil/mdp/', views.changer_mot_de_passe, name='changer_mot_de_passe'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('chatbot/message/', views.chatbot_message, name='chatbot_message'),
    path('notifications/count/', views.notifications_count, name='notifications_count'),
    path('notifications/lues/', views.marquer_notifications_lues, name='marquer_notifications_lues'),
    path('notifications/admin/', views.notifications_admin_count, name='notifications_admin_count'),
    path('notifications/admin/lues/', views.marquer_notifications_admin_lues, name='marquer_notifications_admin_lues'),

    # Actions demande
    path('demander/<int:materiel_id>/', views.ajouter_demande, name='ajouter_demande'),
    path('rendre/<int:demande_id>/', views.rendre_materiel, name='rendre_materiel'),
    path('bon-sortie/<int:demande_id>/', views.bon_sortie_pdf, name='bon_sortie_pdf'),
    path('recuperer/<int:demande_id>/', views.recuperer_materiel, name='recuperer_materiel'),
    path('materiel/<int:materiel_id>/reservations/', views.reservations_materiel, name='reservations_materiel'),
    path('signaler-panne-emprunt/<int:demande_id>/', views.signaler_panne_emprunt, name='signaler_panne_emprunt'),
    path('demande/<int:demande_id>/annuler/', views.annuler_demande, name='annuler_demande'),

    # PDF — Fiche d'emprunt (étudiant ou staff)
    path('demande/<int:demande_id>/pdf/emprunt/',
         views.pdf_fiche_emprunt,
         name='pdf_fiche_emprunt'),

    # PDF — Reçu de restitution (étudiant ou staff)
    path('demande/<int:demande_id>/pdf/restitution/',
         views.pdf_recu_restitution,
         name='pdf_recu_restitution'),

    # PDF — Bon de sortie (staff uniquement)
    path('demande/<int:demande_id>/pdf/bon-sortie/',
         views.pdf_bon_sortie,
         name='pdf_bon_sortie'),
    path('signaler-panne-page/<int:demande_id>/', views.signaler_panne_page, name='signaler_panne_page'),
    path('changer-nom-utilisateur/', views.changer_nom_utilisateur, name='changer_nom_utilisateur'),
    path('connexion-enseignant/', views.connexion_enseignant, name='connexion_enseignant'),
    path('inscription-enseignant/', views.inscription_enseignant, name='inscription_enseignant'),
    path('espace-enseignant/', views.espace_enseignant, name='espace_enseignant'),
    path('enseignant/valider/<int:demande_id>/', views.enseignant_valider_demande, name='enseignant_valider_demande'),
    path('profil-enseignant/', views.profil_enseignant, name='profil_enseignant'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)