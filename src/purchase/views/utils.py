from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class ProtectedViewsMixin(PermissionRequiredMixin, LoginRequiredMixin):
    pass
