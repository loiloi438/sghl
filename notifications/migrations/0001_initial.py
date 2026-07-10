import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceToken',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('token', models.CharField(max_length=512, unique=True)),
                (
                    'plateforme',
                    models.CharField(
                        choices=[
                            ('android', 'Android'),
                            ('ios', 'iOS'),
                            ('web', 'Web'),
                            ('inconnu', 'Inconnu'),
                        ],
                        default='inconnu',
                        max_length=20,
                    ),
                ),
                ('actif', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'utilisateur',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='appareils_push',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'jeton appareil',
                'verbose_name_plural': 'jetons appareils',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='NotificationInbox',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('titre', models.CharField(max_length=200)),
                ('corps', models.TextField()),
                ('categorie', models.CharField(blank=True, max_length=50)),
                ('donnees', models.JSONField(blank=True, default=dict)),
                ('lu', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'utilisateur',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='notifications_inbox',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'notification',
                'verbose_name_plural': 'notifications',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['utilisateur', 'lu'], name='notificatio_utilisa_8f0b0d_idx')],
            },
        ),
    ]
