# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import RequestFactory

from ralph.lib.transitions import transition_action
from ralph.lib.transitions.exceptions import (
    TransitionModelNotFoundError,
    TransitionNotAllowedError
)
from ralph.lib.transitions.models import (
    _check_and_get_transition,
    _create_graph_from_actions,
    _sort_graph_topologically,
    Action,
    CycleError,
    run_field_transition,
    Transition
)
from ralph.lib.transitions.tests import TransitionTestCase
from ralph.tests.models import Foo, Order, OrderStatus


@transition_action()
def mocked_action(*args, **kwargs):
    """
    Mark action as runned.
    """
    mocked_action.runned = True
    return None


class PermissionsTest(TransitionTestCase):
    def test_create_transition_should_create_perm(self):
        name = 'Foo'
        _, transition, _ = self._create_transition(Order, name)
        perm_exist = Permission.objects.filter(
            **transition.permission_info
        ).exists()
        self.assertTrue(perm_exist)

    def test_delete_transition_should_delete_perm(self):
        name = 'Foo'
        _, transition, _ = self._create_transition(Order, name)
        transition.delete()
        perm_exist = Permission.objects.filter(
            **transition.permission_info
        ).exists()
        self.assertFalse(perm_exist)

    def test_change_name_should_change_perm_name_and_codename(self):
        name = 'Foo'
        _, transition, _ = self._create_transition(Order, name)

        transition.name = 'Bar'
        transition.save()

        perm_exist = Permission.objects.filter(
            **transition.permission_info
        ).exists()
        self.assertTrue(perm_exist)


class TransitionsTest(TransitionTestCase):

    def setUp(self):
        super().setUp()
        self.request = RequestFactory()
        self.request.user = get_user_model().objects.create_user(
            username='test1',
            password='password',
        )

    def test_model_should_not_found_in_registry(self):
        foo = Foo()
        irrelevant_arg = None
        with self.assertRaises(TransitionModelNotFoundError):
            _check_and_get_transition(foo, irrelevant_arg, irrelevant_arg)

    def test_transition_change_status(self):
        order = Order.objects.create()
        _, transition, _ = self._create_transition(
            model=order, name='prepare',
            source=[OrderStatus.new.id], target=OrderStatus.to_send.id,
            actions=['go_to_post_office']
        )

        self.assertEqual(order.status, OrderStatus.new.id)
        run_field_transition(
            [order], transition, request=self.request, field='status'
        )
        self.assertEqual(order.status, OrderStatus.to_send.id)

    def test_run_action_during_transition(self):
        order = Order.objects.create(status=OrderStatus.to_send.id)
        _, transition, actions = self._create_transition(
            model=order, name='send',
            source=[OrderStatus.to_send.id], target=OrderStatus.sended.id,
            actions=['go_to_post_office']
        )
        order.__class__.go_to_post_office = mocked_action
        run_field_transition(
            [order], transition, request=self.request, field='status'
        )
        self.assertTrue(order.go_to_post_office.runned)

    def test_run_transition_from_string(self):
        transition_name = 'send'
        order = Order.objects.create(status=OrderStatus.to_send.id)
        Transition.objects.create(
            name=transition_name,
            model=order.transition_models['status'],
            source=[OrderStatus.to_send.id],
            target=OrderStatus.sended.id,
        )
        self.assertTrue(
            run_field_transition(
                [order], transition_name, request=self.request, field='status'
            )
        )

    def test_run_non_existent_transition(self):
        transition_name = 'non_existent_transition'
        order = Order.objects.create()
        with self.assertRaises(Transition.DoesNotExist):
            run_field_transition(
                [order], transition_name, request=self.request, field='status'
            )

    def test_available_transitions(self):
        order = Order.objects.create()
        transition = Transition.objects.create(
            name='send',
            model=order.transition_models['status'],
            source=[OrderStatus.new.id],
            target=OrderStatus.sended.id,
        )

        self.assertEqual(
            list(order.get_available_transitions_for_status()), [transition]
        )

        order.status = OrderStatus.sended.id
        self.assertEqual(
            list(order.get_available_transitions_for_status()), []
        )

    def test_transition_exception(self):
        order = Order.objects.create()
        _, transition, actions = self._create_transition(
            model=order, name='generate_exception',
            source=[OrderStatus.new.id], target=OrderStatus.sended.id,
            actions=['generate_exception']
        )

        result, _ = run_field_transition(
            [order], transition, request=self.request, field='status'
        )
        self.assertFalse(result)

    def test_forbidden_transition(self):
        order = Order.objects.create()
        transition = Transition.objects.create(
            name='send',
            model=order.transition_models['status'],
            source=[OrderStatus.to_send.id],
            target=OrderStatus.sended.id,
        )

        self.assertEqual(
            list(order.get_available_transitions_for_status()), []
        )
        with self.assertRaises(TransitionNotAllowedError):
            run_field_transition(
                [order], transition, request=self.request, field='status'
            )

    def test_create_graph_from_actions(self):
        order = Order.objects.create()
        _, transition, _ = self._create_transition(
            model=order, name='prepare',
            source=[OrderStatus.new.id], target=OrderStatus.to_send.id,
            actions=['go_to_post_office', 'pack']
        )
        graph = _create_graph_from_actions(transition.actions.all(), order)
        self.assertEqual(graph, {
            'pack': ['go_to_post_office'],
            'go_to_post_office': [],
        })

    def test_create_graph_from_actions_when_requirement_not_in_transition(self):
        order = Order.objects.create()
        _, transition, _ = self._create_transition(
            model=order, name='prepare',
            source=[OrderStatus.new.id], target=OrderStatus.to_send.id,
            actions=['go_to_post_office']
        )
        graph = _create_graph_from_actions(transition.actions.all(), order)
        self.assertEqual(graph, {
            'go_to_post_office': [],
        })

    def test_topological_sort(self):
        graph = {
            1: [],
            2: [1, 4],
            3: [],
            4: [1]
        }
        order = [a for a in _sort_graph_topologically(graph)]
        # order of 2 and 3 doesn't matter
        self.assertEqual(set(order[:2]), set([2, 3]))
        self.assertEqual(order[2:], [4, 1])

    def test_topological_sort_cycle(self):
        graph = {
            1: [2],
            2: [1, 4],
            3: [],
            4: [1]
        }
        with self.assertRaises(CycleError):
            [a for a in _sort_graph_topologically(graph)]
