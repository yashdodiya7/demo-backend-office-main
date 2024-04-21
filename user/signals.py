# from django.db.models.signals import post_save
#
# from .models import Profile, User
#
#
# def createProfile(sender, instance, created, **kwargs):
#     if created:
#         user = instance
#         profile = Profile.objects.create(
#             user_id=user,
#         )
#
#
# # def updateUser(sender, instance, created, **kwargs):
# #     profile = instance
# #     user = profile.user
# #
# #     if created == False:
# #         user.first_name = profile.name
# #         user.email = profile.email
# #         user.username = profile.username
# #         user.save()
#
#
# post_save.connect(createProfile, sender=User)
# # post_save.connect(updateUser, sender=Profile)
