from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('technicien', 'Technicien'),
        ('admin', 'Administrateur'),
    ]

    matricule = models.CharField(max_length=20, unique=True, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')
    filiere = models.CharField(max_length=100, blank=True, null=True)
    niveau = models.CharField(max_length=50, blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    photo_profil = models.ImageField(upload_to='profil_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"


class Categorie(models.Model):
    libelle = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.libelle


class Materiel(models.Model):
    ETAT_CHOICES = [
        ('disponible', 'Disponible'),
        ('emprunte', 'Emprunté'),
        ('maintenance', 'En maintenance'),
        ('hors_service', 'Hors service'),
    ]

    nom = models.CharField(max_length=200)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='materiels')
    numero_serie = models.CharField(max_length=100, unique=True, blank=True, null=True)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='disponible')
    photo = models.ImageField(upload_to='materiel_photos/', blank=True, null=True)
    description = models.TextField(blank=True)
    date_acquisition = models.DateField(null=True, blank=True)

    # Nouveaux champs pour la gestion des quantités
    quantite_totale = models.PositiveIntegerField(default=1, help_text="Quantité totale en stock")
    quantite_disponible = models.PositiveIntegerField(default=1, help_text="Quantité disponible à l'emprunt")

    def __str__(self):
        return f"{self.nom} ({self.numero_serie or 'N/A'})"

    def est_disponible(self):
        return self.quantite_disponible > 0 and self.etat == 'disponible'


class Demande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuvee', 'Approuvée'),
        ('refusee', 'Refusée'),
        ('en_cours', 'En cours'),
        ('restituee', 'Restituée'),
        ('retard', 'En retard'),
        ('annulee', 'Annulee'),
    ]

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='demandes')
    date_demande = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    motif = models.TextField(blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='validations')
    motif_refus = models.TextField(blank=True)

    def __str__(self):
        return f"Demande #{self.id} - {self.utilisateur.username} - {self.statut}"


class LigneDemande(models.Model):
    demande = models.ForeignKey(Demande, on_delete=models.CASCADE, related_name='lignes')
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ['demande', 'materiel']

    def __str__(self):
        return f"{self.demande.id} - {self.materiel.nom} x{self.quantite}"


class Emplacement(models.Model):
    demande = models.ForeignKey(Demande, on_delete=models.CASCADE, related_name='emplacements')
    libelle = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    adresse = models.TextField(blank=True)

    def __str__(self):
        return self.libelle or f"Emplacement #{self.id}"


class Restitution(models.Model):
    demande = models.OneToOneField(Demande, on_delete=models.CASCADE, related_name='restitution')
    date_retour = models.DateTimeField(auto_now_add=True)
    etat_materiel = models.TextField(blank=True, help_text="État du matériel au retour")
    observations = models.TextField(blank=True)

    def __str__(self):
        return f"Restitution Demande #{self.demande.id}"


class Maintenance(models.Model):
    STATUT_CHOICES = [
        ('signale', 'Signalé'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
    ]

    TYPE_CHOICES = [
        ('panne', 'Panne'),
        ('revision', 'Révision'),
        ('etalonnage', 'Étalonnage'),
        ('reparation', 'Réparation'),
    ]

    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE, related_name='maintenances')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_signalement = models.DateTimeField(auto_now_add=True)
    date_resolution = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='signale')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.materiel.nom} - {self.type} - {self.statut}"


class ConversationChat(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='conversations')
    date = models.DateTimeField(auto_now_add=True)
    messages = models.JSONField(default=list, help_text="Liste des messages (format JSON)")

    def __str__(self):
        return f"Chat {self.utilisateur.username} - {self.date.strftime('%Y-%m-%d %H:%M')}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('recuperation', 'Récupération'),
        ('retour', 'Retour'),
        ('retard', 'Retard'),
        ('nouvelle_demande', 'Nouvelle demande'),
        ('validation', 'Validation'),
    ]

    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    demande = models.ForeignKey('Demande', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='notifications')

    def __str__(self):
        return f"{self.get_type_display()} - {self.date.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        ordering = ['-date']

class Reservation(models.Model):
    STATUT_CHOICES = [
        ('active', 'Active'),
        ('annulee', 'Annulee'),
        ('terminee', 'Terminee'),
    ]

    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE, related_name='reservations')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='reservations')
    demande = models.OneToOneField('Demande', on_delete=models.CASCADE, related_name='reservation', null=True, blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    quantite = models.PositiveIntegerField(default=1)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='active')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_debut']

    def __str__(self):
        return f"Reservation {self.materiel.nom} - {self.utilisateur.username} ({self.date_debut} -> {self.date_fin})"

    @staticmethod
    def verifier_conflit(materiel_id, date_debut, date_fin, quantite=1, exclude_id=None):
        from datetime import date
        qs = Reservation.objects.filter(
            materiel_id=materiel_id,
            statut='active',
            date_debut__lt=date_fin,
            date_fin__gt=date_debut
        )
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        quantite_reservee = qs.aggregate(total=models.Sum('quantite'))['total'] or 0
        materiel = Materiel.objects.get(id=materiel_id)
        return quantite_reservee + quantite > materiel.quantite_totale, quantite_reservee


class JournalActivite(models.Model):
    ACTION_CHOICES = [
        ('connexion', 'Connexion'),
        ('deconnexion', 'Deconnexion'),
        ('inscription', 'Inscription'),
        ('demande_creee', 'Demande creee'),
        ('demande_approuvee', 'Demande approuvee'),
        ('demande_refusee', 'Demande refusee'),
        ('materiel_recupere', 'Materiel recupere'),
        ('materiel_rendu', 'Materiel rendu'),
        ('panne_signalee', 'Panne signalee'),
        ('maintenance_resolue', 'Maintenance resolue'),
        ('materiel_ajoute', 'Materiel ajoute'),
        ('materiel_modifie', 'Materiel modifie'),
        ('materiel_supprime', 'Materiel supprime'),
        ('role_modifie', 'Role modifie'),
        ('reservation_creee', 'Reservation creee'),
        ('reservation_annulee', 'Reservation annulee'),
    ]

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='journal')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    demande = models.ForeignKey('Demande', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal')
    materiel = models.ForeignKey('Materiel', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal')

    class Meta:
        ordering = ['-date']
        verbose_name = 'Journal activite'
        verbose_name_plural = 'Journal des activites'

    def __str__(self):
        user = self.utilisateur.username if self.utilisateur else 'Systeme'
        return f"[{self.date.strftime('%d/%m/%Y %H:%M')}] {user} - {self.get_action_display()}"
