from django import template
register = template.Library()

@register.filter
def total_stock_kg(queryset):
    return sum(item.quantite_actuelle for item in queryset if item.unite == 'kg')