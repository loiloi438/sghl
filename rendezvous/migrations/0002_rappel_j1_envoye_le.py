from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rendezvous', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rendezvous',
            name='rappel_j1_envoye_le',
            field=models.DateTimeField(
                blank=True,
                help_text='Horodatage du dernier e-mail de rappel la veille du RDV.',
                null=True,
                verbose_name='Rappel J-1 envoyé le',
            ),
        ),
    ]
