# Generated by Django 3.1.4 on 2021-04-02 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lexeme', '0005_lexemecontent_deleted_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='lexeme',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
