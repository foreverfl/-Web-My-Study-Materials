# 표준 라이브러리
import base64
import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
import pytz

# 서드파티 라이브러리
from allauth.socialaccount.models import SocialAccount
from apscheduler.schedulers.background import BackgroundScheduler
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from markdownx.utils import markdownify
import requests

# 애플리케이션 내부 모듈
from .forms import NoticeForm, CategoryForm, ClassificationForm, DataForm
from .models import Subscription, Notice, Category, Classification, Data
from .context_processors import common_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def index_view(request):
    notices = Notice.objects.all().order_by('-date')  # 날짜 내림차순으로 정렬
    context = {
        'notices': notices,
    }
    return render(request, 'index.html', context)


def notice_create_form(request):
    return render(request, 'notice_create_form.html')


@require_POST
def notice_create(request):  # Notice 생성
    title = request.POST.get('title')
    content = request.POST.get('content')
    notice = Notice(title=title, content=content,
                    user=request.user, date=timezone.now())
    notice.save()
    return redirect('notice_detail', notice_id=notice.id)


def notice_detail(request, notice_id):  # Notice 상세보기
    notice = get_object_or_404(Notice, pk=notice_id)
    notice.content = markdownify(notice.content)  # Markdown 형식의 내용을 HTML로 변환
    context = {
        'notice': notice
    }
    return render(request, 'notice.html', context)


@login_required
def notice_update_form(request, notice_id):
    notice = get_object_or_404(Notice, pk=notice_id)

    # 권한 검사 (글 작성자 혹은 관리자만 수정 가능하도록)
    if request.user != notice.user and not request.user.is_superuser:
        return redirect('some_error_page')  # 권한 없음 오류 페이지로 리다이렉션

    context = {
        'notice': notice
    }
    return render(request, 'notice_update_form.html', context)


@require_POST
def notice_update(request, notice_id):  # Notice 수정
    notice = get_object_or_404(Notice, pk=notice_id)
    notice.title = request.POST.get('title')
    notice.content = request.POST.get('content')
    notice.save()
    return redirect('notice_detail', notice_id=notice.id)


def notice_delete(request, notice_id):  # Notice 삭제
    notice = get_object_or_404(Notice, pk=notice_id)
    notice.delete()
    # index는 목록 페이지로 돌아가는 URL 패턴의 이름이어야 함
    return HttpResponseRedirect(reverse('index'))


# Category

@require_POST
@login_required
def category_create(request):
    user = request.user
    subscription = Subscription.objects.get(user=user)
    current_categories_count = Category.objects.filter(user=user).count()
    if subscription.is_subscribed:
        max_categories = 10
    else:
        max_categories = 1

    if current_categories_count >= max_categories:
        return JsonResponse({"status": "error", "errors": "Maximum number of categories reached"}, status=400)

    form = CategoryForm(request.POST)
    form.user = request.user
    if form.is_valid():  # user 필드가 필수가 아니므로 이 시점에서 유효성 검사 가능
        category = form.save(commit=False)
        category.user = request.user  # user 필드에 현재 로그인된 사용자 할당
        category.save()
        return JsonResponse({"status": "success"}, status=201)
    else:
        return JsonResponse({"status": "error", "errors": form.errors}, status=400)


def category_detail(request, category_id):
    logger.info('test')
    category = get_object_or_404(Category, pk=category_id)
    categories = Category.objects.all()
    classifications = Classification.objects.filter(category=category)
    context = {
        'categories': categories,
        'category': category,
        'classifications': classifications
    }
    return render(request, 'category.html', context)


@require_POST
def category_update(request):
    for index in range(len(request.POST)//2):
        category_id = request.POST.get(f'category_id_{index}')
        category_name = request.POST.get(f'category_name_{index}')
        category = get_object_or_404(Category, id=category_id)
        category.name = category_name
        category.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('index')))


@require_POST  # POST 요청만을 받아들이도록 강제
def category_delete(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        category.delete()
        return JsonResponse({'status': 'ok'})
    except Category.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '카테고리를 찾을 수 없습니다.'}, status=404)


# Classification
@require_POST
def classification_create(request, category_id):
    try:
        name = request.POST.get('name')
        category = get_object_or_404(Category, pk=category_id)
        classification = Classification.objects.create(
            category=category, name=name)
        return JsonResponse({"status": "success"}, status=201)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


def classification_list(request):
    classifications = Classification.objects.all()
    return JsonResponse(list(classifications.values()), safe=False)


def classification_detail(request, category_id, classification_id):
    category = get_object_or_404(Category, pk=category_id)
    classification = get_object_or_404(Classification, pk=classification_id)
    # Data 모델에서 classification 필드의 값이 변수 classification과 일치하는 객체들을 필터링하여 가져옴
    data_list = Data.objects.filter(classification=classification)
    context = {
        'category': category,
        'category_id': category_id,
        'classification': classification,
        'classification_id': classification_id,
        'data_list': data_list  # Data 객체 목록을 템플릿에 전달
    }
    return render(request, 'classification.html', context)


