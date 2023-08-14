from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Category, Classification, Data
from .forms import CategoryForm, ClassificationForm, DataForm


def index_view(request):
    categories = Category.objects.all()
    return render(request, 'index.html', {'categories': categories})


# Category
@require_POST
def category_create(request):
    form = CategoryForm(request.POST)
    if form.is_valid():
        # 데이터가 조건을 모두 만족하면, form 인스턴스의 save 메소드를 호출하여 해당 데이터를 DB에 저장.
        form.save()
        return JsonResponse({"status": "success"}, status=201)
    else:
        return JsonResponse({"status": "error", "errors": form.errors}, status=400)


def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'category': category
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
    concept = request.POST['concept']
    features = request.POST['features']
    command = request.POST['command']
    code = request.POST['code']
    others = request.POST['others']

    # Data 객체 생성 및 저장
    data = Data(
        classification=Classification.objects.get(pk=classification_id),
        name=name,
        concept=concept,
        features=features,
        command=command,
        frequency=1,
        code=code,
        others=others
    )
    data.save()

    # 저장 후 해당 데이터의 세부 페이지로 리다이렉션
    return redirect('data_detail', category_id=category_id, classification_id=classification_id, data_id=data.id)


def data_detail(request, category_id, classification_id, data_id):
    data = get_object_or_404(Data, pk=data_id)
    stars = '☆' * data.frequency
    context = {
        'name': data.name,
        'concept': data.concept,
        'features': data.features,
        'command': data.command,
        'frequency': data.frequency,
        'code': data.code,
        'others': data.others,
        'category_id': category_id,
        'classification_id': classification_id,
        'data_id': data_id,
        'stars': stars,
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
    data.concept = request.POST.get('concept')
    data.features = request.POST.get('features')
    data.command = request.POST.get('command')
    data.frequency = int(request.POST.get('frequency'))
    data.code = request.POST.get('code')
    data.others = request.POST.get('others')
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
    print(query)

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

    print(results)

    context = {
        'results': results,
    }

    return render(request, 'search.html', context)
