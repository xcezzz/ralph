# -*- coding: utf-8 -*-
from datetime import date
from decimal import Decimal
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.http import QueryDict
from rest_framework import relations
from rest_framework.test import APIClient, APIRequestFactory

from ralph.api.serializers import ReversedChoiceField
from ralph.api.tests.api import (
    Bar,
    BarViewSet,
    Car,
    CarSerializer,
    CarViewSet,
    ManufacturerSerializer2,
    ManufacturerViewSet
)
from ralph.api.viewsets import RalphAPIViewSet
from ralph.tests import RalphTestCase
from ralph.tests.factories import ManufacturerFactory


class ViewsetWithoutRalphPermission(RalphAPIViewSet):
    permission_classes = []


class ViewsetWithoutPermissionsForObjectFilter(RalphAPIViewSet):
    filter_backends = []


class TestRalphViewset(RalphTestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = APIRequestFactory()
        self.manufacture_1 = ManufacturerFactory(
            name='test', country='Poland'
        )
        self.manufacture_2 = ManufacturerFactory(
            name='test2', country='test'
        )
        get_user_model().objects.create_superuser(
            'test', 'test@test.test', 'test'
        )
        self.client = APIClient()
        self.client.login(username='test', password='test')

        Bar.objects.create(
            name='Bar11',
            date=date(2015, 3, 1),
            price=Decimal('21.4'),
            count=1
        )
        Bar.objects.create(
            name='Bar22',
            date=date(2014, 4, 1),
            price=Decimal('11.4'),
            count=2
        )
        Bar.objects.create(
            name='Bar33',
            date=date(2013, 5, 1),
            price=Decimal('31.4'),
            count=3
        )

    def test_should_raise_attributeerror_when_ralph_permission_missing(self):
        with self.assertRaises(AttributeError):
            ViewsetWithoutRalphPermission()

    def test_should_raise_attributeerror_when_permission_for_object_filter_missing(self):  # noqa
        with self.assertRaises(AttributeError):
            ViewsetWithoutPermissionsForObjectFilter()

    def test_get_serializer_class_should_return_base_when_safe_request(self):
        request = self.request_factory.get('/')
        cvs = CarViewSet()
        cvs.request = request
        self.assertEqual(cvs.get_serializer_class(), CarSerializer)

    def test_get_serializer_class_should_return_dynamic_when_not_safe_request(self):  # noqa
        request = self.request_factory.post('/')
        cvs = CarViewSet()
        cvs.request = request
        serializer_class = cvs.get_serializer_class()
        self.assertEqual(serializer_class.__name__, 'CarSaveSerializer')
        self.assertEqual(serializer_class.Meta.model, Car)
        self.assertEqual(serializer_class.Meta.depth, 0)
        self.assertEqual(
            serializer_class.serializer_choice_field, ReversedChoiceField
        )
        self.assertEqual(
            serializer_class.serializer_related_field,
            relations.PrimaryKeyRelatedField
        )

    def test_get_serializer_class_should_return_defined_when_not_safe_request_and_save_serializer_class_defined(self):  # noqa
        request = self.request_factory.patch('/')
        mvs = ManufacturerViewSet()
        mvs.request = request
        self.assertEqual(mvs.get_serializer_class(), ManufacturerSerializer2)

    def test_extend_filter_fields(self):
        request = self.request_factory.get('/')
        request.query_params = QueryDict(urlencode({'name': 'test'}))
        mvs = ManufacturerViewSet()
        mvs.request = request
        self.assertEqual(len(mvs.get_queryset()), 2)

        request.query_params = QueryDict(urlencode({'name': 'test2'}))
        mvs.request = request
        self.assertEqual(len(mvs.get_queryset()), 1)

    def test_query_filters_charfield(self):
        request = self.request_factory.get('/api/bar')
        bvs = BarViewSet()
        request.query_params = QueryDict(
            urlencode({'name__icontains': 'bar1'})
        )
        bvs.request = request
        self.assertEqual(len(bvs.get_queryset()), 1)

        # Failed filter
        request.query_params = QueryDict(urlencode({'name__range': 10}))
        self.assertEqual(len(bvs.get_queryset()), 3)

    def test_query_filters_decimalfield(self):
        request = self.request_factory.get('/api/bar')
        bvs = BarViewSet()
        request.query_params = QueryDict(urlencode({'price__gte': 20}))
        bvs.request = request
        self.assertEqual(len(bvs.get_queryset()), 2)

        # Failed filter
        request.query_params = QueryDict(urlencode({'price__istartswith': 10}))
        self.assertEqual(len(bvs.get_queryset()), 3)

    def test_query_filters_integerfield(self):
        request = self.request_factory.get('/api/bar')
        bvs = BarViewSet()
        request.query_params = QueryDict(urlencode({'count__gte': 2}))
        bvs.request = request
        self.assertEqual(len(bvs.get_queryset()), 2)

        # Failed filter
        request.query_params = QueryDict(urlencode({'count__istartswith': 10}))
        self.assertEqual(len(bvs.get_queryset()), 3)

    def test_query_filters_datefield(self):
        request = self.request_factory.get('/api/bar')
        bvs = BarViewSet()
        request.query_params = QueryDict(urlencode({'date__year': 2015}))
        bvs.request = request
        self.assertEqual(len(bvs.get_queryset()), 1)

        # Failed filter
        request.query_params = QueryDict(urlencode({'date__istartswith': 10}))
        self.assertEqual(len(bvs.get_queryset()), 3)

    def test_query_filters_datetimefield(self):
        request = self.request_factory.get('/api/bar')
        bvs = BarViewSet()
        request.query_params = QueryDict(urlencode(
            {'created__year': date.today().year})
        )
        bvs.request = request
        self.assertEqual(len(bvs.get_queryset()), 3)

        request.query_params = QueryDict(
            urlencode({
                'date__year': 2014,
                'created__month': date.today().month
            })
        )
        bvs.request = request
        self.assertEqual(len(bvs.get_queryset()), 1)

        # Failed filter
        request.query_params = QueryDict(
            urlencode({'created__istartswith': 10})
        )
        self.assertEqual(len(bvs.get_queryset()), 3)

    def test_options_filtering(self):
        response = self.client.options('/api/manufacturers/')
        self.assertListEqual(response.data['filtering'], ['name'])


class TestAdminSearchFieldsMixin(RalphTestCase):
    def test_get_filter_fields_from_admin(self):
        cvs = CarViewSet()
        self.assertEqual(
            cvs.filter_fields,
            ['manufacturer__name', 'name', 'foos__bar', 'year']
        )
