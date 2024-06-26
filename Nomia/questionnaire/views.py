import logging
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from .config import question_titles
from .forms import SurveyForm, InstitutionForm, BusinessForm
from .models import Question, Answer, Institution

logger = logging.getLogger(__name__)


class EnterView(View):
    """
    Cтартовая страница при входе в личный кабинет
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        question = Question.objects.get(title=question_titles['enter_question'])
        selected_answers = Answer.objects.filter(survey__question=question)

        form = SurveyForm(instance=question)
        form.fields['answers'].queryset = selected_answers

        context = {
            'form': form,
            'question': question,
            'selected_answers': selected_answers
        }
        logger.info('Пользователь зашел на стартовую страницу')
        return render(request, 'questionnaire/enter.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SurveyForm(request.POST)

        if form.is_valid():
            selected_answer = str(form.cleaned_data['answers'][0].text)

            if selected_answer == 'Создайте первое заведение':
                return redirect((reverse('questionnaire:create_institution')))
            elif selected_answer == 'Зайти в личный кабинет':
                return redirect((reverse('questionnaire:account')))

        return render(request, 'questionnaire/invalid_form.html')


class CreateInstitution(View):
    """
    Страница с созданием заведения(название и адрес)
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        form = InstitutionForm()
        question = Question.objects.get(title=question_titles['create_institution_question'])

        context = {
            'form': form,
            'question': question,
        }
        logger.info('Пользователь выбрал создание заведения')
        return render(request, 'questionnaire/create_institution.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = InstitutionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            city_country = form.cleaned_data['city_country']
            address = form.cleaned_data['address']

            if Institution.objects.filter(name=name).exists():
                form.add_error('name', 'Заведение с таким названием уже существует')
                return render(request, 'questionnaire/create_institution.html', {'form': form})

            new_institution = Institution(name=name, city_country=city_country, address=address)
            new_institution.save()
            logger.info('Пользователь зарегистрировался успешно')

            request.session['new_institution'] = {
                'name': new_institution.name,
                'city_country': new_institution.city_country,
                'address': new_institution.address
            }
            return redirect('questionnaire:business_type')

        return render(request, 'questionnaire/invalid_form.html')


class Account(View):
    """
    Страница с личным кабинетом
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            'user': User.objects.get(id=1)  # в дальнейшем переделать на юзера из сессии
        }
        logger.info('Пользователь зашел в личный кабинет')
        return render(request, 'questionnaire/account.html', context=context)


class BusinessType(View):
    """
    Страница с выбором типов бизнеса
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        form = BusinessForm(request.POST)
        question = Question.objects.get(title=question_titles['business_type_question'])

        context = {
            'form': form,
            'question': question
        }

        return render(request, 'questionnaire/business_type.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = BusinessForm(request.POST)

        if form.is_valid():
            business_type = form.cleaned_data['business_type']
            name = request.session.get('new_institution')['name']

            try:
                institution = Institution.objects.get(name=name)
            except Institution.DoesNotExist:
                institution = None

            if institution:
                institution.business_type = business_type
                institution.save()

            if business_type == 'restaurant':
                logger.info('Пользователь выбрал тип бизнеса общепит')
                return redirect((reverse('questionnaire:catering')))
            elif business_type == 'retail':
                logger.info('Пользователь выбрал тип бизнеса ритейл')
                return redirect((reverse('questionnaire:retail')))
            elif business_type == 'services':
                logger.info('Пользователь выбрал тип бизнеса услуги')
                return redirect((reverse('questionnaire:services_type')))

        return render(request, 'questionnaire/invalid_form.html')


class Catering(View):
    """
    Страница с выбором типом заведения в общепите
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        question = Question.objects.get(title=question_titles['catering_question'])
        selected_answers = Answer.objects.filter(survey__question=question)

        form = SurveyForm(instance=question)
        form.fields['answers'].queryset = selected_answers

        context = {
            'form': form,
            'question': question
        }

        return render(request, 'questionnaire/catering.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SurveyForm(request.POST)

        if form.is_valid():
            direction = str(form.cleaned_data['answers'][0].text)
            name = request.session.get('new_institution')['name']
            institution = Institution.objects.get(name=name)
            institution.direction = direction
            institution.save()
            logger.info('Пользователь выбрал тип заведения в общепите')
            return redirect((reverse('questionnaire:catering_type')))

        return render(request, 'questionnaire/invalid_form.html')


class CateringType(View):
    """
    Страница с выбором типов сервисов в общепите
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        question = Question.objects.get(title=question_titles['catering_type_question'])
        selected_answers = Answer.objects.filter(survey__question=question)

        form = SurveyForm(instance=question)
        form.fields['answers'].queryset = selected_answers

        context = {
            'form': form,
            'question': question
        }

        return render(request, 'questionnaire/catering_type.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SurveyForm(request.POST)

        if form.is_valid():
            service_type = str(form.cleaned_data['answers'][0].text)
            name = request.session.get('new_institution')['name']
            institution = Institution.objects.get(name=name)
            institution.service_type = service_type
            institution.save()
            logger.info('Пользователь выбрал тип сервиса в общепите')
            return redirect((reverse('questionnaire:account')))

        return render(request, 'questionnaire/invalid_form.html')


class Retail(View):
    """
    Страница с выбором типа ритейла
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        question = Question.objects.get(title=question_titles['retail_question'])
        selected_answers = Answer.objects.filter(survey__question=question)

        form = SurveyForm(instance=question)
        form.fields['answers'].queryset = selected_answers

        context = {
            'form': form,
            'question': question
        }

        return render(request, 'questionnaire/retail.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SurveyForm(request.POST)

        if form.is_valid():
            direction = str(form.cleaned_data['answers'][0].text)
            name = request.session.get('new_institution')['name']
            institution = Institution.objects.get(name=name)
            institution.direction = direction
            institution.save()
            logger.info('Пользователь выбрал тип ритейла')
            return redirect((reverse('questionnaire:retail_type')))

        return render(request, 'questionnaire/invalid_form.html')


class RetailType(View):
    """
    Страница с выбором вида заказов в ритейле
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        question = Question.objects.get(title=question_titles['retail_type_question'])
        selected_answers = Answer.objects.filter(survey__question=question)

        form = SurveyForm(instance=question)
        form.fields['answers'].queryset = selected_answers

        context = {
            'form': form,
            'question': question
        }

        return render(request, 'questionnaire/retail_type.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SurveyForm(request.POST)

        if form.is_valid():
            service_type = str(form.cleaned_data['answers'][0].text)
            name = request.session.get('new_institution')['name']
            institution = Institution.objects.get(name=name)
            institution.service_type = service_type
            institution.save()
            logger.info('Пользователь выбрал вид заказов в ритейле')
            return redirect((reverse('questionnaire:account')))

        return render(request, 'questionnaire/invalid_form.html')


class ServicesType(View):
    """
    Страница с выбором типом услуг
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        question = Question.objects.get(title=question_titles['services_type_question'])
        selected_answers = Answer.objects.filter(survey__question=question)

        form = SurveyForm(instance=question)
        form.fields['answers'].queryset = selected_answers

        context = {
            'form': form,
            'question': question
        }

        return render(request, 'questionnaire/services_type.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SurveyForm(request.POST)

        if form.is_valid():
            service_type = str(form.cleaned_data['answers'][0].text)
            name = request.session.get('new_institution')['name']
            institution = Institution.objects.get(name=name)
            institution.service_type = service_type
            institution.save()
            logger.info('Пользователь выбрал тип услуг')
            return redirect((reverse('questionnaire:account')))

        return render(request, 'questionnaire/invalid_form.html')
