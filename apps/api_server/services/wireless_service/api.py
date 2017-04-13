from decimal import Decimal
# from flask import json, request
from flask import session, request
from flask_security import auth_token_required, roles_required
from flask_restful import fields, Resource, marshal_with, reqparse

from apps.api_server import api
from .models import WirelessSimOrder, WirelessSimActivateModel


class NestedArgument(reqparse.Argument):
    def __init__(self, name, **kwargs):
        pieces = name.split('.')

        self.full_name = name

        if len(pieces) > 1:
            name = pieces.pop()

        super(NestedArgument, self).__init__(name, **kwargs)

    def source(self, request):
        pieces = self.full_name.split('.')
        source = super(NestedArgument, self).source(request)

        if len(pieces) == 1:
            return source

        for piece in pieces[:-1]:
            source = source.get(piece, None)
            if source is None:
                self.handle_validation_error(ValueError(
                        u"{0} is required in {1}".format(
                                self.full_name,
                                self.location
                        )))

        return source


class NestedRequestParser(reqparse.RequestParser):
    def __init__(self):
        super(NestedRequestParser, self).__init__(argument_class=NestedArgument)

    def parse_args(self, req=None):
        if req is None:
            req = request

        namespace = self.namespace_class()

        for arg in self.args:
            pieces = arg.full_name.split('.')
            current = namespace

            # setup namespace for nested arguments
            # given a `full_name` of `a.b.c`, we create namespace { 'a': { 'b': {} } }
            if len(pieces) > 1:
                for i in range(0, len(pieces) - 1):
                    if current.get(pieces[i]) is None:
                        current[pieces[i]] = {}
                    current = current[pieces[i]]

            current[arg.dest or arg.name] = arg.parse(req)

        return namespace


class WirelessSimPlan(Resource):
    """
    [요금제 API]
    요금제 이름:         요금제 이름
    요금제 종류:         월별 요금제(정액 요금제-flat) / 기본 요금제(non-flat)
    요금제 활성화:        True/False(요금제 이용 가능 여부) - display 여부
    요금제 가격: 요금제 최소 충전 가격
    요금제 currency: 요금제 최소 충전 currncy
    요금제 terms: 요금제 수수료 차감 조건
    요금제 info: 요금제 내부에 plan을 나타냄

    data:
    {
    'name': "요금제 이름",
    'classify': '요금제 종류' (flat , non-flat),
    'is_active': '요금제 이용 가능 여부' (default: False),
    'price': '요금제 최소 충전 가격',
    "currency": "통화",
    'terms': {
                'classify': (기간인지, 금액인지) 'period','price', (classify에 따라 content 및 unit이 변경)
                'content': 내용
                'unit': 기간이면 월/ 가격이면 currency
             }
    'info':[
            {
                'title': 'internet',
                'description': 설명,

                <'차감량'>: (기본 요금제 일때) - root의 classify에 따라 변환
                'price': 가격(Decimal),
                'currency': 통화(환전),
                'measure': 산정량( eg. 1MB),

                <'허용량'>: (정액 요금제일 때) - root의 classify에 따라 변환
                'unit': 단위,
                'content': 내용
            },
            {
                'title': 'voice',
                'description': 설명,

                <'차감량'>: (기본 요금제 일때)
                'price': 가격,
                'currency: 통화,
                'measure': 산정량,

                <'허용량'>: (정액 요금제일 때)
                'unit': 단위,
                'content': 내용
            },
                ...
            ]
        }
    }
    """
    root_parser = reqparse.RequestParser()
    root_parser.add_argument('name', required=True, trim=True, help='Name must be set.')
    root_parser.add_argument('classify', required=True, help='classify must be set. choices(flat, non-flat)',
                             choices=('flat', 'non-flat'), trim=True)
    root_parser.add_argument('is_active', default=False, type=bool, trim=True)
    root_parser.add_argument('price', required=True, type=Decimal, trim=True, help='price must be set.')
    root_parser.add_argument('currency', required=True, trim=True, help='currency must be set.')
    root_parser.add_argument('terms', type=dict, required=True, trim=True, help='terms must be set.')
    root_parser.add_argument('info', action='append', type=dict, trim=True, help='info must be set.')
    # root_parser.add_argument('info', required=True, action='append',  trim=True, help='info must be settled.')

    # terms Parser
    terms_parser = reqparse.RequestParser()
    terms_parser.add_argument('classify', required=True, choices=('period', 'price'), trim=True,
                              location='terms', help='terms\'s classify must be set.')
    terms_parser.add_argument('content', required=True, location='terms')
    terms_parser.add_argument('unit', required=True, location='terms')

    # info Parser
    info_parser = reqparse.RequestParser()
    info_parser.add_argument('title', location='info', help='bbbb')
    info_parser.add_argument('description', location='info')
    info_parser.add_argument('measure', help='aaaa', location='info')
    info_parser.add_argument('price', location='info')
    info_parser.add_argument('currency', location='info')
    info_parser.add_argument('content', location='info')

    # @auth_token_required
    # @roles_required('superuser')
    def post(self):
        """
        요금제 추가
        """
        session['aa'] = 10

        root_args = self.root_parser.parse_args(strict=True)

        terms_args = self.terms_parser.parse_args(req=root_args)
        # print(root_args)
        # print(terms_args)

        info_args = self.info_parser.parse_args(req=root_args)

        print(info_args)

        pass

    def get(self):
        return 'hi'


api.add_resource(WirelessSimPlan, '/wireless')


class WirelessSimOrderAPI(Resource):
    @auth_token_required
    def post(self):
        pass


class WirelessSimPaymentAPI(Resource):
    @auth_token_required
    def post(self):
        pass


class WirelessSimTopupAPI(Resource):
    @auth_token_required
    def post(self):
        pass


api.add_resource(WirelessSimOrderAPI, '/wireless/sim')
api.add_resource(WirelessSimTopupAPI, '/wireless/topup')
