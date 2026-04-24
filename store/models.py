from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Seller(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name   = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    phone       = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.shop_name

class Product(models.Model):
    SHIPPING_CHOICES = [
        ('available',     'شحن متوفر'),
        ('local',         'شحن جزئي'),
        ('not_available', 'شحن غير متوفر'),
    ]
    seller      = models.ForeignKey(Seller, on_delete=models.CASCADE)
    title       = models.CharField(max_length=200)
    description = models.TextField()
    price       = models.DecimalField(max_digits=8, decimal_places=2)
    image       = models.ImageField(upload_to='products/', blank=True)
    stock       = models.IntegerField(default=0)
    category    = models.ForeignKey(Category, on_delete=models.CASCADE)
    shipping    = models.CharField(max_length=20, choices=SHIPPING_CHOICES, blank=True)
    wilaya      = models.CharField(max_length=100, blank=True)
    phone       = models.CharField(max_length=20, blank=True)
    website     = models.URLField(blank=True)

    def __str__(self):
        return self.title

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'قيد الانتظار'),
        ('confirmed', 'تم التأكيد'),
        ('shipped',   'تم الشحن'),
        ('delivered', 'تم التسليم'),
        ('cancelled', 'ملغي'),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wilaya     = models.CharField(max_length=100, blank=True)
    commune    = models.CharField(max_length=100, blank=True)
    phone      = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'طلب {self.pk} - {self.user}'

class OrderItem(models.Model):
    order    = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product  = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    price    = models.DecimalField(max_digits=8, decimal_places=2)

class Message(models.Model):
    sender     = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver   = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read    = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} -> {self.receiver}'

class Profile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    phone      = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name  = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Review(models.Model):
    product    = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    rating     = models.IntegerField(default=5)
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f'{self.user} - {self.product} - {self.rating}⭐'