from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import Product, Category, Order, OrderItem, Seller, Message, Profile

def product_list(request):
    products   = Product.objects.filter(stock__gt=0)
    categories = Category.objects.all()
    category   = request.GET.get('category')
    search     = request.GET.get('search')

    if category:
        products = products.filter(category__name=category)
    if search:
        products = products.filter(title__icontains=search)

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

def add_to_cart(request, pk):
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')

def cart_view(request):
    cart     = request.session.get('cart', {})
    products = Product.objects.filter(pk__in=cart.keys())
    items    = [{'product': p, 'qty': cart[str(p.pk)], 'subtotal': p.price * cart[str(p.pk)]} for p in products]
    total    = sum(i['subtotal'] for i in items)
    return render(request, 'store/cart.html', {'items': items, 'total': total})

@login_required
def checkout(request):
    cart     = request.session.get('cart', {})
    products = Product.objects.filter(pk__in=cart.keys())
    total    = sum(p.price * cart[str(p.pk)] for p in products)

    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total=total)
        for product in products:
            OrderItem.objects.create(
                order=order, product=product,
                quantity=cart[str(product.pk)], price=product.price
            )
        request.session['cart'] = {}
        return redirect('product_list')

    return render(request, 'store/checkout.html', {'total': total})

def register(request):
    error = ''
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email    = request.POST['email']
        if User.objects.filter(username=username).exists():
            error = 'اسم المستخدم موجود مسبقاً، جرب اسماً آخر'
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            Seller.objects.create(user=user, shop_name=username)
            login(request, user)
            return redirect('product_list')
    return render(request, 'store/register.html', {'error': error})

@login_required
def become_seller(request):
    if hasattr(request.user, 'seller'):
        return redirect('seller_dashboard')
    if request.method == 'POST':
        Seller.objects.create(
            user=request.user,
            shop_name=request.POST['shop_name'],
            description=request.POST['description'],
            phone=request.POST['phone'],
        )
        return redirect('seller_dashboard')
    return render(request, 'store/become_seller.html')

@login_required
def seller_dashboard(request):
    if not hasattr(request.user, 'seller'):
        return redirect('become_seller')
    products = Product.objects.filter(seller=request.user.seller)
    return render(request, 'store/seller_dashboard.html', {'products': products})

@login_required
def add_product(request):
    if not hasattr(request.user, 'seller'):
        return redirect('become_seller')
    if request.method == 'POST':
        Product.objects.create(
            seller=request.user.seller,
            title=request.POST['title'],
            description=request.POST['description'],
            price=request.POST['price'],
            stock=request.POST['stock'],
            category=Category.objects.get(pk=request.POST['category']),
            image=request.FILES.get('image'),
        )
        return redirect('seller_dashboard')
    categories = Category.objects.all()
    return render(request, 'store/add_product.html', {'categories': categories})

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.seller == request.user.seller:
        product.delete()
    return redirect('seller_dashboard')
   
@login_required
def send_message(request, pk):
    product  = get_object_or_404(Product, pk=pk)
    receiver = product.seller.user
    if request.method == 'POST':
        content = request.POST['content']
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            product=product,
            content=content
        )
        return redirect('product_detail', pk=pk)
    return redirect('product_detail', pk=pk)

@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'store/inbox.html', {'messages': messages})

@login_required
def reply_message(request, pk):
    original = get_object_or_404(Message, pk=pk)
    if request.method == 'POST':
        content = request.POST['content']
        Message.objects.create(
            sender=request.user,
            receiver=original.sender,
            product=original.product,
            content=content
        )
        return redirect('inbox')
    return redirect('inbox')

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    error   = ''
    success = ''

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_info':
            profile.first_name = request.POST['first_name']
            profile.last_name  = request.POST['last_name']
            profile.phone      = request.POST['phone']
            profile.save()
            success = 'تم تحديث المعلومات بنجاح!'

        elif action == 'change_password':
            old_password = request.POST['old_password']
            new_password = request.POST['new_password']
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                success = 'تم تغيير كلمة المرور بنجاح!'
            else:
                error = 'كلمة المرور القديمة خاطئة!'

    return render(request, 'store/profile.html', {
        'profile': profile,
        'error':   error,
        'success': success,
    })