@require_POST
def classification_update(request, category_id):
    for index in range(len(request.POST)//2):
        classification_id = request.POST.get(f'classification_id_{index}')
        classification_name = request.POST.get(f'classification_name_{index}')
        classification = get_object_or_404(
            Classification, id=classification_id)
        classification.name = classification_name
        classification.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('index')))


@require_POST
def classification_delete(request, category_id, classification_id):
    try:
        classification = Classification.objects.get(pk=classification_id)
        classification.delete()
        return JsonResponse({'status': 'success'})
    except Classification.DoesNotExist:
        return JsonResponse({'error': 'Classification not found'}, status=404)


# Data
def data_create_form(request, category_id, classification_id):
    context = {
        'category_id': category_id,
        'classification_id': classification_id,
    }
    return render(request, 'data_create_form.html', context)


@require_POST
def data_create(request, category_id, classification_id):
    # 폼에서 전송된 데이터 가져오기
    name = request.POST['name']
    description = request.POST['description']
    frequency = 1  # frequency는 1로 설정하거나 다른 방식으로 처리할 수 있습니다.

    # Data 객체 생성 및 저장
    data = Data(
        classification=Classification.objects.get(pk=classification_id),
        name=name,
        description=description,
        frequency=frequency
    )
    data.save()

    # 저장 후 해당 데이터의 세부 페이지로 리다이렉션
    return redirect('data_detail', category_id=category_id, classification_id=classification_id, data_id=data.id)


def data_detail(request, category_id, classification_id, data_id):
    category = get_object_or_404(Category, pk=category_id)  # category 쿼리
    classification = get_object_or_404(
        Classification, pk=classification_id)  # classification 쿼리
    data = get_object_or_404(Data, pk=data_id)
    stars = '☆' * data.frequency
    # markdownify 함수를 사용하여 Markdown 형식으로 변환
    description = markdownify(data.description)
    context = {
        'name': data.name,
        'description': description,
        'frequency': data.frequency,
        'category_id': category_id,
        'classification_id': classification_id,
        'data_id': data_id,
        'stars': stars,
        'category': category,
        'classification': classification,
    }
    return render(request, 'data.html', context)


def data_update_form(request, category_id, classification_id, data_id):
    data = get_object_or_404(Data, pk=data_id)

    context = {
        'data': data,
        'category_id': category_id,
        'classification_id': classification_id,
    }

    return render(request, 'data_update_form.html', context)


@require_POST
def data_update(request, category_id, classification_id, data_id):
    data = get_object_or_404(Data, pk=data_id)
    data.name = request.POST.get('name')
    data.description = request.POST.get('description')
    data.frequency = int(request.POST.get('frequency'))
    data.save()

    # 저장 후 상세 페이지로 리다이렉션
    return redirect('data_detail', category_id=category_id, classification_id=classification_id, data_id=data_id)


@require_POST
def data_delete(request, category_id, classification_id, data_id):
    data = get_object_or_404(Data, pk=data_id)  # 해당 data_id를 가진 객체를 찾음
    data.delete()  # 객체 삭제
    return redirect('classification_detail', category_id=category_id, classification_id=classification_id)


# Search


def search(request):
    query = request.GET.get('q', '')  # 검색어 가져오기

    # 각 필드별로 검색 진행
    # __icontains: 대소문자를 구분하지 않음
    # distinct(): 중복된  결과를 제거함
    results = Data.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(frequency__icontains=query)
    ).distinct()

    context = common_context(request)

    context['my_categories'] = []
    context['added_categories'] = []

    for data in results:
        category = data.classification.category
        classification = data.classification

        target_list = []  # 선택된 카테고리 목록을 담을 변수를 초기화

        if category.user == request.user:
            target_list.append(context['my_categories'])

        if category.user.is_superuser:
            target_list.append(context['added_categories'])

        for target_categories in target_list:
            category_data = next(
                (item for item in target_categories if item['name'] == category.name), None)
            if not category_data:
                category_data = {'name': category.name, 'classifications': []}
                target_categories.append(category_data)

            classification_data = next(
                (item for item in category_data['classifications'] if item['name'] == classification.name), None)
            if not classification_data:
                classification_data = {
                    'name': classification.name, 'datas': []}
                category_data['classifications'].append(classification_data)

            data_detail = {
                'name': data.name,
                'id': data.id,
                'classification_id': classification.id,
                'category_id': category.id
            }
            classification_data['datas'].append(data_detail)

    return render(request, 'search.html', context)

# Payment


