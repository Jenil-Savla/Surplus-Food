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
        #foodimages = FoodImage.objects.filter(food__id__in = foods)
        serializer = FoodViewSerializer(foods,many=True)
        return Response(serializer.data,status = status.HTTP_200_OK)

    def post(self,request):
        data = request.data
        setattr(data, '_mutable', True)
        data['user'] = User.objects.get(email=request.user.email).id
        restaurant_name = data['restaurant_name']
        city = data['city']
        area = data['area']
        phone = data['phone']
        address,k = Address.objects.get_or_create(restaurant_name=restaurant_name,city=city,area=area,phone=phone,user=request.user)
        data['restaurant'] = address.id
        category,k = Category.objects.get_or_create(name=data['category'])
        data['category'] = category.id
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        #food_image = data['food_image']
        fd = Food.objects.get(id = serializer.data['id'])
        #foodimg = FoodImage.objects.create(food=fd, image = food_image)
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
    serializer_class = FoodViewSerializer
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
            foods = Food.objects.filter(name__icontains=name,category__name__icontains=category, price__gte=price_low, price__lte=price_high, restaurant__in=address)
        serializer = self.serializer_class(foods,many=True)
        return Response(serializer.data,status = status.HTTP_200_OK)
    
class ProviderOrderAPI(GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):
        user = request.user
        orders = Order.objects.filter(orderitem__food__user=user)
        serializer = self.serializer_class(orders,many=True)
        orderitems = OrderItem.objects.filter(order__in=orders)
        serializer2 = OrderItemSerializer(orderitems,many=True)
        return Response({'order':serializer.data,'order_items':serializer2.data},status = status.HTTP_200_OK)
    
from django.db.models import Count
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from rest_framework.decorators import api_view
from rest_framework.response import Response
from surprise import Dataset
from surprise import SVD
from surprise import Reader
from surprise.model_selection import train_test_split
import pandas as pd


@api_view(['GET'])
def get_food_recommendations(request):
    # Get the current time of day
        current_time = datetime.now().time()
        
        # Get the current month
        current_month = datetime.now().month
        
        # Get the foods ordered in the last 30 days
        last_30_days = datetime.now() - timedelta(days=30)
        ordered_foods = OrderItem.objects.filter(order__created_at__gte=last_30_days).values('food').annotate(order_count=Count('food'))
        
        # Get the most popular foods based on order count
        popular_foods = ordered_foods.order_by('-order_count')[:10]
        popular_food_ids = [food['food'] for food in popular_foods]
        
        # Get the food descriptions for TF-IDF vectorization
        food_descriptions = Food.objects.filter(id__in=popular_food_ids).values_list('id', 'description')
        
        # Create a TF-IDF matrix for food descriptions
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform([desc for _, desc in food_descriptions])
        
        # Compute cosine similarity between food descriptions
        cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
        
        # Get the indices of the top recommendations based on cosine similarity
        recommendation_indices = cosine_similarities[0].argsort()[:-5:-1]
        recommended_foods = [food_descriptions[idx][0] for idx in recommendation_indices.tolist()]

        #Advnaced ML
        # Create a DataFrame for user-item interactions
        data = pd.DataFrame(list(OrderItem.objects.all().values('order__user', 'food', 'quantity')))
        reader = Reader(rating_scale=(0, 5))  # Define the rating scale

        # Load the data into the Surprise Dataset format
        dataset = Dataset.load_from_df(data, reader)

        # Split the data into training and testing sets
        trainset, testset = train_test_split(dataset, test_size=0.2)
        # Initialize the SVD algorithm
        algo = SVD()

        # Train the model on the training set
        algo.fit(trainset)

        # Get the current user
        current_user_id = request.user.id

        # Generate predictions for the test set
        predictions = algo.test(testset)

        # Filter predictions for the current user
        user_predictions = [pred for pred in predictions if pred.uid == current_user_id]

        # Sort the predictions by estimated rating (descending order)
        user_predictions.sort(key=lambda x: x.est, reverse=True)

        # Get the top-N recommendations for the current user
        top_n = 5

        # Get the recommended food IDs
        recommended_food_ids = [int(prediction.iid) for prediction in user_predictions[:top_n]]

        recommended_foods.extend(recommended_food_ids)
        
        # Get the recommended food objects
        recommendations = Food.objects.filter(id__in=recommended_foods)
        
        # Serialize the recommended food objects
        #serialized_recommendations = [{'id': food.id, 'name': food.name, 'description': food.description} for food in recommendations]
        serialized_recommendations = FoodViewSerializer(recommendations, many=True)
        
        return Response(serialized_recommendations.data, status=status.HTTP_200_OK)