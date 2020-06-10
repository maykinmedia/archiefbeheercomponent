from django.views.generic import ListView

from .models import DestructionList


class RecordManagerDestructionListView(ListView):
    """ data for user who can start destruction lists"""

    template_name = "destruction/recordmanager_list.html"

    def get_queryset(self):
        return DestructionList.objects.filter(author=self.request.user).order_by("-id")
