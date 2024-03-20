from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import messages
from event_data.models import *
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.http import HttpResponse
from company.views import *
from django.db.models import Q

def index(request):
    return redirect('home')

def home(request):
    active = "home"
    events = Event.objects.order_by('start_datetime')[:6]
    context={
        'active' : active,
        'events' : events
    }
    return render(request , 'user/home.html',context)

def home_search(request):
    search_keyword = request.POST.get('keyword')
    if search_keyword:
            events = Event.objects.filter(event_name__icontains=search_keyword)
            
            active = "event"
            Event_subcategory_obj = Event_subcategory.objects.all()
            Event_workhand_obj = Event_workhand.objects.all()
            total_event = Event.objects.count()
            event_count = events.count()
            context={
                'active' : active,
                'events' : events,
                'Event_subcategory' : Event_subcategory_obj,
                'Event_Workhand' : Event_workhand_obj,
                'total_event': total_event,
                'event_count': event_count
            }
    else:
        return redirect('event')

def event(request):
    active = "event"
    current_datetime = timezone.now()
    events = Event.objects.filter(start_datetime__gt=current_datetime).order_by('start_datetime')
    Event_subcategory_obj = Event_subcategory.objects.all().order_by()
    Event_workhand_obj = Event_workhand.objects.all()

    total_event = Event.objects.count()
    event_count = events.count()
    #---- For pagination ---#
    paginator = Paginator(events,5)
    page_number = request.GET.get('page')
    EventDataFinal = paginator.get_page(page_number)
    totalPage = EventDataFinal.paginator.num_pages
    #------------------------#

    context={
        'active' : active,
        'events' : EventDataFinal,
        'totalPageList' : [n+1 for n in range(totalPage)],
        'currentPage': EventDataFinal.number,  # Pass current page number to template
        'Event_subcategory' : Event_subcategory_obj,
        'Event_Workhand' : Event_workhand_obj,
        'event_count' : event_count,
        'total_event' : total_event,
    }
    return render(request , 'user/event.html',context)

def closed_event(request):
    active = "event"
    events = Event.objects.all().order_by("start_datetime")
    Event_subcategory_obj = Event_subcategory.objects.all().order_by()
    Event_workhand_obj = Event_workhand.objects.all()
    context={
        'active' : active,
        'events' : events,
        'Event_subcategory' : Event_subcategory_obj,
        'Event_Workhand' : Event_workhand_obj,
    }
    return render(request , 'user/close-event.html',context)

def search_event(request):
    if request.method == "POST":
        search_keyword = request.POST.get('keyword')
        search = request.POST.get('search')
        events = Event.objects.all()
        if not search_keyword == "":
            events = events.filter(
                Q(event_name__icontains = search_keyword) |
                Q(company_id__name__icontains = search_keyword) |
                Q(city_id__city_name__icontains = search_keyword) |
                Q(state_id__state_name__icontains = search_keyword)
                )
            
            active = "event"
            Event_subcategory_obj = Event_subcategory.objects.all()
            Event_workhand_obj = Event_workhand.objects.all()
            total_event = Event.objects.count()
            event_count = events.count()
            
            context={
            'active' : active,
            'events' : events,
            'Event_subcategory' : Event_subcategory_obj,
            'Event_Workhand' : Event_workhand_obj,
            'total_event' : total_event,
            'event_count' :  event_count,
            }

            return render(request , 'user/event.html',context)

        if search == "all": 
            return redirect('event') 
        else:
            events = Event.objects.filter(event_subcategory_id=search) 

        active = "event"
        Event_subcategory_obj = Event_subcategory.objects.all()
        Event_workhand_obj = Event_workhand.objects.all()
        total_event = Event.objects.count()
        event_count = events.count()

        context={
        'active' : active,
        'events' : events,
        'Event_subcategory' : Event_subcategory_obj,
        'Event_Workhand' : Event_workhand_obj,
        'total_event' : total_event,
        'event_count' :  event_count,
        }
        return render(request , 'user/event.html',context)

