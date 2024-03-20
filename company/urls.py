from django.urls import path,include
from company import views
from EventManagement import urls
from django.conf.urls import handler404

urlpatterns = [
    path("my-events/",views.my_event,name="myevent"),
    path("add-event/" , views.add_event , name="addevent"),
    path("get-subcat/",views.get_subcat , name = "get_subcat"),
    path("workhands-requests/workhand-profile/<slug>",views.workhand_profile, name="workhand_profile"),
    path("workhands-requests/<slug>",views.workhand_requests,name="workhand_requests"),
    path("workhands-requests/approved-requests/<slug>",views.approved_requests,name="approved_requests"),
    path("request-approve/",views.request_approve,name="request_approve"),
    path("payment/<slug>",views.payment , name="payment"),
    path('payment/success/',views.success,name="success"),


    #------- Users Url's path-------#
    # path('',include("EventManagement.urls")),

    #---------- For Admin ---------------#
    # path('admin/report/',views.report,name="report"),
    #------------------------------------#
]

handler404 = 'EventManagement.views.error_404'