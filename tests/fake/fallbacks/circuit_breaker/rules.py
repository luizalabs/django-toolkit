# -*- coding: utf-8 -*-
from django_toolkit.fallbacks.circuit_breaker.rules import Rule


class FakeRuleShouldOpen(Rule):

    def should_open_circuit(self, total_failures, total_requests):
        return True

    def log_increase_failures(self, total_failures, total_requests):
        pass


class FakeRuleShouldNotOpen(Rule):

    def should_open_circuit(self, total_failures, total_requests):
        return False

    def log_increase_failures(self, total_failures, total_requests):
        pass


class FakeRuleShouldNotIncreaseFailure(Rule):

    def should_increase_failure_count(self):
        return False

    def should_open_circuit(self, total_failures, total_requests):
        return False

    def log_increase_failures(self, total_failures, total_requests):
        pass


class FakeRuleShouldNotIncreaseRequest(Rule):

    def should_increase_request_count(self):
        return False

    def should_open_circuit(self, total_failures, total_requests):
        return False

    def log_increase_failures(self, total_failures, total_requests):
        pass
