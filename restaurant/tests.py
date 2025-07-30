from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal
from datetime import date, datetime
from .models import Menu, Booking
import json

class MenuModelTest(TestCase):
    """测试Menu模型"""
    
    def setUp(self):
        self.menu_item = Menu.objects.create(
            title="Test Pizza",
            price=Decimal('15.99'),
            inventory=10
        )
    
    def test_menu_creation(self):
        """测试菜单项目创建"""
        self.assertEqual(self.menu_item.title, "Test Pizza")
        self.assertEqual(self.menu_item.price, Decimal('15.99'))
        self.assertEqual(self.menu_item.inventory, 10)
    
    def test_menu_str_method(self):
        """测试菜单项目字符串表示"""
        expected_str = f"{self.menu_item.title} : {str(self.menu_item.price)}"
        self.assertEqual(str(self.menu_item), expected_str)

class BookingModelTest(TestCase):
    """测试Booking模型"""
    
    def setUp(self):
        self.booking = Booking.objects.create(
            name="John Doe",
            no_of_guests=4,
            booking_date=date.today()
        )
    
    def test_booking_creation(self):
        """测试预订创建"""
        self.assertEqual(self.booking.name, "John Doe")
        self.assertEqual(self.booking.no_of_guests, 4)
        self.assertEqual(self.booking.booking_date, date.today())
    
    def test_booking_fields(self):
        """测试预订字段"""
        self.assertIsInstance(self.booking.name, str)
        self.assertIsInstance(self.booking.no_of_guests, int)
        self.assertIsInstance(self.booking.booking_date, date)

class MenuAPITest(TestCase):
    """测试Menu API端点"""
    
    def setUp(self):
        self.client = APIClient()
        self.menu_item = Menu.objects.create(
            title="Test Pasta",
            price=Decimal('12.99'),
            inventory=20
        )
        self.menu_data = {
            'title': 'New Dish',
            'price': '18.50',
            'inventory': 15
        }
    
    def test_get_menu_items(self):
        """测试获取所有菜单项目"""
        response = self.client.get('/restaurant/menu-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Pasta')
    
    def test_create_menu_item(self):
        """测试创建菜单项目"""
        response = self.client.post('/restaurant/menu-items/', self.menu_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Menu.objects.count(), 2)
        self.assertEqual(Menu.objects.latest('id').title, 'New Dish')
    
    def test_get_single_menu_item(self):
        """测试获取单个菜单项目"""
        response = self.client.get(f'/restaurant/menu-items/{self.menu_item.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Pasta')
    
    def test_update_menu_item(self):
        """测试更新菜单项目"""
        update_data = {
            'title': 'Updated Pasta',
            'price': '15.99',
            'inventory': 25
        }
        response = self.client.put(f'/restaurant/menu-items/{self.menu_item.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.menu_item.refresh_from_db()
        self.assertEqual(self.menu_item.title, 'Updated Pasta')
    
    def test_delete_menu_item(self):
        """测试删除菜单项目"""
        response = self.client.delete(f'/restaurant/menu-items/{self.menu_item.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Menu.objects.count(), 0)

class BookingAPITest(TestCase):
    """测试Booking API端点"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.booking_data = {
            'name': 'Jane Smith',
            'no_of_guests': 2,
            'booking_date': date.today().strftime('%Y-%m-%d')
        }
    
    def test_create_booking_authenticated(self):
        """测试认证用户创建预订"""
        response = self.client.post('/restaurant/booking/tables/', self.booking_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(Booking.objects.latest('id').name, 'Jane Smith')
    
    def test_create_booking_unauthenticated(self):
        """测试未认证用户创建预订（应该失败）"""
        self.client.credentials()  # 移除认证
        response = self.client.post('/restaurant/booking/tables/', self.booking_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_bookings_authenticated(self):
        """测试认证用户获取预订列表"""
        Booking.objects.create(
            name='Test Booking',
            no_of_guests=4,
            booking_date=date.today()
        )
        response = self.client.get('/restaurant/booking/tables/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_bookings_unauthenticated(self):
        """测试未认证用户获取预订列表（应该失败）"""
        self.client.credentials()  # 移除认证
        response = self.client.get('/restaurant/booking/tables/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ViewsTest(TestCase):
    """测试视图功能"""
    
    def setUp(self):
        self.client = Client()
        self.menu_item = Menu.objects.create(
            title="Test Dish",
            price=Decimal('18.50'),
            inventory=15
        )
        self.booking = Booking.objects.create(
            name="Test Customer",
            no_of_guests=3,
            booking_date=date.today()
        )
    
    def test_index_view(self):
        """测试首页"""
        response = self.client.get('/restaurant/')
        self.assertEqual(response.status_code, 200)
    
    def test_menu_view(self):
        """测试菜单页面"""
        response = self.client.get('/restaurant/menu/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dish')
    
    def test_about_view(self):
        """测试关于页面"""
        response = self.client.get('/restaurant/about/')
        self.assertEqual(response.status_code, 200)
    
    def test_book_view_get(self):
        """测试预订页面GET请求"""
        response = self.client.get('/restaurant/book/')
        self.assertEqual(response.status_code, 200)
    
    def test_book_view_post(self):
        """测试预订页面POST请求"""
        booking_data = {
            'name': 'New Customer',
            'no_of_guests': 2,
            'booking_date': date.today().strftime('%Y-%m-%d')
        }
        response = self.client.post('/restaurant/book/', booking_data)
        self.assertEqual(response.status_code, 200)
        # 验证预订是否创建成功
        self.assertTrue(Booking.objects.filter(name='New Customer').exists())
    
    def test_reservations_view(self):
        """测试预订查看页面"""
        response = self.client.get('/restaurant/reservations/')
        self.assertEqual(response.status_code, 200)

class AuthenticationTest(TestCase):
    """测试认证功能"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_token_creation(self):
        """测试令牌创建"""
        response = self.client.post('/restaurant/api-token-auth/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_invalid_login(self):
        """测试无效登录"""
        response = self.client.post('/restaurant/api-token-auth/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class BookingJSONAPITest(TestCase):
    """测试JSON格式的预订API"""
    
    def setUp(self):
        self.client = Client()
        self.booking = Booking.objects.create(
            name="JSON Test",
            no_of_guests=2,
            booking_date=date.today()
        )
    
    def test_get_bookings_json(self):
        """测试获取JSON格式的预订数据"""
        response = self.client.get('/restaurant/bookings')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_create_booking_json(self):
        """测试通过JSON创建预订"""
        booking_data = {
            'name': 'JSON Customer',
            'no_of_guests': 4,
            'booking_date': date.today().strftime('%Y-%m-%d')
        }
        response = self.client.post('/restaurant/bookings', 
                                   json.dumps(booking_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Booking.objects.filter(name='JSON Customer').exists())