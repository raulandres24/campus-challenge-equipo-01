# Migración escrita a mano: solo agrega los dos campos nuevos.
# (Los cambios de verbose_name que Django detecta en 0001 vienen de antes y no afectan a MongoDB.)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservas", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="estudiante",
            name="nivel",
            field=models.CharField(
                choices=[("pregrado", "Pregrado"), ("postgrado", "Postgrado"), ("doctorado", "Doctorado")],
                default="pregrado",
                help_text="Define qué salas puede reservar (ver reservas/niveles.py).",
                max_length=10,
                verbose_name="Nivel académico",
            ),
        ),
        migrations.AddField(
            model_name="sala",
            name="exclusiva_posgrado",
            field=models.BooleanField(
                default=False,
                help_text="Si está marcada, solo la reservan estudiantes de postgrado o doctorado (salas A y E).",
                verbose_name="¿Exclusiva de postgrado y doctorado?",
            ),
        ),
    ]
