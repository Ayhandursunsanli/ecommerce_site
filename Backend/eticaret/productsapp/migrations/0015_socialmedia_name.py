# Generated by Django 4.2 on 2023-07-01 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productsapp', '0014_footer_social_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialmedia',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