@login_required
def event_details(request,slug):
    if request.method == 'POST':
        event_details = Event.objects.get(slug=slug)
        workhands_feedback = Feedback.objects.filter(event_id=event_details)
        if not request.user.is_staff:
            workhand_detail = Workhand.objects.get(User_id=request.user)
            already_registered = Event_Registrations.objects.filter( workhand_id=workhand_detail , event_id=event_details)
             #------ Feedback ---------#
            workhand_info = Workhand.objects.get(User_id = request.user)
            feedback = Event_Registrations.objects.filter(workhand_id=workhand_info,registration_status=True,event_id=event_details)
            already_feedback = Feedback.objects.filter(event_id=event_details , workhand_id=Workhand.objects.get(User_id=request.user))
            #-------------------------#
            contaxt = {
                'event' : event_details,
                'already_registered' : already_registered,
                'feedback' : feedback,
                'workhand' : workhand_info,
                'workhands_feedback' : workhands_feedback,
                'already_feedback' : already_feedback
            }
        else:
             contaxt = {
                'event' : event_details,
                'workhands_feedback' : workhands_feedback,
            }
        return render(request , 'user/event-details.html',contaxt)

    if slug is not None:
            event_details = Event.objects.get(slug=slug)
            workhands_feedback = Feedback.objects.filter(event_id=event_details)
            Event_Registration_info = Event_Registrations.objects.filter(event_id=event_details) # For getting rating in event-detail page
            if not request.user.is_staff: 
                # Check workhand already does feedback or not
                already_feedback = Feedback.objects.filter(event_id=event_details , workhand_id = Workhand.objects.get(User_id=request.user))
                contaxt = {
                        'event' : event_details,
                        'workhands_feedback' : workhands_feedback,
                        'Event_Registration_info' : Event_Registration_info,
                        'already_feedback' : already_feedback,
                    }
                return render(request , 'user/event-details.html',contaxt)

            elif request.user.is_staff:
                contaxt = {
                        'event' : event_details,
                        'workhands_feedback' : workhands_feedback,
                        'Event_Registration_info' : Event_Registration_info,
                    }
                return render(request , 'user/event-details.html',contaxt)

            else:
                return HttpResponse("Method not allowed", status=405)

@login_required
def event_register(request,slug):
    if request.method == "POST":
        Event_detail = Event.objects.get(slug=slug)
        workhand = Workhand.objects.get(User_id=request.user)
        #Check that wokrhand is already registerd in this event or not
        already_registered = Event_Registrations.objects.filter(workhand_id=workhand , event_id=Event_detail)
        if already_registered:
            messages.error(request,f"You are already registered in this event!!")
            return redirect('event')
        else:
            selected_category = request.POST.get('selected_category')
            if selected_category is not None:
                event_workhand =  Event_workhand.objects.get(id=selected_category)  
                registration = Event_Registrations(event_workhand_id=event_workhand , workhand_id = workhand , event_id = Event_detail , company_id = Event_detail.company_id)
                registration.save()

                #---------Email code-------------# 
                subject = "Event Registration Successfully!!"
                msg = f"Your event registration is successful"
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(subject , msg , from_email , [workhand.email])
                msg.content_subtype = 'html'
                msg.send()
                #--------------------#
                return redirect('register_success')
            else:
                pass

    event_details = Event.objects.get(slug=slug)
    event_workhand = Event_workhand.objects.all()   
    workhand = Workhand.objects.get(User_id=request.user)
    contaxt={
        'event':event_details,
        'event_workhand' : event_workhand,
        'workhand' : workhand,
    }
    return render(request , 'user/event-register.html',contaxt)

@login_required
def register_success(request):
    return render(request,'user/sucessful_register.html')

def about(request):
    active = "about"
    context={
        'active' : active
    }
    return render(request , 'user/about.html',context)

@login_required
def history(request):
    active = 'history'
    workhand = Workhand.objects.get(User_id=request.user)
    registration = Event_Registrations.objects.filter(workhand_id=workhand)
    Event_workhand_obj = Event_workhand.objects.all()

    #-- For Feedback -->
    feedback = Feedback.objects.filter(workhand_id=workhand)

    #---- For pagination ---#
    paginator = Paginator(registration,3)
    page_number = request.GET.get('page')
    RegistrationDataFinal = paginator.get_page(page_number)
    totalPage = RegistrationDataFinal.paginator.num_pages
    context={
        'active':active,
        'registration':RegistrationDataFinal,
        'Event_Workhand' : Event_workhand_obj,
        'totalPageList' : [n+1 for n in range(totalPage)],
        'currentPage': RegistrationDataFinal.number,  # Pass current page number to template
        'feedback' : feedback,
    }
    return render(request,'user/history.html',context)

