import json
from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from orders import models as order_models
from payment import models as payment_models
from payment import enums

User = get_user_model()


class PaymentWebhookTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword')
        self.order = order_models.Order.objects.create(user=self.user)

    def test_successful_payment_webhook(self):
        payload = {
            "PAYMENT_SERVICE_SIGNATURE": settings.PAYMENT_SERVICE_SIGNATURE,
            "status": enums.PaymentStatuses.SUCCESS.value,
            "order_id": self.order.pk,
            "payment_id": f"{self.order.pk}test_payment_id"
        }
        response = self.client.post(reverse('api:payment:payment-webhook'),
                                    data=payload,
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertTrue(self.order.paid)
        payment = payment_models.Payment.objects.get(order=self.order)
        self.assertEqual(payment.payment_id, f"{self.order.pk}test_payment_id")

    def test_failed_payment_webhook(self):
        payload = {
            "PAYMENT_SERVICE_SIGNATURE": settings.PAYMENT_SERVICE_SIGNATURE,
            "status": enums.PaymentStatuses.FAIL.value,
            "order_id": self.order.pk,
            "payment_id": f"{self.order.pk}test_payment_id"
        }

        response = self.client.post(reverse('api:payment:payment-webhook'),
                                    data=payload,
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertFalse(self.order.paid)
        self.assertEqual(self.order.status,
                         order_models.Order.Statuses.REJECTED)

    def test_invalid_signature(self):
        payload = {
            "PAYMENT_SERVICE_SIGNATURE": "invalid_signature",
            "status": enums.PaymentStatuses.SUCCESS.value,
            "order_id": self.order.pk,
            "payment_id": f"{self.order.pk}test_payment_id"
        }
        payload_json = json.dumps(payload)

        response = self.client.post(reverse('api:payment:payment-webhook'),
                                    data=payload_json,
                                    content_type='application/json')

        self.assertEqual(response.status_code, 403)
        self.order.refresh_from_db()
        self.assertFalse(self.order.paid)
