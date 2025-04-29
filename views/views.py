from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.http import JsonResponse
from account.service import AccountService
from account.models import PasswordResetToken
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from category.models import Category
from product.models import Product
from product.service import ProductService
from product.serializer import ProductForm
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from order.service import OrderService
from order.models import Order
from django.contrib.auth.decorators import user_passes_test

User = get_user_model()

def index(request):
    title = request.GET.get('title', '')
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 3)
    category_name = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    price_range = request.GET.get('price_range')  # dạng "100-500"
    if price_range:
        min_price, max_price = map(int, price_range.split('-'))
    # Gọi service để lấy sản phẩm đã lọc và phân trang
    result = ProductService.list_product(
        page=page,
        page_size=page_size,
        category_name=category_name,
        min_price=min_price,
        max_price=max_price,
        title=title
    )
    
    user_role = request.user.role if request.user.is_authenticated else None

    categories = Category.objects.all()

    context = {
        'categories': categories,
        'products': result['products'],
        'total_pages': result['total_pages'],
        'current_page': int(result['current_page']),
        'total_items': result['total_items'],
        'selected_category': category_name,
        'page_size': page_size,
        'min_price': min_price,
        'max_price': max_price,
        'range_total_pages': range(1, result['total_pages'] + 1),
        'user_role' : user_role
    }

    return render(request, 'index.html', context)

@csrf_exempt
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            tokens = AccountService.login(username, password)  # Retrieve tokens
            
            next_url = request.POST.get('next') or reverse('index')

            response = redirect(next_url)  # Đúng

            # Set cookie lên response redirect
            response.set_cookie('refresh_token', tokens['refresh'], httponly=True)  
            response.set_cookie('access_token', tokens['access'], httponly=True)  
            return response

        else:
            return render(request, 'login.html', {'error': 'Thông tin đăng nhập không chính xác'})

    return render(request, 'login.html')


@csrf_exempt
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            phone = request.POST.get('phone')
            role = request.POST.get('role', 'Customer')  # Default role is 'user'
            address = request.POST.get('address')

            user = AccountService.register(
                username=username,
                full_name=full_name,
                email=email,
                password=password,
                phone=phone,
                role=role,
                address=address
            )
            messages.success(request, "Đăng ký thành công, vui lòng đăng nhập.")
            return redirect('login')

        except ValueError as ve:
            return JsonResponse({'error': str(ve)}, status=400)

        except Exception as e:
            return JsonResponse({'error': 'Đã có lỗi xảy ra.'}, status=500)

    return JsonResponse({'error': 'Chỉ hỗ trợ phương thức POST'}, status=405)

