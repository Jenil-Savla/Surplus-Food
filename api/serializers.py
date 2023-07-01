from rest_framework import serializers
from .models import Notification, User, Food, Order, OrderItem, Address, Payment, Review, Cart, CartItem, Category, FoodImage

import re
email_pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(max_length=32,min_length=8,write_only = True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'phone', 'type_of_user']

    def validate(self,attrs):
        email = attrs.get('email',' ')

        if not email_pattern.match(email):
            raise serializers.ValidationError('Please enter a valid email!')
        return attrs

    def create(self,validated_data):
            validated_data['is_active'] = True
            return User.objects.create_user(**validated_data)

class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class FoodImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodImage
        fields = '__all__'

class FoodViewSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    user = RegisterSerializer(read_only=True)
    #food_image = FoodImageSerializer(many=True, required=False)
    restaurant = AddressSerializer(read_only=True)
    food_image = serializers.SerializerMethodField()

    def get_food_image(self, obj):
         #data = {...} # your logic
         food_images = FoodImage.objects.filter(food=obj)
         if food_images:
            field_serializer = FoodImageSerializer(food_images.first())
            return field_serializer.data

    class Meta:
        model = Food
        fields = ['id', 'name', 'age', 'description', 'price', 'category', 'user', 'quantity', 'is_available','is_verified', 'restaurant','food_image']

class FoodSerializer(serializers.ModelSerializer):
    #category = CategorySerializer(read_only=True)
    #user = RegisterSerializer(read_only=True)
    #food_image = FoodImageSerializer(many=True, required=False)
    #food_image = serializers.FileField()
    #restaurant = AddressSerializer(read_only=True)
    class Meta:
        model = Food
        fields = ['id', 'name', 'age', 'description', 'price', 'category', 'user', 'quantity', 'is_available','is_verified', 'restaurant']

    def create(self, validated_data):
    #     category_data = validated_data.pop('category')
    #     #user_data = validated_data.pop('user')
        #food_image_data = validated_data.pop('food_image', None)
    #     #restaurant_data = validated_data.pop('restaurant')
    #     category,k = Category.objects.get_or_create(**category_data)
    #     #user = User.objects.get_or_create(**user_data)
    #     #restaurant = Address.objects.get_or_create(**restaurant_data)
        food = Food.objects.create(**validated_data)
        #if food_image_data:
            #if len(food_image_data) == 1:
                #FoodImage.objects.create(food=food, image=food_image_data)
            #else:
                #for image in food_image_data:
                    #FoodImage.objects.create(food=food, image=image)
        return food

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    food = FoodSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

class CartItemViewSerializer(serializers.ModelSerializer):
    food = FoodViewSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'