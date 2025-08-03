
from django.db import models
from django.conf import settings
from django.utils import timezone as tz
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal

class Category(models.Model):
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class product_manager(models.Manager):
    def get_queryset(self):
        return super(product_manager, self).get_queryset().filter(status=True)


class products(models.Model):
    athour = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ManyToManyField(Category, related_name="products_by_cat")
    badge = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    review = models.TextField(blank=True, null=True)
    boldtext = models.TextField(blank=True, null=True)
    cost  = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='images/articles', blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    stock = models.PositiveIntegerField(default=0) 

    def get_absulute_url(self):
        return reverse('blog:product_details', kwargs={'slug': self.slug})

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.slug = slugify(self.name)
        super(products, self).save()

    def __str__(self):
        return f"{self.name}-{self.body[0:50]}"

    class Meta:
        ordering = ('-updated',)


class headtitle(models.Model):
    title = models.CharField(max_length=50, null=True)
    head_sequence = models.CharField(max_length=50, null=True)
    body = models.TextField(null=True)
    category = models.ManyToManyField(Category)
    badge = models.CharField(max_length=50, blank=True, null=True)
    boldtext = models.TextField(blank=True, null=True)
    cost = models.IntegerField(blank=True, null=True)
    discount = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='images/headtitle', null=True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    review = models.TextField(blank=True, null=True)

    def get_absulute_url(self):
        return reverse('blog:head_details', args=[self.slug])

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.slug = slugify(self.title)
        super(headtitle, self).save()

    def __str__(self):
        return f"{self.title}-{self.body[:20]}"

    class Meta:
        ordering = ('-updated',)



class Comment(models.Model):
    product = models.ForeignKey("Blog_app.products",on_delete=models.CASCADE,related_name='comments')
    athour = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE , null=True ,blank=True , related_name='replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[:100]


class Message(models.Model):
    title = models.CharField(max_length=70)
    name = models.CharField(max_length=70)
    e_mail = models.EmailField()
    phone = models.CharField(max_length=11)
    text = models.TextField()
    message_recive_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title





class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    def total_price(self):
        return int(self.quantity *( self.product.cost or 0))
    def calculate_discount(self):
        discount_difference = (self.product.discount or 0) - (self.product.cost or 0)
        if self.total_price() >= 5000000:
            return int(Decimal('0.10') * self.total_price() + discount_difference)
        return int(discount_difference)
    def Calculate_discount2(self):
        if self.total_price() >= 5000000:
            return int(Decimal('0.10') * self.total_price())
        return 0
    def final_price(self):
        carry = Decimal(500000)
        discount = self.Calculate_discount2()
        return int( self.total_price() - discount + carry)

# Create your models here.

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Rejected', 'Rejected'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    final_total = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(products, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return f"{self.quantity} of {self.product} at {self.price}"


   

  


