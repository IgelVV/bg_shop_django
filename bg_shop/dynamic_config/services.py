from django.conf import settings

from dynamic_config import models


class DynamicConfigService:
    @staticmethod
    def set_default_config():
        d_config = models.DynamicConfig(
            ordinary_delivery_cost=settings.ORDINARY_DELIVERY_COST,
            express_delivery_extra_charge=settings.EXPRESS_DELIVERY_EXTRA_CHARGE,
            boundary_of_free_delivery=settings.BOUNDARY_OF_FREE_DELIVERY,
            company_info=settings.COMPANY_INFO,
            legal_address=settings.LEGAL_ADDRESS,
            main_phone=settings.MAIN_PHONE,
            main_email=settings.MAIN_EMAIL,
        )
        d_config.save()

