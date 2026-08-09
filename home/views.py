from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Avg
from django.views.decorators.csrf import csrf_exempt
import json
import os
import urllib.request
import urllib.error
from .models import Product, ProductImage, Pricing, QuoteRequest, PhoneNumber, Review, Category


OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
OPENROUTER_MODELS = [
    'cohere/north-mini-code:free',
    'google/gemma-4-26b-a4b-it:free',
    'nvidia/nemotron-nano-9b-v2:free',
]


def get_products_context():
    products = Product.objects.prefetch_related('pricings').all()
    product_lines = []
    for p in products:
        pricings = p.pricings.all().order_by('moq')
        pricing_str = ', '.join([f"MOQ {pr.moq} pcs = Rs.{pr.price}" for pr in pricings]) if pricings else "No pricing set"
        phone = p.phone_number if p.phone_number else "Not available"
        product_lines.append(
            f"- SKU: {p.sku} | Description: {p.description} | Dimensions: {p.dimensions or 'N/A'} | "
            f"Material: {p.material or 'N/A'} | Colors: {p.colors_variants or 'N/A'} | "
            f"Weight: {p.weight or 'N/A'} | Packaging: {p.packaging or 'N/A'} | "
            f"Pricing: {pricing_str} | Phone for order: {phone} | "
            f"Product URL: /product/{p.id}/"
        )
    return '\n'.join(product_lines)


@csrf_exempt
def chatbot_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)

    products_context = get_products_context()

    system_prompt = f"""You are "DecorBot", the AI assistant for The Decor Edits - a premium home decor website based in India.

You help customers find products, check pricing, MOQ details, and connect with the seller.

RULES:
1. ONLY answer questions related to The Decor Edits products and services.
2. If a customer asks about a specific product, give them the SKU, description, dimensions, pricing (MOQ), and phone number.
3. Always be polite, professional, and helpful.
4. If you don't know something, say so honestly.
5. Keep responses short and to the point (2-4 lines max unless more detail is needed).
6. When listing products, format them nicely with bullet points.
7. Always mention the phone number so customers can call directly.
8. If asked about shipping, delivery, or other business questions, give general helpful answers about The Decor Edits.

PRODUCT CATALOG:
{products_context}

The Decor Edits is located in India. Phone for inquiries: Use the phone number from the product details above.
Website: thedecoredits.com"""

    messages_list = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    last_error = None
    for model in OPENROUTER_MODELS:
        try:
            payload = json.dumps({
                "model": model,
                "messages": messages_list,
                "max_tokens": 1024,
                "temperature": 0.7,
            }).encode('utf-8')

            req = urllib.request.Request(
                'https://openrouter.ai/api/v1/chat/completions',
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                    'HTTP-Referer': 'https://thedecoredits.com',
                    'X-Title': 'The Decor Edits Chatbot',
                },
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                ai_reply = result['choices'][0]['message']['content']
                if not ai_reply:
                    ai_reply = result['choices'][0]['message'].get('reasoning', '')
                if ai_reply:
                    return JsonResponse({'reply': ai_reply})

        except urllib.error.HTTPError as e:
            last_error = f'{model}: HTTP {e.code}'
            if e.code == 429:
                continue
            error_body = e.read().decode('utf-8') if e.readable() else str(e)
            return JsonResponse({'error': f'API error: {e.code}', 'detail': error_body}, status=502)
        except urllib.error.URLError as e:
            return JsonResponse({'error': f'Connection error: {str(e.reason)}'}, status=502)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

    return JsonResponse({'error': f'All models rate-limited. Try again shortly.', 'detail': last_error}, status=429)


def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('home')


def home(request):
    products = Product.objects.all().order_by('-created_at')[:8]
    categories = Category.objects.all()
    return render(request, 'home.html', {'products': products, 'categories': categories})


