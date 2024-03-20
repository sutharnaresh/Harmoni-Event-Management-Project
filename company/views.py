from django.shortcuts import render,redirect
from event_data.models import *
from django.conf import settings
from EventManagement.settings import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required , user_passes_test
from django.contrib.auth.models import User
import razorpay
from django.views.decorators.csrf import csrf_protect
from django.db.models import Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives

# from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

@login_required(login_url="/accounts/login/")
@user_passes_test(lambda u: u.is_staff, login_url='/404-error/')
def my_event(request):
    #--------- For search -----------#
    if request.method == "POST":
        active="myevent"
        search = request.POST.get('search')
        if search == "all":
            return redirect('myevent') 
        else:
            Company_id = Company.objects.get(User_id=request.user)
            event = Event.objects.filter(event_subcategory_id=search,company_id=Company_id).order_by("start_datetime") 
        Event_Category = Event.objects.filter(company_id=Company_id)
        Event_workhand_obj = Event_workhand.objects.all()
        context = {
            'active' : active,
            'events' : event,
            'event_count' : event.count(),
            'Event_Workhand' : Event_workhand_obj,
            'total_event' : Event.objects.filter(company_id=Company_id).count(),
            'Event_Category' : Event_Category,
        }

        return render(request,'vendor/company_event.html',context)
    #------------ Search end -----------#
    active="myevent"
    company_id = Company.objects.get(User_id=request.user)
    Events = Event.objects.filter(company_id=company_id).order_by("-start_datetime")
    Event_Category = Event.objects.filter(company_id=company_id)
    Event_workhand_obj = Event_workhand.objects.all()

    #---- Search GET -----#
    if request.GET.get('year-search'):
        year = request.GET.get('year-search')
        Events = Event.objects.filter(company_id=company_id,start_datetime__year=year)

    if request.GET.get('month-search'):
        month = request.GET.get('month-search')
        Events = Event.objects.filter(company_id=company_id,start_datetime__month=month)
    #-----------------------------#


    #---- For pagination ---#
    paginator = Paginator(Events,2)
    page_number = request.GET.get('page')
    EventDataFinal = paginator.get_page(page_number)
    totalPage = EventDataFinal.paginator.num_pages

    contaxt={
        'active' : active,
        'events' : EventDataFinal,
        'totalPageList' : [n+1 for n in range(totalPage)],
        'event_count' : Events.count(),
        'total_event' : Event.objects.filter(company_id=company_id).count(),
        'currentPage': EventDataFinal.number,  # Pass current page number to template
        'Event_Workhand' : Event_workhand_obj,
        'Event_Category' : Event_Category,
    }
    return render(request,'vendor/company_event.html',contaxt)


@login_required(login_url="/accounts/login/")
@user_passes_test(lambda u: u.is_staff, login_url='/404-error/')
def add_event(request):
    if request.method == "POST":
        try:
            Event_Category_id = request.POST.get('cat')
            Event_Subcategory_id = request.POST.get('subcat')
            event_name = request.POST.get('event_name')
            start_datetime_str = request.POST.get('start_datetime')
            end_datetime_str = request.POST.get('end_datetime')
            street_address = request.POST.get('street_address')
            state_id = request.POST.get('state')
            city_id = request.POST.get('city')
            description = request.POST.get('description')

            start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%dT%H:%M")
            end_datetime = datetime.strptime(end_datetime_str, "%Y-%m-%dT%H:%M")
            current_date = timezone.now().date()

            # Now perform the comparison considering only dates
            if start_datetime.date() <= current_date:
                messages.error(request, "Start date should be greater than today")
                return redirect("addevent")
            elif start_datetime > end_datetime:
                messages.error(request, "Start date should be less than end date")
                return redirect("addevent")

            Workhand_categories = request.POST.getlist('Workhand_categories')
            price = request.POST.getlist('price')
            workhand_number = request.POST.getlist('workhand_number')
            total_workhand = sum(map(int ,workhand_number))
            total_price = sum(map(int , price))

            #Object Instances--->
            Event_Category_obj = Event_Category.objects.get(id = Event_Category_id)
            Event_subcategory_obj = Event_subcategory.objects.get(id=Event_Subcategory_id)
            city_obj = City.objects.get(id=city_id)
            state_obj = State.objects.get(id=state_id)
            Company_id = Company.objects.get(User_id = request.user)
            # ------------------>

            if len(Workhand_categories) == len(workhand_number) == len(price):
                # Save data in Event Table
                Event_info = Event(event_name=event_name , description = description , start_datetime = start_datetime , end_datetime = end_datetime , total_workhand = total_workhand, total_price = total_price ,street_address = street_address , city_id = city_obj , state_id = state_obj , event_category_id = Event_Category_obj , event_subcategory_id = Event_subcategory_obj , company_id = Company_id)
                Event_info.save()

                # Save data in Event_workhand Table
                for Workhand_category_id, numbers_of_workhand , workhand_price in zip(Workhand_categories, workhand_number,price):
                    Workhand_category_obj = None
                    Workhand_category_obj = Workhand_category.objects.get(id=Workhand_category_id)
                    Event_workhand_info = Event_workhand(Workhand_category_id = Workhand_category_obj , number_of_workhand=numbers_of_workhand , price = workhand_price , event_id=Event_info )
                    Event_workhand_info.save()

                messages.success(request , "Event Successfully Added!!")
                return redirect('addevent')
            
            messages.error(request , "Something Went Wrong!!")
            return redirect('addevent')
        except:
            messages.error(request,"Something Went Wrong. Try again!")
            return redirect('addevent')
    
    Event_category = Event_Category.objects.all()
    States = State.objects.all().order_by('-state_name')
    Workhand_categories = Workhand_category.objects.all().order_by('workhand_category_name')
    active = "myevent"
    context={
        'active' : active,
        'States' : States,
        'Workhand_category' : Workhand_categories,
        'Event_category' : Event_category
    }
    return render(request , 'vendor/addevent.html',context)



