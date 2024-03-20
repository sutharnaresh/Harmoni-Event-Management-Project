"""EventManagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from EventManagement import views
from django.conf import settings
from django.conf.urls.static import static 
from django.conf.urls import handler404


urlpatterns = [
    path('admin/', admin.site.urls),

    #------------- User Path -----------------#

    #--Header--#
    path('',views.index , name="index"),
    path('home/',views.home,name="home"),
    path('home/serach',views.home_search,name="home_search"),
    path('event/',views.event , name="event"),
    path('event/closed-event/',views.closed_event,name="closed_event"),
    path('about-us/',views.about , name="about"),
    path('company/',views.company,name="company"),
    path('company/<slug>',views.company_profile,name="company_profile"),
    path('contact-us/',views.contact , name="contact"),
    path('event-details/<slug>',views.event_details , name="event_details"),
    path('event-register/<slug>',views.event_register,name="event_register"),
    path('register-successful/',views.register_success,name="register_success"),
    path('history/',views.history,name="history"),
    path('feedback/',views.feedback,name="feedback"),
    path('FAQ/',views.FAQ,name="FAQ"),
    

    #--Login ,  Logout & js AJAX finctions--#
    path('get-city/',views.get_city , name = "get_city"),
    path('login/',views.logIn,name="handle_login"),
    #------------------------------------#

    #-----Account purpose---------#
    path('account/register/',views.register, name="register"),
    path('account/logout/',views.logout,name="logout"),
    path('account/profile/',views.profile,name="profile"),
    path('account/update_profile',views.update_profile,name="update_profile"),

    path('accounts/', include('django.contrib.auth.urls')),
    #------------------------------------#

    #-- 404-Error Page --#
    path('404-error/',views.error_404, name="error_404"),
    #------------------------------------#

    #-- Companu URL Path --#
    path('',include("company.urls")),
    #------------------------------------#

    #---- Search Event ----------#
    path('event/search/',views.search_event,name="search_event"),
    #------------------------------------#
] + static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)

handler404 = 'EventManagement.views.error_404'