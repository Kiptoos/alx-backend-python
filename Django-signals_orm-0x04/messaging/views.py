from django.contrib.auth.decorators import login_required
from django.contrib import messages as dj_messages
from django.shortcuts import redirect, render
@login_required
def delete_user(request):
    if request.method == "POST":
        user = request.user
        username = user.get_username()
        user.delete()
        dj_messages.success(request, f"Account '{username}' deleted successfully.")
        return redirect("admin:index")
    return render(request, "messaging/confirm_delete.html")
