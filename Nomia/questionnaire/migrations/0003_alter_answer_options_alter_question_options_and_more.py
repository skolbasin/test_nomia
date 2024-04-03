# Generated by Django 5.0.3 on 2024-04-03 14:54

import questionnaire.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0002_remove_answer_question_question_answers'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'verbose_name': 'Ответ', 'verbose_name_plural': 'Ответы'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'verbose_name': 'Вопрос', 'verbose_name_plural': 'Вопросы'},
        ),
        migrations.AddField(
            model_name='answer',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=questionnaire.models.answer_image_directory_path, verbose_name='Картинка'),
        ),
    ]