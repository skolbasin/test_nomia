# Generated by Django 5.0.3 on 2024-04-03 20:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0005_alter_answer_clarification_alter_question_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surveys', to='questionnaire.question', verbose_name='Вопрос'),
        ),
    ]
