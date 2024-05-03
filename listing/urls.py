from django.urls import path
from . import views

urlpatterns = [
    path("create", views.CreateListingView.as_view(), name="create_listing"),
    path("getlistings", views.GetAllListings.as_view(), name="get_listings"),
    path("update", views.GetUpdateListingView.as_view(), name="update_listing"),
    path("update/<int:listId>", views.GetSingleListing.as_view(), name="get_single_list"),
    path("delete", views.GetSingleListing.as_view(), name="delete_listing"),
    path("listsearch", views.ListingSearchAPIView.as_view(), name="listsearch"),
    path("nearbypost/<int:listId>", views.NearbyPostsAPIView.as_view(), name="nearbypost"),

    path("listuserprofile/<int:listId>", views.UserListProfileView.as_view(), name="listuserprofile"),
    path('listings/<int:listing_id>/interested', views.InterestedCreateView.as_view(), name='interested-create'),
    path('interested', views.InterestedListView.as_view(), name='interested-list'),
    path('interestedusers', views.InterestedUsersListView.as_view(), name='interested-users'),
    path('interesteduserprofile/<int:userId>', views.InterestedUserProfileView.as_view(),
         name='interested_user_profile'),

    path('make-deal', views.MakeDealAPIView.as_view(), name="make-deal"),
    path('confirm-deal/<int:listing_id>', views.ConfirmDealAPIView.as_view(), name="confirm-deal"),
    path('my-deal', views.MyDealView.as_view(), name="my-deal"),
]
