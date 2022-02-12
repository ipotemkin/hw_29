from typing import Optional
from pydantic import BaseModel, Field
import json

from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .models import Ad, Cat


# shortcuts
ADO = Ad.objects
CATO = Cat.objects


class AdModel(BaseModel):
    pk: Optional[int] = Field(alias="id")
    name: str
    author: str
    price: int
    description: str
    address: str
    is_published: bool

    class Config:
        orm_mode = True


class AdsModel(BaseModel):
    item: list[AdModel]

    class Config:
        orm_mode = True


class CatModel(BaseModel):
    pk: Optional[int] = Field(alias="id")
    name: str

    class Config:
        orm_mode = True


def index(request):
    return JsonResponse({"status": "ok"})


@method_decorator(csrf_exempt, name='dispatch')
class AdView(View):
    @staticmethod
    def get(request):
        return JsonResponse(
            [AdModel.from_orm(ad).dict() for ad in ADO.all()],
            safe=False,
            json_dumps_params={"ensure_ascii": False, "indent": 2}  # чтобы вывести кириллицу в браузере + отступы
        )

    @staticmethod
    def post(request):
        ad = ADO.create(**AdModel.parse_raw(request.body).dict())
        return JsonResponse(AdModel.from_orm(ad).dict())


class AdDetailView(DetailView):
    model = Ad

    def get(self, request, *args, **kwargs):
        ad = self.get_object()
        return JsonResponse(AdModel.from_orm(ad).dict(), json_dumps_params={"ensure_ascii": False, "indent": 2})


@method_decorator(csrf_exempt, name='dispatch')
class AdHTTPJsonView(View):
    @staticmethod
    def get(request):
        if name := request.GET.get("name", None):
            res_obj = ADO.filter(name=name)
        else:
            res_obj = ADO.all()

        s_dicts = [AdModel.from_orm(ad).dict(include={"pk", "name", "price"}) for ad in res_obj]
        # s_dicts = [{"item": AdModel.from_orm(ad)} for ad in res_obj]
        # s_dicts = AdsModel.from_orm(s_dicts)
        s = json.dumps(s_dicts, ensure_ascii=False, indent=2)

        return HttpResponse(s, content_type='text/plain; charset=utf-8')


@method_decorator(csrf_exempt, name='dispatch')
class AdHTTPView(View):
    @staticmethod
    def get(request):
        res_obj = ADO.filter(name=name) if (name := request.GET.get("name", None)) else ADO.all()
        return render(request, 'ads_list.html', {"ads": res_obj})


class AdHTTPJsonDetailView(DetailView):
    model = Ad

    def get(self, request, *args, **kwargs):
        s = AdModel.from_orm(self.get_object()).json(ensure_ascii=False, indent='\t')
        return HttpResponse(s, content_type='text/plain; charset=utf-8')


@method_decorator(csrf_exempt, name='dispatch')
class CatView(View):
    @staticmethod
    def get(request):
        return JsonResponse(
            [CatModel.from_orm(cat).dict() for cat in CATO.all()],
            safe=False
        )

    @staticmethod
    def post(request):
        cat = CATO.create(**CatModel.parse_raw(request.body).dict())
        return JsonResponse(CatModel.from_orm(cat).dict())


class CatDetailView(DetailView):
    model = Cat

    def get(self, request, *args, **kwargs):
        cat = self.get_object()
        return JsonResponse(CatModel.from_orm(cat).dict())
