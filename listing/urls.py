from django.urls import path
from . import views

urlpatterns = [
    path("create", views.CreateListingView.as_view(), name="create_listing"),
    path("getlistings", views.GetAllListings.as_view(), name="get_listings"),
    path("update", views.GetUpdateListingView.as_view(), name="update_listing"),
    path("update/<int:listId>", views.GetSingleListing.as_view(), name="get_single_list"),
    path("listsearch", views.ListingSearchAPIView.as_view(), name="listsearch"),
    path("nearbypost/<int:listId>", views.NearbyPostsAPIView.as_view(), name="nearbypost"),
    path("listuserprofile/<int:listId>", views.UserListProfileView.as_view(), name="listuserprofile"),
]
