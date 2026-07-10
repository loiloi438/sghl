from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('provider', models.CharField(choices=[('stripe', 'Stripe'), ('mtn', 'MTN Mobile Money'), ('airtel', 'Airtel Money'), ('paypal', 'PayPal')], max_length=30)),
                ('amount_cents', models.BigIntegerField()),
                ('currency', models.CharField(default='XAF', max_length=6)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('reference', models.CharField(max_length=128, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=128, null=True)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.user')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
