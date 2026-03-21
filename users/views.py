from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import MyLogInForm, ProfileUpdateForm, UserRegisterForm, UserUpdateForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f' Your account has been created! Your now able to log in', extra_tags='text-center')
            return redirect('login')
    else:

        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):

    # populate form input values
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        # restrict to edit 'test user' profile
        if str(request.user) == 'testuser':
            messages.warning(request, f'You are not authorized to edit this profile. ', extra_tags='exclamation')
            return redirect('profile')

        # if Valid form entries, update form(username, email or image profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            if request.user.is_authenticated:
                messages.success(request, f' Your account has been updated', extra_tags='check')
            return redirect('profile')  # prevent the browser's msg of resubmitting when reloading, i.e, 'POST-GET redirect pattern'

    else:
        # instantiate UserUpdateForm & ProfileUpdateForm class and sent value to template
        user_form = UserUpdateForm(instance=request.user)  # "instance=request.user" will populate the username and email in profile form
        profile_form = ProfileUpdateForm(instance=request.user.profile)  # "instance=request.user.profile" will populate the images profile form

    context = {
        'dropdown_arrow': 'down',
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'users/profile.html', context)


class MyLoginView(LoginView):
    authentication_form = MyLogInForm
