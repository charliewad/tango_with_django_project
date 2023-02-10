from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm


def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    # Place the list in our context_dict dictionary (with our boldmessage!)
    # # that will be passed to the template engine.

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    # return render response and send it back
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    context_dict = {'boldmessage': 'This tutorial has been put together by Charlie.'}

    return render(request, 'rango/about.html', context=context_dict)


def register(request):
    # boolean for telling the template whether
    # registration was successful, initially set to False
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            # hash password with set_password method and update user object
            user.set_password(user.password)
            user.save()

            # set commit = False to delay saving the model as we need to set
            # the user attributes ourselves
            profile = profile_form.save(commit=False)
            profile.user = user

            # if user provided a picture, get it from input form
            # and put it in UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            # update registered to show successful registration
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        # not POST req so we render form using blank ModelForm instances, ready for input
        user_form = UserForm()
        profile_form = UserProfileForm()


    return render(request, 'rango/register.html', context={'user_form': user_form,
                                                           'profile_form': profile_form,
                                                           'registered': registered})


def user_login(request):
    if request.method == 'POST':
        # get username and password provided by user
        # use request.POST.get('<variable>') as opposed to request.POST['<variable>']
        # because the former returns None if the value does not exist while
        # the latter will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # use Django's machinery to attempt to see if the username/password
        # combo is valid - a User object is returned if it is
        user = authenticate(username=username, password=password)

        # if we have a User object, the details are correct
        # if None, no user with matching credentials was found
        if user:
            # account could have been disabled
            if user.is_active:
                # if valid and active, log user in
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # inactive account - don't log user in
                return HttpResponse('Your Rango account is disabled.')
        else:
            # bad login details
            print(f'Invalid login details: {username}, {password}')
            return HttpResponse('Invalid login details supplied.')
    else:
        return render(request, 'rango/login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)

        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)


@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            cat = form.save(commit=True)
            print(cat, cat.slug)
            return redirect('/rango/')
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

