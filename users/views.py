from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from webscraping.constants import DEMO_READ_ONLY_USERNAME

from .forms import MyLogInForm, ProfileUpdateForm, UserRegisterForm, UserUpdateForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Your account has been created. You can now log in.',
                extra_tags='text-center',
            )
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        # Keep the seeded demo account read-only.
        if request.user.get_username() == DEMO_READ_ONLY_USERNAME:
            messages.warning(
                request,
                'You are not authorized to edit this profile.',
                extra_tags='exclamation',
            )
            return redirect('profile')

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(
                request,
                'Your account has been updated.',
                extra_tags='check',
            )
            # POST-Redirect-GET prevents duplicate submissions on refresh.
            return redirect('profile')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'dropdown_arrow': 'down',
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'users/profile.html', context)


class MyLoginView(LoginView):
    authentication_form = MyLogInForm
