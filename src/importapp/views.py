import json
from io import TextIOWrapper

from django.views import View
from django.shortcuts import render
from django.core.management import call_command
from django.http import HttpResponse, HttpRequest

from .forms import JSONImportForm


class ImportProductsJSONView(View):
    form = JSONImportForm()
    context = {
        "form": form,
    }

    def get(self, request: HttpRequest):
        return render(request, "importapp/import-products.html", context=self.context)

    def post(self, request: HttpRequest):
        form = JSONImportForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, "importapp/import-products.html", context=self.context, status=400)
        json_file = TextIOWrapper(
            form.files["json_file"].file,
            encoding=request.encoding,
        )
        data = json.load(json_file)
        call_command("start_import", data=data, email=form.email)
        return HttpResponse("Импорт начался")

# def import_products_json_view(request: HttpRequest) -> HttpResponse:
#     form = JSONImportForm()
#     context = {
#         "form": form,
#     }
#
#     if request.method == "POST":
#         form = JSONImportForm(request.POST, request.FILES)
#         if not form.is_valid():
#             return render(request, "importapp/import-products.html", context=context, status=400)
#         json_file = TextIOWrapper(
#             form.files["json_file"].file,
#             encoding=request.encoding,
#         )
#         data = json.load(json_file)
#         call_command("start_import", data=data, email=form.email)
#         return HttpResponse("Импорт начался")
#     return render(request, "importapp/import-products.html", context=context)
#