@csrf_exempt
def custom_logout(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if refresh_token:
        try:
            AccountService.logout(refresh_token)  # Blacklist refresh token
        except Exception as e:
            print(f"Error blacklisting token: {e}")
    
    logout(request)  # Log out user from session
    response = redirect('login') 
    response.delete_cookie('refresh_token')
    response.delete_cookie('access_token') 
    return response 

@csrf_exempt
@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        try:
            message = AccountService.change_user_password(request.user, old_password, new_password)
            response = redirect('login')
            response.delete_cookie('refresh_token')  
            response.delete_cookie('access_token') 
            return response

        except (DjangoValidationError, DRFValidationError) as e:
            return render(request, 'change_password.html', {
                'error': "Mật khẩu cũ không đúng",
            })

    return render(request, 'change_password.html')

@csrf_exempt
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token_obj = AccountService.create_token(user)
            reset_url = AccountService.build_reset_url(request, token_obj)
            AccountService.send_reset_email(user, reset_url)
            return render(request, 'mail_success.html', {'success': 'Email đặt lại mật khẩu đã được gửi.'})
        except User.DoesNotExist:
            return render(request, 'forgot_password.html', {'error': 'Email không tồn tại trong hệ thống.'})
    return render(request, 'forgot_password.html')

def mail_success(request):
    return render(request, 'mail_success.html')

@csrf_exempt
def password_reset_confirm(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token, expires_at__gt=timezone.now())
    except PasswordResetToken.DoesNotExist:
        return render(request, 'password_reset_confirm.html', {'error': 'Link không hợp lệ hoặc đã hết hạn.'})

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        token_obj.user.set_password(new_password)
        token_obj.user.save()
        token_obj.delete()  # Xóa token sau khi dùng xong
        return redirect('login')

    return render(request, 'password_reset_confirm.html', {'token': token})


def product_detail(request, slug):
    # Lấy sản phẩm dựa trên slug
    product = get_object_or_404(Product, slug=slug)
    
    # Lấy danh sách các hình ảnh của sản phẩm
    images = product.list_image.all()
    
    # Trả về dữ liệu vào template
    context = {
        'product': product,
        'images': images
    }
    
    return render(request, 'product_detail.html', context)

def add_to_cart_or_checkout(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))  # Mặc định mua 1 nếu không có quantity

        if product.stock >= quantity:
            # Lấy giỏ hàng từ session
            cart = request.session.get('cart', [])
            
            # Kiểm tra nếu sản phẩm đã có trong giỏ hàng
            product_in_cart = next((item for item in cart if item['id'] == product.id), None)

            if product_in_cart:
                product_in_cart['quantity'] += quantity  # Nếu sản phẩm đã có, tăng số lượng
            else:
                cart.append({
                    'id': product.id,
                    'title': product.title,
                    'price': float(product.price),
                    'image': product.image.url if product.image else None,
                    'quantity': quantity
                })

            # Cập nhật giỏ hàng vào session
            request.session['cart'] = cart

            product.stock -= quantity
            product.save()

            if not request.user.is_authenticated:
                login_url = reverse('login')
                checkout_url = reverse('checkout')
                return redirect(f"{login_url}?next={checkout_url}")
            else:
                return redirect('checkout')
        else:
            # Nếu sản phẩm không đủ hàng
            return redirect('product_detail', slug=product.slug)
    else:
        return redirect('product_detail', slug=product.slug)
    
def checkout_view(request):
    # Lấy giỏ hàng từ session
    cart = request.session.get('cart', [])

    # Nếu giỏ hàng trống, chuyển về trang cart (hoặc index)
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('index')  # hoặc redirect('index') nếu bạn không có cart view

    # Tính tổng tiền
    cart_total = sum(item['price'] * item['quantity'] for item in cart)

    if request.method == 'POST':
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')

        # Chuẩn hóa items cho service
        items = [
            {'product_id': item['id'], 'quantity': item['quantity']}
            for item in cart
        ]

        try:
            order = OrderService.create_order(
                user=request.user,
                phone=phone,
                address=address,
                items=items
            )
            # Xóa giỏ hàng sau khi đặt hàng
            request.session['cart'] = []
            messages.success(request, "Order placed successfully!")
            return redirect('order_success')
        except Exception as e:
            messages.error(request, f"Error placing order: {e}")
            return redirect('checkout')

    # Với GET, hiển thị form checkout
    return render(request, 'check_out.html', {
        'cart': cart,
        'cart_total': cart_total
    })
    
    
def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

@user_passes_test(is_admin)
def create_category_view(request, id=None):
    categories = Category.objects.all()
    editing_mode = False
    category_to_edit = None

    if id:  # đang sửa
        category_to_edit = get_object_or_404(Category, id=id)
        editing_mode = True

        if request.method == 'POST':
            name = request.POST.get('name')
            if name:
                category_to_edit.name = name
                category_to_edit.save()
                return redirect('create_category')  # về lại chế độ tạo mới

    elif request.method == 'POST':  # đang tạo mới
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            return redirect('create_category')

    return render(request, 'admin/add-category.html', {
        'categories': categories,
        'editing_mode': editing_mode,
        'category_to_edit': category_to_edit
    })

def delete_category_view(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect('create_category')

@user_passes_test(is_admin)
def product_create_update_view(request, id=None):
    if id:
        product = get_object_or_404(Product, id=id)
    else:
        product = None

    form = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('create_product')  # redirect lại chính trang này

    products = Product.objects.all()
    return render(request, 'admin/add-product.html', {
        'form': form,
        'products': products,
        'editing': id is not None,
    })
    
def delete_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('create_product') 


@login_required
def order_list_view(request):
    if request.user.is_staff:
        orders = Order.objects.all().order_by('-create_at') 
    else:
        orders = Order.objects.filter(user=request.user).order_by('-create_at') 
    return render(request, 'order_list.html', {'orders': orders})
