from django.test import TestCase
from django.urls import reverse
from shopapp.models import Product, Registration


class SitePagesTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Classic Tee', price=499, image='Product/demo.jpg')

    def test_homepage_loads(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_complete_page_loads(self):
        response = self.client.get(reverse('password_reset_complete'))
        self.assertEqual(response.status_code, 200)

    def test_admin_redirects_to_login(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_register_creates_auth_user_and_registration_record(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Registration.objects.filter(email='newuser@example.com').exists())

    def test_product_detail_page_loads(self):
        response = self.client.get(reverse('product_detail', args=[self.product.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Classic Tee')

    def test_add_to_cart_updates_session(self):
        response = self.client.post(reverse('add_to_cart'), {'product_id': self.product.pk, 'quantity': 2}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('cart', self.client.session)
        self.assertEqual(self.client.session['cart'][str(self.product.pk)]['quantity'], 2)
