"""Enums related to Payment."""

from enum import Enum


class PaymentStatuses(Enum):
    SUCCESS = "success"
    FAIL = "fail"