def company(request):
    active = "vendor"
    company_obj = Company.objects.all()
    contaxt={
        'active' : active,
        'company' : company_obj
    }
    return render(request , 'user/company.html',contaxt)

def company_profile(request,slug):
    active = "vendor"
    Company_obj = Company.objects.get(slug=slug)
    events = Event.objects.filter(company_id = Company_obj)
    context={
        'active' : active,
        'company' : Company_obj,
        'events' : events,
    }
    return render(request , 'user/company_profile.html',context)

@login_required(login_url="/accounts/login/")
def contact(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            mail = request.POST.get('email')
            city = request.POST.get('city')
            number = request.POST.get('number')
            message = request.POST.get('message')

            #Email code 
            subject = "We Recieved Your E-mail!"
            msg = f"Your email has succesfully sent to us. you message is <h>'{message}'</h>. <br> Now we work on your problem/suggestion and fix it as soon as if possible. <br>Thank You!!"
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(subject , msg , from_email , [mail])
            msg.content_subtype = 'html'
            msg.send()
            #--------------------#

            messages.success(request,f"your message has been Succesfully Sent!")
            return redirect('contact')
        except e:
            messages.error(request,"Something went wrong!!")
            return redirect('contact')
            

    active="contact"
    User = None
    if not request.user.is_staff:
        User = Workhand.objects.get(User_id=request.user)
    else:
        User = Company.objects.get(User_id=request.user)
    contaxt={
        'active' : active,
        'User' : User,
    }
    return render(request , 'user/contact.html',contaxt)

def register(request):
    if request.method == "POST":
        try:
            role = request.POST.get('role')

            if role == "workhand":
                username = request.POST.get('username')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')
                email = request.POST.get('email')
                contact_number = request.POST.get('contact_number')
                street_address = request.POST.get('street_address')
                state = request.POST.get('state')
                city = request.POST.get('city')
                workhand_category = request.POST.get('workhand_category')
                profile_image = request.FILES.get('profile_image')
                
                #Object Instances--->
                city_obj = City.objects.get(id=city)
                state_obj = State.objects.get(id=state)
                workhand_category_obj = Workhand_category.objects.get(id=workhand_category)
                # ------------------>

                if password and confirm_password:
                    if password != confirm_password:
                        messages.error(request , "Password does not  match")
                        return redirect('register')
                    else:
                        try:
                        #save user model
                            user_info = User.objects.create_user(username = username , first_name = first_name , last_name = last_name ,password = password , email = email)
                            user_info.save()
                        except:
                            messages.error(request,"Username is already taken!")
                            return redirect('register')

                        if profile_image:
                            #save workhand model
                            Workhand_info = Workhand(first_name=first_name , last_name=last_name , email=email , contact_number=contact_number , street_address=street_address ,state_id=state_obj , city_id=city_obj , profilePic_path=profile_image , Workhand_category_id=workhand_category_obj , User_id=user_info)
                            Workhand_info.save()

                            #save in Porfile model
                            user_profile = profile_pics(User=user_info , image = profile_image)
                            user_profile.save()
                        else:
                            #save workhand model
                            Workhand_info = Workhand(first_name=first_name , last_name=last_name , email=email , contact_number=contact_number , street_address=street_address ,state_id=state_obj , city_id=city_obj , Workhand_category_id=workhand_category_obj , User_id=user_info)
                            Workhand_info.save()

                            #save in Porfile model
                            user_profile = profile_pics(User=user_info)
                            user_profile.save()

                        #user login and redirect
                        auth_login(request,user_info)

                        #Email code 
                        subject = "Sucessfully loggedIn!!"
                        msg = f"Welcome {username} to Harmoni Event Management!<br>We are thrilled to welcome you to the community! Thank you for choosing us as your partner.<br>As a newly registered user, you now have access to a wide range of events.<br>Here are a few things you can do now to get started:<br>Explore Our Features- Take some time to explore all the features and functionalities available to you and Stay Connected- Connect with us on social media platforms to stay updated on the latest events and updates.<br>We are committed to providing you with the best possible experience, and we value your feedback.<br>Please feel free to share your thoughts, suggestions, or concerns with us at any time.<br>Once again, welcome to the Harmoni family! We're excited to embark on this journey with you.<br><br>Best regards,<br>Harmoni Event Management,<br>6354981001"
                        from_email = settings.EMAIL_HOST_USER
                        msg = EmailMultiAlternatives(subject , msg , from_email , [email])
                        msg.content_subtype = 'html'
                        msg.send()
                        #--------------------#

                        #redirected on index page
                        return redirect('index')
                        #--------------------#

            elif role == "vendor":
                username = request.POST.get('username')
                company_name = request.POST.get('company_name')
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')
                email = request.POST.get('email')
                contact_number = request.POST.get('contact_number')
                street_address = request.POST.get('street_address')
                state = request.POST.get('state')
                city = request.POST.get('city')
                discription = request.POST.get('discription')
                company_logo = request.FILES.get('company_logo')

                #Object Instances--->
                city_obj = City.objects.get(id=city)
                state_obj = State.objects.get(id=state)
                # ------------------>

                if password and confirm_password:
                    if password != confirm_password:
                        messages.error(request , "Password doen's match")
                        return redirect('register')
                    else:
                        try:
                            #save user model
                            user_info = User.objects.create_user(username = username , first_name = company_name ,password = password , email = email ,is_staff = True)
                            user_info.save()
                        except:
                            messages.error(request,"Username is already taken!")
                            return redirect('register')

                        if company_logo:
                            #save company model
                            Company_info = Company(name=company_name , email=email , contact_number=contact_number , street_address=street_address , city_id = city_obj , state_id=state_obj , companyLogo_path = company_logo, description=discription ,User_id=user_info)
                            Company_info.save()
                            
                            # Save in profile table
                            user_profile = profile_pics(User=user_info , image = company_logo)
                            user_profile.save()
                        else:
                            Company_info = Company(name=company_name , email=email , contact_number=contact_number , street_address=street_address , city_id = city_obj , state_id=state_obj , description=discription ,User_id=user_info)
                            Company_info.save()
                            
                            # Save in profile table
                            user_profile = profile_pics(User=user_info)
                            user_profile.save()
                        #user login and redirect
                        auth_login(request,user_info)

                        #Email code 
                        subject = "Sucessfully loggedIn!!"
                        msg = f"Welcome {username} to Harmoni Event Management!<br>We are thrilled to welcome you to the community! Thank you for choosing us as your partner.<br>As a newly registered user, you now have access to a wide range of events.<br>Here are a few things you can do now to get started:<br>Explore Our Features- Take some time to explore all the features and functionalities available to you and Stay Connected- Connect with us on social media platforms to stay updated on the latest events and updates.<br>We are committed to providing you with the best possible experience, and we value your feedback.<br>Please feel free to share your thoughts, suggestions, or concerns with us at any time.<br>Once again, welcome to the Harmoni family! We're excited to embark on this journey with you.<br><br>Best regards,<br>Harmoni Event Management,<br>6354981001"
                        from_email = settings.EMAIL_HOST_USER
                        msg = EmailMultiAlternatives(subject , msg , from_email , [email])
                        msg.content_subtype = 'html'
                        msg.send()
                        #--------------------#

                        #redirected on index page
                        return redirect('index')
                        #--------------------#
        except:
            messages.error(request , "Something went wrong . please try again !")
            return redirect('register')

    # Register page #
    if request.user.is_authenticated:
        return redirect('home')
    else:
        States = State.objects.all().order_by('-state_name')
        Workhand_categories = Workhand_category.objects.all().order_by('workhand_category_name')
        context = {
            'States' : States,
            'Workhand_category' : Workhand_categories
        }
        return render(request , 'registration/register.html' , context)

def get_city(request):
    state_id = request.GET['state_id']
    get_state = State.objects.get(id=state_id)
    city = City.objects.filter(state_id=get_state)
    return render(request , 'login/get-city.html',locals())
    


def logIn(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('pass')

        user = authenticate(username = username , password = password)

        if user is not None:
            auth_login(request,user)
            if request.GET.get('next' , None):
                return redirect(request.GET['next'])
            return redirect('index')
        else:
            messages.error(request , "Username or Password doesn't match")
            return redirect('login')

    if request.user.is_authenticated:
        return redirect('home')
    else:
        return render(request , 'accounts/login.html')

def logout(request):
    try:
        auth_logout(request)
        return redirect('index')
    except e:
        print(e)


@login_required(login_url="/accounts/login/")
def profile(request):
    try:
        if request.user.is_staff:
            company = Company.objects.get(User_id=request.user)
            States = State.objects.all().order_by('-state_name')
            context={
                'company' : company,
                'States' : States,
            }  
        else:
            workhand = Workhand.objects.get(User_id=request.user)
            States = State.objects.all().order_by('-state_name')
            Workhand_categories = Workhand_category.objects.all().order_by('workhand_category_name')
            context={
                'workhand' : workhand,
                'States' : States,
                'Workhand_category' : Workhand_categories,
            }
        return render(request , 'user/profile.html', context)
    except:
        return redirect('index')

@login_required
def update_profile(request):
    if request.method == "POST":
        if request.user.is_staff:
            company_name = request.POST.get('company_name')
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            street_address = request.POST.get('street_address')
            state = request.POST.get('state')
            city = request.POST.get('city')
            discription = request.POST.get('discription')
            company_logo = request.FILES.get('company_logo')
            company = Company.objects.get(User_id=request.user)
            profile_id = profile_pics.objects.get(User=request.user)

            file_path = None


            if company_logo is None:
                Company.objects.filter(id=company.id).update(name=company_name , email=email , contact_number=contact_number , street_address=street_address , city_id = city , state_id=state ,  description=discription)
            else:
                file_path = default_storage.save(f'company_img/{company_logo.name}', ContentFile(company_logo.read()))
                Company.objects.filter(id=company.id).update(name=company_name , email=email , contact_number=contact_number , street_address=street_address , city_id = city , state_id=state , companyLogo_path = file_path, description=discription)
                profile_id.image = company_logo
                profile_id.save()
                
            messages.success(request , "Profile Successfully Updated!!")
            return redirect('profile')

        else:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            street_address = request.POST.get('street_address')
            state = request.POST.get('state')
            city = request.POST.get('city')
            workhand_category = request.POST.get('workhand_category')
            profile_image = request.FILES.get('profile_image')
            workhand = Workhand.objects.get(User_id=request.user)
            profile_id = profile_pics.objects.get(User=request.user)

            file_path = None

            if profile_image is None:
                Workhand.objects.filter(id=workhand.id).update(first_name=first_name, last_name=last_name , email=email , contact_number=contact_number , street_address=street_address ,state_id=state , city_id=city , Workhand_category_id=workhand_category)
            else:
                file_path = default_storage.save(f'workhand_img/{profile_image.name}', ContentFile(profile_image.read()))
                Workhand.objects.filter(id=workhand.id).update(first_name=first_name, last_name=last_name , email=email , contact_number=contact_number , street_address=street_address ,state_id=state , city_id=city , Workhand_category_id=workhand_category , profilePic_path=file_path)
                profile_id.image = profile_image
                profile_id.save()
            messages.success(request , "Profile Successfully Updated!!")
            return redirect('profile')

def error_404(request,exception):
    return render(request, 'login/404-error.html')


def feedback(request):
    if request.method == "POST":
        workhand_info = request.POST.get('workhand_id')
        event_info = request.POST.get('event_id')
        feedback = request.POST.get('feedback')

        event_obj = Event.objects.get(id=event_info)
        workhand_obj = Workhand.objects.get(id=workhand_info)

        Feedback_info = Feedback(feedback=feedback,event_id=event_obj,workhand_id=workhand_obj)
        Feedback_info.save()

        messages.success(request , "Thank You For Your Feedback !")
        return redirect('event_details', slug=event_obj.slug)

def FAQ(request):
    return render(request, "user/faq.html")