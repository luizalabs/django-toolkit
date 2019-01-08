# -*- coding: utf-8 -*-
from django_toolkit.fallbacks.circuit_breaker.rules import Rule


class FakeRuleShouldOpen(Rule):

    def should_open_circuit(self, total_failures, total_requests):
        return True


class FakeRuleShouldNotOpen(Rule):

    def should_open_circuit(self, total_failures, total_requests):
        return False
