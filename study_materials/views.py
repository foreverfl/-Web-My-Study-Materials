import logging
from datetime import timezone

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from markdownx.utils import markdownify

from .forms import CategoryForm, ClassificationForm, DataForm
from .models import Notice, Category, Classification, Data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def index_view(request):
    categories = Category.objects.all()
    notices = Notice.objects.all().order_by('-date')  # 날짜 내림차순으로 정렬
    context = {
        'categories': categories,
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
    form = CategoryForm(request.POST)
    form.user = request.user
    if form.is_valid():  # user 필드가 필수가 아니므로 이 시점에서 유효성 검사 가능
        category = form.save(commit=False)
        category.user = request.user  # user 필드에 현재 로그인된 사용자 할당
        category.save()
        return JsonResponse({"status": "success"}, status=201)
    else:
        return JsonResponse({"status": "error", "errors": form.errors}, status=400)


@require_POST
def category_update(request):
    for index in range(len(request.POST)//2):
        category_id = request.POST.get(f'category_id_{index}')
        category_name = request.POST.get(f'category_name_{index}')
        category = get_object_or_404(Category, id=category_id)
        category.name = category_name
        category.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('index')))


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


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})


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
    # icontains: 대소문자를 구분하지 않는 포함 검색
    # distinct(): 중복된 결과를 제거
    results = Data.objects.filter(
        Q(name__icontains=query) |
        Q(concept__icontains=query) |
        Q(features__icontains=query) |
        Q(command__icontains=query) |
        Q(frequency__contains=query) |
        Q(code__icontains=query) |
        Q(others__icontains=query)
    ).distinct()

    logger.info(query)

    context = {
        'results': results,
    }

    return render(request, 'search.html', context)
