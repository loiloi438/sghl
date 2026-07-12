from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rendezvous', '0003_rendezvous_lien_visio_rendezvous_type_consultation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rendezvous',
            name='statut',
            field=models.CharField(
                choices=[
                    ('en_attente', 'En attente de validation'),
                    ('planifie', 'Planifié'),
                    ('confirme', 'Confirmé'),
                    ('annule', 'Annulé'),
                    ('termine', 'Terminé'),
                    ('absent', 'Absent'),
                ],
                default='planifie',
                max_length=20,
            ),
        ),
    ]
