from django.test import TestCase
from django.urls import reverse

from produtos.models import Category, Product


class ProductsViewTest(TestCase):
    def test_products_page_renders_for_category(self):
        categoria = Category.objects.create(name='Panelas', slug='panelas')
        produto = Product.objects.create(
            category=categoria,
            name='Panela de aço',
            slug='panela-de-aco',
            preco=100.00,
            preco_promocional=90.00,
            estoque=10,
        )

        response = self.client.get(reverse('produtos:produto', kwargs={'categoria_slug': categoria.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, produto.name)
