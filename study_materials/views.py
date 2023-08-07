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


def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    categories = Category.objects.all()
    return render(request, 'category.html', {'categories': categories, 'category': category})


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})


@require_POST
def category_new(request):
    form = CategoryForm(request.POST)
    if form.is_valid():
        # 데이터가 조건을 모두 만족하면, form 인스턴스의 save 메소드를 호출하여 해당 데이터를 DB에 저장.
        form.save()
        return JsonResponse({"status": "success"}, status=201)
    else:
        return JsonResponse({"status": "error", "errors": form.errors}, status=400)


@require_POST  # POST 요청만을 받아들이도록 강제
def category_delete(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        category.delete()
        return JsonResponse({'status': 'ok'})
    except Category.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '카테고리를 찾을 수 없습니다.'}, status=404)

# Classification


def classification_list(request):
    classifications = Classification.objects.all()
    return JsonResponse(list(classifications.values()), safe=False)


def classification_detail(request, classification_id):
    try:
        classification = Classification.objects.get(pk=classification_id)
        return JsonResponse(classification)
    except Classification.DoesNotExist:
        return JsonResponse({'error': 'Classification not found'}, status=404)


@require_POST
def classification_create(request):
    category_id = request.POST.get('category_id')
    name = request.POST.get('name')
    category = Category.objects.get(pk=category_id)
    classification = Classification.objects.create(
        category=category, name=name)
    return JsonResponse(classification, status=201)


@require_POST
def classification_update(request, classification_id):
    try:
        classification = Classification.objects.get(pk=classification_id)
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        category = Category.objects.get(pk=category_id)
        classification.category = category
        classification.name = name
        classification.save()
        return JsonResponse(classification)
    except Classification.DoesNotExist:
        return JsonResponse({'error': 'Classification not found'}, status=404)


@require_POST
def classification_delete(request, classification_id):
    try:
        classification = Classification.objects.get(pk=classification_id)
        classification.delete()
        return JsonResponse({'status': 'ok'})
    except Classification.DoesNotExist:
        return JsonResponse({'error': 'Classification not found'}, status=404)


# Data
