# Generated by Django 4.2.3 on 2023-08-13 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productsapp', '0049_siparisurun_urun_stok_kodu'),
    ]

    operations = [
        migrations.AddField(
            model_name='siparis',
            name='teslimat_bilgileri_email',
            field=models.EmailField(max_length=200, null=True, verbose_name='E-Mail'),
        ),
    ]
