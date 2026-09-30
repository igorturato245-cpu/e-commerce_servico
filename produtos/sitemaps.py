from django.contrib.sitemaps import Sitemap
from produtos.models import Product

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(disponivel=True).select_related('category')

    def lastmod(self, obj):
        return obj.atulizado 

    def location(self, obj):
        from django.urls import reverse
        return reverse('produtos:detalhe_produto', args=[obj.category.slug, obj.slug])