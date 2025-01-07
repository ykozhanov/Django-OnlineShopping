from typing import List

from products.models import Category


def get_category_service():
    return CategoryService()


class CategoryService:
    def __init__(self):
        self.categories = None

    def get_active_categories(self):
        if self.categories is None:
            self.categories = Category.objects.filter(is_active=True).select_related("parent")
        return self.categories

    def get_childrens_by_parent(self, parent: Category) -> List[Category]:
        """Возвращает список из родительской категории и её наследников"""
        return [category for category in self.categories if category.parent == parent or category == parent]
