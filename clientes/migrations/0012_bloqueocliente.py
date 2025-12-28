from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('negocios', '0001_initial'),
        ('clientes', '0011_add_duracion_servicio_to_reserva'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BloqueoCliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_bloqueo', models.DateTimeField(auto_now_add=True, help_text='Fecha en que se aplicó el bloqueo')),
                ('fecha_desbloqueo', models.DateTimeField(blank=True, help_text='Fecha en que se desbloqueó (si es manual)', null=True)),
                ('motivo', models.TextField(help_text='Motivo del bloqueo (ej: múltiples inasistencias)')),
                ('inasistencias_que_causaron', models.IntegerField(default=0, help_text='Número de inasistencias que causaron el bloqueo')),
                ('activo', models.BooleanField(default=True, help_text='Si el bloqueo está activo')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bloqueos_cliente', to=settings.AUTH_USER_MODEL)),
                ('desbloqueado_por', models.ForeignKey(blank=True, help_text='Usuario que desbloqueó manualmente', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bloqueos_desbloqueados', to=settings.AUTH_USER_MODEL)),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bloqueos_negocio', to='negocios.negocio')),
            ],
            options={
                'verbose_name': 'Bloqueo de Cliente',
                'verbose_name_plural': 'Bloqueos de Clientes',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.AddIndex(
            model_name='bloqueocliente',
            index=models.Index(fields=['cliente', 'negocio', 'activo'], name='clientes_blo_cliente_2c6d2f_idx'),
        ),
        migrations.AddIndex(
            model_name='bloqueocliente',
            index=models.Index(fields=['negocio', 'activo'], name='clientes_blo_negocio_62e6c0_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='bloqueocliente',
            unique_together={('cliente', 'negocio', 'activo')},
        ),
    ]


