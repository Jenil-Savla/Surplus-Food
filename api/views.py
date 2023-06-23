from rest_framework.generics import GenericAPIView
from rest_framework import status,permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from django.contrib.auth import authenticate

from .serializers import *
from .models import *

class RegisterAPI(GenericAPIView):
	
	serializer_class = RegisterSerializer
	
	def post(self,request,*args,**kwargs):
		data = request.data
		serializer = self.serializer_class(data=data)
		serializer.is_valid(raise_exception = True)
		user = serializer.save()
		token = Token.objects.create(user=user)		
		return Response(serializer.data,status=status.HTTP_201_CREATED)


class LoginAPI(GenericAPIView):
	
	serializer_class = LoginSerializer
	
	def post(self,request,*args,**kwargs ):
		email = request.data.get('email',None)
		password = request.data.get('password',None)
		user = authenticate(email = email, password = password)
		if user :
			token,k = Token.objects.get_or_create(user=user)
			return Response({'token' : token.key,'email' : user.email, 'role':user.type_of_user},status = status.HTTP_200_OK)
		return Response('Invalid Credentials',status = status.HTTP_404_NOT_FOUND)
	
class LogoutAPI(GenericAPIView):
	permission_classes = [permissions.IsAuthenticated]
    
	def post(self,request):
		token = Token.objects.get(user=request.user)
		token.delete()
		return Response('Logged Out',status = status.HTTP_200_OK)
	
class ForgotPasswordAPI(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    
    def post(self,request):
        email = request.data.get('email',None)
        user =  User.objects.filter(email=email)
        if user.exists():
            return Response('Email Sent',status = status.HTTP_200_OK)
        return Response('Invalid Email',status = status.HTTP_404_NOT_FOUND)
    
class NotificationAPI(GenericAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request):
        user = request.user
        notifications = Notification.objects.filter(user=user)
        serializer = self.serializer_class(notifications,many=True)
        return Response(serializer.data,status = status.HTTP_200_OK)
    
    def post(self,request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class FoodAPI(GenericAPIView):
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request):
        user = request.user
        foods = Food.objects.filter(user=user)
        serializer = FoodViewSerializer(foods,many=True)
        return Response(serializer.data,status = status.HTTP_200_OK)
    
    def post(self,request):
        data = request.data
        data['user'] = User.objects.get(email=request.user.email).id
        restaurant_name = data['restaurant_name']
        city = data['city']
        area = data['area']
        phone = data['phone']
        address,k = Address.objects.get_or_create(restaurant_name=restaurant_name,city=city,area=area,phone=phone,user=request.user.id)
        data['restaurant'] = address.id
        category,k = Category.objects.get_or_create(name=data['category'])
        data['category'] = category.id
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class CartAPI(GenericAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request):
        user = request.user
        cart,k = Cart.objects.get_or_create(user=user, is_ordered=False)
        serializer = self.serializer_class(cart)
        cart_items = CartItem.objects.filter(cart=cart)
        serializer2 = CartItemViewSerializer(cart_items,many=True)
        return Response({'cart':serializer.data,'cart_items':serializer2.data},status = status.HTTP_200_OK)
    
    def post(self,request):
        data = request.data
        data['user'] = User.objects.get(email=request.user.email)
        cart,k = Cart.objects.get_or_create(user=request.user, is_ordered=False)
        data['cart'] = cart.id
        serializer = CartItemSerializer(data=data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class CartItemAPI(GenericAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self,request,pk):
        data = request.data
        cart_item = CartItem.objects.get(id=pk)
        food = Food.objects.get(id=cart_item.food.id)
        cart_item.quantity = data['quantity']
        cart_item.save()
        serializer = self.serializer_class(cart_item)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def delete(self,request,pk):
        cart_item = CartItem.objects.get(id=pk)
        cart_item.delete()
        return Response('Item Deleted',status = status.HTTP_200_OK)
    
class OrderAPI(GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request):
        user = request.user
        orders = Order.objects.filter(user=user)
        serializer = self.serializer_class(orders,many=True)
        return Response(serializer.data,status = status.HTTP_200_OK)
    
    def post(self,request):
        data = request.data
        cart = Cart.objects.get(user=request.user, is_ordered=False)
        data['cart'] = cart.id
        data['user'] = User.objects.get(email=request.user.email).id
        cart_items = CartItem.objects.filter(cart=cart)
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception = True):
            serializer.save()
            print(cart_items)
            for cart_item in cart_items:
                food = Food.objects.get(id=cart_item.food.id)
                if food.quantity - cart_item.quantity < 0:
                    continue
                elif food.quantity - cart_item.quantity == 0:
                    food.is_available = False
                food.quantity = food.quantity - cart_item.quantity
                food.save()
                order = Order.objects.get(id=serializer.data['id'])
                order_item = OrderItem.objects.create(order=order,food=cart_item.food,quantity=cart_item.quantity)
                order_item.save()
            cart.is_ordered = True
            cart.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class OrderDetailAPI(GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request,pk):
        order = Order.objects.get(id=pk)
        serializer = self.serializer_class(order)
        orderitems = OrderItem.objects.filter(order=order)
        serializer2 = OrderItemSerializer(orderitems,many=True)
        return Response({'order':serializer.data,'order_items':serializer2.data},status = status.HTTP_200_OK)
    
class SearchAndFilterAPI(GenericAPIView):
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request):
        name = request.GET.get('name',None)
        category = request.GET.get('category',None)
        location = request.GET.get('location',None)
        price_low = int(request.GET.get('price_low',0))
        price_high = int(request.GET.get('price_high',100000))
        foods = Food.objects.filter(name__icontains=name,category__name__icontains=category, price__gte=price_low, price__lte=price_high)
        if location:
            address = Address.objects.filter(city__icontains=location)
            foods = Food.objects.filter(name__icontains=name,category__name__icontains=category, price__gte=price_low, price__lte=price_high)
        serializer = self.serializer_class(foods,many=True)
        return Response(serializer.data,status = status.HTTP_200_OK)