def payment_describe(request):
    return render(request, 'payment_describe.html')


def read_secret():
    secrets_path = finders.find('secrets.txt')
    client_key = None
    secret_key = None

    with open(secrets_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=', 1)  # split(delimiter, cnt_max_to_divide)
            if key == 'payment_client_key':
                client_key = value

            if key == 'payment_secret_key':
                secret_key = value

            if client_key and secret_key:
                break

    return client_key, secret_key


def payment(request):
    client_key, secret_key = read_secret()
    social_account = SocialAccount.objects.get(user=request.user)

    context = {
        'client_key': client_key,
        'uid': social_account.uid,
    }

    return render(request, 'payment.html', context)


def payment_success(request):
    client_key, secret_key = read_secret()
    authKey = request.GET.get('authKey')
    customerKey = request.GET.get('customerKey')

    # 빌링키 발급받기
    url_billing_key = "https://api.tosspayments.com/v1/billing/authorizations/issue"
    userpass = secret_key + ':'
    encoded_u = base64.b64encode(userpass.encode()).decode()

    headers = {
        "Authorization": "Basic %s" % encoded_u,
        "Content-Type": "application/json"
    }

    params_billing_key = {
        "authKey": authKey,
        "customerKey": customerKey,
    }

    res = requests.post(url_billing_key, data=json.dumps(
        params_billing_key), headers=headers)
    resjson = res.json()
    pretty = json.dumps(resjson, indent=4, ensure_ascii=False)
    logger.info(f"Response JSON: {pretty}")

    billingKey = resjson["billingKey"]
    cardCompany = resjson["cardCompany"]
    cardNumber = resjson["cardNumber"]

    # 빌링키로 결제하기
    url_payment = "https://api.tosspayments.com/v1/billing/"
    params_payment = {
        "orderId": int(time.time()),
        "amount": 300,
        "customerKey": customerKey,
        "orderName": "MyStudyMaterials 구독",
        "customerName": "이름",
        "customerEmail": "이메일"
    }

    res = requests.post(url_payment + billingKey,
                        data=json.dumps(params_payment), headers=headers)
    resjson = res.json()
    pretty = json.dumps(resjson, indent=4, ensure_ascii=False)
    logging.info(pretty)

    if resjson.get('status') == 'DONE':
        subscription, created = Subscription.objects.get_or_create(
            user=request.user)
        subscription.is_subscribed = True
        subscription.start_date = timezone.now()
        subscription.end_date = timezone.now() + timedelta(days=30)  # 30일 뒤에 만료
        subscription.payment_status = 'completed'
        subscription.billing_key = billingKey  # 빌링키 저장
        subscription.save()
        logging.info('saved')
    else:
        logging.info('failed to save')

    context = {
        "res": pretty,
        "billingKey": billingKey,
        "cardCompany": cardCompany,
        "cardNumber": cardNumber,
    }

    return render(request, "payment_success.html", context)


def payment_fail(request):
    code = request.GET.get('code')
    message = request.GET.get('message')
    context = {
        "code": code,
        "message": message,
    }
    return render(request, "payment_fail.html", context)


# 자동 결제


def check_subscriptions():
    client_key, secret_key = read_secret()

    subscriptions = Subscription.objects.all()
    for subscription in subscriptions:
        user = subscription.user
        social_account = SocialAccount.objects.get(user=user)
        billingKey = subscription.billing_key

        # 결제 로직
        url_payment = "https://api.tosspayments.com/v1/billing/"
        userpass = secret_key + ':'
        encoded_u = base64.b64encode(userpass.encode()).decode()

        headers = {
            "Authorization": "Basic %s" % encoded_u,
            "Content-Type": "application/json"
        }

        params_payment = {
            "orderId": int(time.time()),
            "amount": 300,
            "customerKey": social_account.uid,
            "orderName": "MyStudyMaterials 구독",
            "customerName": user.username,
            "customerEmail": user.email,
        }

        res = requests.post(url_payment + billingKey,
                            data=json.dumps(params_payment), headers=headers)
        resjson = res.json()
        pretty = json.dumps(resjson, indent=4, ensure_ascii=False)
        logging.info(pretty)

        if resjson.get('status') == 'DONE':
            subscription.end_date = timezone.now() + timedelta(days=30)  # 30일 뒤로 만료일 갱신
            subscription.payment_status = 'completed'  # 결제 상태를 완료로 설정
            subscription.save()  # DB에 저장

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"Auto-renewed subscription for {user.username} at {current_time}"
            logging.info(log_message)
        else:
            logging.info(f"Failed to renew subscription for {user.username}")


# scheduler = BackgroundScheduler()
# scheduler.add_job(check_subscriptions, 'interval', minutes=1)  # 1분마다 실행
# scheduler.start()