def products(request):
    products_data = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    
    category_filter = request.GET.get('category')
    if category_filter:
        products_data = products_data.filter(category_id=category_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        products_data = products_data.filter(description__icontains=search_query)
    
    return render(request, 'products.html', {
        'products': products_data,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_filter,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    pricings = product.pricings.all().order_by('moq')
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    total_reviews = reviews.count()
    product.views_count += 1
    product.save(update_fields=['views_count'])
    return render(request, 'product_detail.html', {
        'product': product,
        'pricings': pricings,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
    })


def quote_form(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    pricings = product.pricings.all().order_by('moq')
    return render(request, 'quote_form.html', {
        'product': product,
        'pricings': pricings,
    })


def quote_submit(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        quantity = request.POST.get('quantity', '1').strip()

        if not full_name or not phone_number:
            messages.error(request, 'Full Name and Phone Number are required')
            return redirect('quote_form', product_id=product.id)

        try:
            quantity = max(1, int(quantity))
        except (ValueError, TypeError):
            quantity = 1

        QuoteRequest.objects.create(
            product=product,
            full_name=full_name,
            phone_number=phone_number,
            quantity=quantity,
        )
        return redirect('thank_you')

    return redirect('quote_form', product_id=product.id)


def thank_you(request):
    return render(request, 'thank_you.html')


def about(request):
    return render(request, 'about.html')


def security_checklist(request):
    return render(request, 'security_checklist.html')


@login_required
def dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    products = Product.objects.prefetch_related('pricings').all().order_by('-created_at')
    total_views = Product.objects.aggregate(total=Sum('views_count'))['total'] or 0
    return render(request, 'dashboard.html', {
        'products': products,
        'total_views': total_views,
    })


@login_required
def dashboard_phones(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            label = request.POST.get('label', '').strip()
            number = request.POST.get('number', '').strip()
            if label and number:
                is_default = not PhoneNumber.objects.exists()
                PhoneNumber.objects.create(label=label, number=number, is_default=is_default)
                messages.success(request, f'Phone "{label}" added')
            else:
                messages.error(request, 'Label and number are required')

        elif action == 'edit':
            phone_id = request.POST.get('phone_id')
            label = request.POST.get('label', '').strip()
            number = request.POST.get('number', '').strip()
            phone = PhoneNumber.objects.filter(id=phone_id).first()
            if phone and label and number:
                phone.label = label
                phone.number = number
                phone.save()
                messages.success(request, f'Phone "{label}" updated')
            else:
                messages.error(request, 'Invalid data')

        elif action == 'set_default':
            phone_id = request.POST.get('phone_id')
            phone = PhoneNumber.objects.filter(id=phone_id).first()
            if phone:
                phone.is_default = True
                phone.save()
                messages.success(request, f'"{phone.label}" set as default')

        elif action == 'delete':
            phone_id = request.POST.get('phone_id')
            phone = PhoneNumber.objects.filter(id=phone_id).first()
            if phone:
                phone.delete()
                messages.success(request, 'Phone deleted')

        return redirect('dashboard_phones')

    phones = PhoneNumber.objects.all()
    return render(request, 'dashboard_phones.html', {'phones': phones})


@login_required
def dashboard_add_product(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')

    if request.method == 'POST':
        sku = request.POST.get('sku', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        category_id = request.POST.get('category')
        dimensions = request.POST.get('dimensions', '').strip()
        material = request.POST.get('material', '').strip()
        colors_variants = request.POST.get('colors_variants', '').strip()
        weight = request.POST.get('weight', '').strip()
        packaging = request.POST.get('packaging', '').strip()

        if not sku or not description or not image:
            messages.error(request, 'SKU, Description, and Image are required')
            return render(request, 'dashboard_add_product.html')

        if Product.objects.filter(sku=sku).exists():
            messages.error(request, f'SKU "{sku}" already exists')
            return render(request, 'dashboard_add_product.html')

        phone_number = request.POST.get('phone_number', '').strip()
        category = Category.objects.filter(id=category_id).first() if category_id else None

        product = Product.objects.create(
            sku=sku,
            description=description,
            image=image,
            category=category,
            dimensions=dimensions,
            material=material,
            colors_variants=colors_variants,
            weight=weight,
            packaging=packaging,
            phone_number=phone_number,
        )

        # Save additional images (up to 4)
        extra_images = request.FILES.getlist('extra_images')
        for idx, img in enumerate(extra_images[:4]):
            ProductImage.objects.create(product=product, image=img, order=idx)

        moq_list = request.POST.getlist('moq')
        price_list = request.POST.getlist('price')
        for moq, price in zip(moq_list, price_list):
            if moq and price:
                Pricing.objects.create(
                    product=product,
                    moq=int(moq),
                    price=float(price),
                )

        messages.success(request, f'Product "{sku}" added successfully')
        return redirect('dashboard')

    phones = PhoneNumber.objects.all()
    categories = Category.objects.all()
    return render(request, 'dashboard_add_product.html', {'phones': phones, 'categories': categories})


@login_required
def dashboard_edit_product(request, product_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        sku = request.POST.get('sku', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        dimensions = request.POST.get('dimensions', '').strip()
        material = request.POST.get('material', '').strip()
        colors_variants = request.POST.get('colors_variants', '').strip()
        weight = request.POST.get('weight', '').strip()
        packaging = request.POST.get('packaging', '').strip()

        if not sku or not description:
            messages.error(request, 'SKU and Description are required')
            return render(request, 'dashboard_edit_product.html', {'product': product})

        if Product.objects.filter(sku=sku).exclude(id=product.id).exists():
            messages.error(request, f'SKU "{sku}" already exists')
            return render(request, 'dashboard_edit_product.html', {'product': product})

        product.sku = sku
        product.description = description
        product.category = Category.objects.filter(id=category_id).first() if category_id else None
        product.dimensions = dimensions
        product.material = material
        product.colors_variants = colors_variants
        product.weight = weight
        product.packaging = packaging
        product.phone_number = request.POST.get('phone_number', '').strip()

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()

        # Handle additional images
        extra_images = request.FILES.getlist('extra_images')
        if extra_images:
            product.images.all().delete()
            for idx, img in enumerate(extra_images[:4]):
                ProductImage.objects.create(product=product, image=img, order=idx)

        product.pricings.all().delete()
        moq_list = request.POST.getlist('moq')
        price_list = request.POST.getlist('price')
        for moq, price in zip(moq_list, price_list):
            if moq and price:
                Pricing.objects.create(
                    product=product,
                    moq=int(moq),
                    price=float(price),
                )

        messages.success(request, f'Product "{sku}" updated successfully')
        return redirect('dashboard')

    pricings = product.pricings.all().order_by('moq')
    extra_images = product.images.all().order_by('order')
    phones = PhoneNumber.objects.all()
    categories = Category.objects.all()
    return render(request, 'dashboard_edit_product.html', {
        'product': product,
        'pricings': pricings,
        'extra_images': extra_images,
        'phones': phones,
        'categories': categories,
    })


@login_required
def dashboard_delete_product(request, product_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, 'Invalid request')
        return redirect('dashboard')

    product = get_object_or_404(Product, id=product_id)
    sku = product.sku
    product.delete()
    messages.success(request, f'Product "{sku}" deleted successfully')
    return redirect('dashboard')


@login_required
def dashboard_manage(request, product_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)
    pricings = product.pricings.all().order_by('moq')
    return render(request, 'dashboard_manage.html', {
        'product': product,
        'pricings': pricings,
    })


@login_required
def dashboard_views_data(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)

    products = Product.objects.all().order_by('-views_count')[:10]
    data = {
        'labels': [p.sku for p in products],
        'views': [p.views_count for p in products],
    }
    return JsonResponse(data)


@login_required
def dashboard_report(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')

    quote_requests = QuoteRequest.objects.select_related('product').all()

    product_filter = request.GET.get('product')
    if product_filter:
        quote_requests = quote_requests.filter(product_id=product_filter)

    total_quotes = quote_requests.count()
    unread_quotes = quote_requests.filter(is_read=False).count()
    products = Product.objects.all().order_by('sku')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_read':
            quote_id = request.POST.get('quote_id')
            if quote_id:
                QuoteRequest.objects.filter(id=quote_id).update(is_read=True)
                messages.success(request, 'Quote marked as read')
        elif action == 'mark_all_read':
            QuoteRequest.objects.filter(is_read=False).update(is_read=True)
            messages.success(request, 'All quotes marked as read')
        elif action == 'delete_quote':
            quote_id = request.POST.get('quote_id')
            if quote_id:
                QuoteRequest.objects.filter(id=quote_id).delete()
                messages.success(request, 'Quote deleted')
        return redirect('dashboard_report')

    return render(request, 'dashboard_report.html', {
        'quote_requests': quote_requests,
        'total_quotes': total_quotes,
        'unread_quotes': unread_quotes,
        'products': products,
        'product_filter': product_filter,
    })


def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        rating = request.POST.get('rating', '5')
        comment = request.POST.get('comment', '').strip()

        if not customer_name or not comment:
            messages.error(request, 'Name and review comment are required')
            return redirect('product_detail', product_id=product.id)

        try:
            rating = max(1, min(5, int(rating)))
        except (ValueError, TypeError):
            rating = 5

        Review.objects.create(
            product=product,
            customer_name=customer_name,
            rating=rating,
            comment=comment,
        )
        messages.success(request, 'Review submitted successfully!')
        return redirect('product_detail', product_id=product.id)

    return redirect('product_detail', product_id=product.id)


@login_required
def dashboard_reviews(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')

    reviews = Review.objects.select_related('product').all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            review_id = request.POST.get('review_id')
            if review_id:
                Review.objects.filter(id=review_id).delete()
                messages.success(request, 'Review deleted')
        return redirect('dashboard_reviews')

    return render(request, 'dashboard_reviews.html', {
        'reviews': reviews,
    })


@login_required
def dashboard_categories(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')

    categories = Category.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            image = request.FILES.get('image')
            if name:
                if Category.objects.filter(name=name).exists():
                    messages.error(request, f'Category "{name}" already exists')
                else:
                    Category.objects.create(name=name, description=description, image=image)
                    messages.success(request, f'Category "{name}" added')
            else:
                messages.error(request, 'Category name is required')

        elif action == 'edit':
            cat_id = request.POST.get('cat_id')
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            cat = Category.objects.filter(id=cat_id).first()
            if cat and name:
                cat.name = name
                cat.description = description
                if request.FILES.get('image'):
                    cat.image = request.FILES.get('image')
                cat.save()
                messages.success(request, f'Category "{name}" updated')
            else:
                messages.error(request, 'Invalid data')

        elif action == 'delete':
            cat_id = request.POST.get('cat_id')
            cat = Category.objects.filter(id=cat_id).first()
            if cat:
                cat.delete()
                messages.success(request, 'Category deleted')

        return redirect('dashboard_categories')

    return render(request, 'dashboard_categories.html', {'categories': categories})
