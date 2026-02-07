from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('negocios', '0001_initial'),
        ('cuentas', '0013_emailtracking'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessCheckoutIntent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_negocio', models.CharField(max_length=150)),
                ('email_contacto', models.EmailField(max_length=254)),
                ('telefono_contacto', models.CharField(blank=True, max_length=30)),
                ('numero_barberos', models.PositiveIntegerField(default=1)),
                ('precio_mensual', models.DecimalField(decimal_places=2, default=Decimal('49000.00'), max_digits=10)),
                ('moneda', models.CharField(default='COP', max_length=5)),
                ('trial_inicio', models.DateTimeField(default=django.utils.timezone.now)),
                ('trial_fin', models.DateTimeField(blank=True, null=True)),
                ('auto_cobro', models.BooleanField(default=True)),
                ('payu_customer_id', models.CharField(blank=True, max_length=100)),
                ('payu_token', models.CharField(blank=True, max_length=150)),
                ('payu_card_mask', models.CharField(blank=True, help_text='Últimos dígitos o referencia segura', max_length=30)),
                ('payu_state', models.CharField(choices=[('trial_activo', 'Trial activo'), ('metodo_guardado', 'Método de pago guardado'), ('pendiente', 'Pendiente'), ('cancelado', 'Cancelado')], default='pendiente', max_length=30)),
                ('notas', models.TextField(blank=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('negocio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checkout_intents', to='negocios.negocio')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checkout_intents', to='cuentas.usuariopersonalizado')),
            ],
            options={
                'verbose_name': 'Intento de checkout de negocio',
                'verbose_name_plural': 'Intentos de checkout de negocio',
                'ordering': ['-creado_en'],
            },
        ),
    ]

