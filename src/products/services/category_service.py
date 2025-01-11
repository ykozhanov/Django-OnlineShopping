from typing import List

from products.models import Category


class CategoryService:
    categories = None

    @classmethod
    def get_active_categories(cls):
        if cls.categories is None:
            cls.categories = Category.objects.filter(is_active=True).select_related("parent")
        return cls.categories

    @classmethod
    def get_childrens_by_parent(cls, parent: Category) -> List[Category]:
        """Возвращает список из родительской категории и её наследников"""
        return [category for category in cls.categories if category.parent == parent or category == parent]