@login_required(login_url="/accounts/login/")
@user_passes_test(lambda u: u.is_staff, login_url='/404-error/')
def workhand_profile(request,slug):
    active = "myevent"
    workhand_info = Workhand.objects.get(slug=slug)
    workhand_events = Event_Registrations.objects.filter(workhand_id=workhand_info,payment_status=True)
    context={
        'active' : active,
        'workhand' : workhand_info,
        'workhand_events' : workhand_events,
    }
    return render(request,'vendor/workhand_profile.html',context)




@login_required(login_url="/accounts/login/")
@user_passes_test(lambda u: u.is_staff, login_url='/404-error/')
def workhand_requests(request,slug):
    active = "myevent"
    event = Event.objects.get(slug=slug)
    workhands_Requests = Event_Registrations.objects.filter(event_id=event).order_by('-event_workhand_id')
    event_workhand = Event_workhand.objects.all() 
    context = {
        'active' : active,
        'event' : event,
        'workhands_Requests' : workhands_Requests,
        'event_workhand':event_workhand,
    }
    return render(request,'vendor/request_approve.html',context)


# Only for redirect purpose
@login_required(login_url="/accounts/login/")
@user_passes_test(lambda u: u.is_staff, login_url='/404-error/')
def request_approve(request):
    Registeration_id = request.GET.get('Registeration_id')
    event_registration_info = Event_Registrations.objects.get(id=Registeration_id)
    event_slug=event_registration_info.event_id.slug #for getting slug
    Registered_workhands = len(Event_Registrations.objects.filter(registration_status=True,event_workhand_id=event_registration_info.event_workhand_id))
    if (int(event_registration_info.event_workhand_id.number_of_workhand)-1) >= int(Registered_workhands):   
        event_registration_info.registration_status = True
        event_registration_info.save()
        return redirect('workhand_requests',slug=event_slug)
    else:
        messages.error(request,f"You need only {event_registration_info.event_workhand_id.number_of_workhand} {event_registration_info.event_workhand_id}")
        print("Error")
        return redirect('workhand_requests',slug=event_slug)


# Only for redirect purpose
@login_required(login_url="/accounts/login/")
@user_passes_test(lambda u: u.is_staff, login_url='/404-error/')
def approved_requests(request,slug):
    if request.method == "POST":
        Registeration_id = request.POST.get("Registeration_id")
        Event_Registrations_info = Event_Registrations.objects.get(id=Registeration_id)
        Event_Registrations_info.registration_status = False
        Event_Registrations_info.payment_status = False
        Event_Registrations_info.save()
        return redirect('approved_requests',slug=slug)

    active = "myevent"
    event = Event.objects.get(slug=slug)
    workhands_Requests = Event_Registrations.objects.filter(event_id=event , registration_status=True).order_by('event_workhand_id')
    context = {
        'active' : active,
        'event' : event,
        'workhands_Requests' : workhands_Requests,
    }
    return render(request,'vendor/approved_requests.html',context)



@user_passes_test(lambda u: u.is_staff, login_url='/404-error/')
def payment(request,slug):
    active = "myevent"
    event = Event.objects.get(slug=slug)
    Registered_workhand = Event_Registrations.objects.filter(event_id=event , registration_status=True).order_by("-registration_date")
    total_price = 0
    for i in Registered_workhand:
        total_price += i.event_workhand_id.price
    context = {
        'active' : active,
        'event' : event,
        'workhands' : Registered_workhand,
        'total_price' : total_price,
    }
    return render(request,'vendor/payment.html',context)




@login_required(login_url="/accounts/login/")
@user_passes_test(lambda u: u.is_staff, login_url='/404-error/')
def success(request):
    try:
        event_register_id = request.GET.get('workhand_id')
        rate = request.GET.get('rating')
        event_registration_info = Event_Registrations.objects.get(id=event_register_id)
        event_registration_info.payment_status = True
        event_registration_info.rating = rate
        event_registration_info.save()
        event_slug=event_registration_info.event_id.slug #for getting slug

        #--------For Email-----#
        email = event_registration_info.workhand_id.email

        subject = "Payment Successful"
        msg = "Your payment have been successully done. <br>Thank you so much for registering in event.We hope you visit us again!.<br>HAVE A NICE DAY."
        from_email = settings.EMAIL_HOST_USER
        msg = EmailMultiAlternatives(subject , msg , from_email , [email])
        msg.content_subtype = 'html'
        msg.send()
        #----------------------------------#

        #--------------- Find Average Rating ------------------#
        workhand = event_registration_info.workhand_id #For getting workhand_id and it is used to change avg_rating in workhand model
        average_rating = Event_Registrations.objects.filter(registration_status=True,workhand_id=workhand).aggregate(avg_rating=Avg('rating'))['avg_rating']
        workhand_info = Workhand.objects.get(id=workhand.id) # Get object of Workhand model
        workhand_info.avg_rating = average_rating
        workhand_info.save()
        return redirect('payment', slug=event_slug)
    except:
        messages.error(request , "Something went wrong!!")
        return redirect('payment',slug=event_slug)

def get_subcat(request):
    cat_id = request.GET['cat_id']
    get_cat = Event_Category.objects.get(id = cat_id)
    subcat = Event_subcategory.objects.filter(Event_Category_id = get_cat)
    return render(request , 'vendor/get-subcat.html',locals())

