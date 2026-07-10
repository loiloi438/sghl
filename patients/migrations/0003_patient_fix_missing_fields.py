from django.db import migrations, models


def ensure_patient_fields(apps, schema_editor):
    Patient = apps.get_model('patients', 'Patient')
    table_name = Patient._meta.db_table
    cursor = schema_editor.connection.cursor()

    if schema_editor.connection.vendor == 'sqlite':
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        existing_columns = {row[1] for row in cursor.fetchall()}
    else:
        existing_columns = {
            column.name
            for column in schema_editor.connection.introspection.get_table_description(cursor, table_name)
        }

    def add_field_if_missing(name, field):
        if name not in existing_columns:
            field.set_attributes_from_name(name)
            schema_editor.add_field(Patient, field)

    add_field_if_missing('photo', models.CharField(blank=True, default='', max_length=100))
    add_field_if_missing('allergies', models.TextField(blank=True, default=''))
    add_field_if_missing('antecedents_medicaux', models.TextField(blank=True, default=''))
    add_field_if_missing('groupe_sanguin', models.CharField(blank=True, default='', max_length=5))
    add_field_if_missing('traitements_en_cours', models.TextField(blank=True, default=''))
    add_field_if_missing('adresse', models.TextField(blank=True, default=''))
    add_field_if_missing('email', models.EmailField(blank=True, default='', max_length=254))
    add_field_if_missing('telephone', models.CharField(blank=True, default='', max_length=20))


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0002_patient_allergies_patient_antecedents_medicaux_and_more'),
    ]

    operations = [
        migrations.RunPython(ensure_patient_fields, reverse_code=migrations.RunPython.noop),
    ]
