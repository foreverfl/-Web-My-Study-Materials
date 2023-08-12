from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Category, Classification, Data
from .forms import CategoryForm, ClassificationForm, DataForm


def index_view(request):
    categories = Category.objects.all()
    return render(request, 'index.html', {'categories': categories})


def layout_view(request):
    categories = Category.objects.all()
    return render(request, 'layout.html', {'categories': categories})


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
    return render(request, 'category.html', {'categories': categories, 'category': category})


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


def classification_detail(request, classification_id):
    classification = get_object_or_404(Classification, pk=classification_id)
    # classification에 해당하는 Data 객체 가져오기
    data_list = Data.objects.filter(classification=classification)
    print("classification_id", classification_id)

    context = {
        'classification': classification,
        'classification_id': classification_id,
        'data_list': data_list  # Data 객체 목록을 템플릿에 전달
    }
    return render(request, 'classification.html', context)


@require_POST
def classification_delete(request, classification_id):
    try:
        classification = Classification.objects.get(pk=classification_id)
        classification.delete()
        return JsonResponse({'status': 'success'})
    except Classification.DoesNotExist:
        return JsonResponse({'error': 'Classification not found'}, status=404)


# Data
def data_create_form(request, classification_id):
    context = {
        'classification_id': classification_id,
    }
    return render(request, 'data_create_form.html', context)


@require_POST
def data_create(request, classification_id):
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
    return redirect('data_detail', classification_id=classification_id, data_id=data.id)


def data_list(request):
    data_list = Data.objects.all()
    data = [{'id': item.id, 'name': item.name} for item in data_list]
    return JsonResponse(data, safe=False)


def data_detail(request, classification_id, data_id):
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
        'classification_id': classification_id,
        'data_id': data_id,
        'stars': stars,
    }
    return render(request, 'data.html', context)


def data_update_form(request, classification_id, data_id):
    data = get_object_or_404(Data, pk=data_id)

    context = {
        'data': data,
        'classification_id': classification_id,
    }

    return render(request, 'data_update_form.html', context)


@require_POST
def data_update(request, classification_id, data_id):
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
    return redirect('data_detail', classification_id=classification_id, data_id=data_id)


@require_POST
def data_delete(request, classification_id, data_id):
    data = get_object_or_404(Data, pk=data_id)  # 해당 data_id를 가진 객체를 찾음
    data.delete()  # 객체 삭제
    return redirect('classification_detail', classification_id=classification_id)

# Search


def search(request):

    query = request.GET.get('q', '')  # 검색어 가져오기
    print(query)

    # 각 필드별로 검색 진행
    name_results = Data.objects.filter(name__icontains=query)
    concept_results = Data.objects.filter(concept__icontains=query)
    features_results = Data.objects.filter(features__icontains=query)
    command_results = Data.objects.filter(command__icontains=query)
    frequency_results = Data.objects.filter(frequency__contains=query)
    code_results = Data.objects.filter(code__icontains=query)
    others_results = Data.objects.filter(others__icontains=query)

    print(name_results)

    context = {
        'name_results': name_results,
        'concept_results': concept_results,
        'features_results': features_results,
        'command_results': command_results,
        'frequency_results': frequency_results,
        'code_results': code_results,
        'others_results': others_results,
    }

    return render(request, 'search.html', context)
