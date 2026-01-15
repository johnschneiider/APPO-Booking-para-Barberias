# Generated manually - Fixed migration to avoid index rename issues

from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('negocios', '0001_initial'),
        ('clientes', '0012_bloqueocliente'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Crear modelo ClienteProvisional
        migrations.CreateModel(
            name='ClienteProvisional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Nombre completo del cliente', max_length=200)),
                ('telefono', models.CharField(help_text='Teléfono de contacto', max_length=15)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('notas', models.TextField(blank=True, help_text='Notas adicionales sobre el cliente')),
                ('creado_por', models.ForeignKey(blank=True, help_text='Usuario del negocio que creó este cliente provisional', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clientes_provisionales_creados', to=settings.AUTH_USER_MODEL)),
                ('negocio', models.ForeignKey(help_text='Negocio al que pertenece este cliente provisional', on_delete=django.db.models.deletion.CASCADE, related_name='clientes_provisionales', to='negocios.negocio')),
            ],
            options={
                'verbose_name': 'Cliente Provisional',
                'verbose_name_plural': 'Clientes Provisionales',
                'ordering': ['-creado_en'],
            },
        ),
        # Agregar índices a ClienteProvisional
        migrations.AddIndex(
            model_name='clienteprovisional',
            index=models.Index(fields=['negocio', '-creado_en'], name='clientes_cl_negocio_87ff9a_idx'),
        ),
        migrations.AddIndex(
            model_name='clienteprovisional',
            index=models.Index(fields=['telefono'], name='clientes_cl_telefon_81d03c_idx'),
        ),
        # Modificar campo cliente en Reserva para hacerlo opcional
        migrations.AlterField(
            model_name='reserva',
            name='cliente',
            field=models.ForeignKey(blank=True, help_text='Cliente con cuenta en el sistema (opcional si es cliente provisional)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reservas_cliente', to=settings.AUTH_USER_MODEL),
        ),
        # Agregar campo cliente_provisional a Reserva
        migrations.AddField(
            model_name='reserva',
            name='cliente_provisional',
            field=models.ForeignKey(blank=True, help_text='Cliente provisional sin cuenta (opcional si es cliente con cuenta)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to='clientes.clienteprovisional'),
        ),
        # NO renombrar índices de BloqueoCliente - se omiten para evitar errores si no existen
    ]
