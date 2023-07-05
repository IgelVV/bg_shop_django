# from django.db.models import signals
# from django.dispatch import receiver
#
# from common import models
#
#
# @receiver(signals.post_delete, sender=models.Image)
# def post_save_image(sender, instance, *args, **kwargs):
#     """Clean Old Image file."""
#     instance.img.delete(save=False)
#
#
# @receiver(signals.pre_save, sender=models.Image)
# def pre_save_image(sender, instance, *args, **kwargs):
#     """ instance old image file will delete from os """
#     try:
#         old_img = instance.__class__.objects.get(id=instance.id).img.path
#         # try:
#         new_img = instance.image.path
#         # except:
#         #     new_img = None
#         if new_img != old_img:
#             import os
#             if os.path.exists(old_img):
#                 os.remove(old_img)
#     except models.Image.DoesNotExist:
#         pass
