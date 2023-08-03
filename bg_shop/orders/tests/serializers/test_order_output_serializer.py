from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from orders.models import Order
from orders.serializers import OrderOutputSerializer
from account.models import Profile
from dynamic_config.services import DynamicConfigService

UserModel = get_user_model()


@override_settings(
    BOUNDARY_OF_FREE_DELIVERY=10,
    ORDINARY_DELIVERY_COST=5,
    EXPRESS_DELIVERY_EXTRA_CHARGE=5,
)
class OrderOutputSerializerTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        DynamicConfigService.set_default_config()

    def setUp(self):
        user = UserModel.objects.create(
            username='testuser', email='test@example.com')
        Profile.objects.create(user=user, phone_number='1234567890')
        Order.objects.create(
            user=user,
            delivery_type=Order.DeliveryTypes.EXPRESS,
            payment_type=Order.PaymentTypes.ONLINE,
            city='Test City',
            address='Test Address',
            comment='Test Comment',
            paid=True,
            status=Order.Statuses.COMPLETED,
        )

    def test_order_output_serializer_fields(self):
        order = Order.objects.first()
        serializer = OrderOutputSerializer(instance=order)

        expected_data = {
            "id": order.id,
            "createdAt": order.created_at.isoformat().replace('+00:00', 'Z'),
            "fullName": order.user.get_full_name(),
            "email": order.user.email,
            "phone": order.user.profile.phone_number,
            "deliveryType": Order.DeliveryTypes.EXPRESS,
            "deliveryCost": Decimal('10'),
            "totalCost": Decimal('10'),
            "status": Order.Statuses.COMPLETED,
            "paid": True,
            "paymentType": Order.PaymentTypes.ONLINE,
            "city": 'Test City',
            "address": 'Test Address',
            "comment": 'Test Comment',
            "products": [],
        }
        self.assertEqual(
            serializer.data,
            expected_data,
            "Serializer data doesn't match expected data",
        )
