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
    classifications = Classification.objects.all()
    return render(request, 'classification.html', {'classifications': classifications, 'classification': classification})


@require_POST
def classification_delete(request, classification_id):
    try:
        classification = Classification.objects.get(pk=classification_id)
        classification.delete()
        return JsonResponse({'status': 'success'})
    except Classification.DoesNotExist:
        return JsonResponse({'error': 'Classification not found'}, status=404)


# Data
def data_create_form(request):
    return render(request, 'data_create_form.html')


@require_POST
def data_create(request):
    classification_id = request.POST.get('classification_id')
    classification = get_object_or_404(Classification, pk=classification_id)

    data = Data.objects.create(
        classification=classification,
        name=request.POST.get('name'),
        concept=request.POST.get('concept'),
        features=request.POST.get('features'),
        command=request.POST.get('command'),
        frequency=request.POST.get('frequency'),
        code=request.POST.get('code'),
        others=request.POST.get('others'),
    )
    return JsonResponse({"status": "success"}, status=201)


def data_list(request):
    data_list = Data.objects.all()
    data = [{'id': item.id, 'name': item.name} for item in data_list]
    return JsonResponse(data, safe=False)


def data_detail(request, data_id):
    data = get_object_or_404(Data, pk=data_id)
    response_data = {
        'name': data.name,
        'concept': data.concept,
        'features': data.features,
        'command': data.command,
        'frequency': data.frequency,
        'code': data.code,
        'others': data.others,
    }
    return JsonResponse(response_data)


@require_POST
def data_update(request, data_id):
    data = get_object_or_404(Data, pk=data_id)
    data.name = request.POST.get('name')
    data.concept = request.POST.get('concept')
    data.features = request.POST.get('features')
    data.command = request.POST.get('command')
    data.frequency = request.POST.get('frequency')
    data.code = request.POST.get('code')
    data.others = request.POST.get('others')
    data.save()
    return JsonResponse({"status": "success"})


@require_POST
def data_delete(request, data_id):
    data = get_object_or_404(Data, pk=data_id)
    data.delete()
    return JsonResponse({"status": "success"})
