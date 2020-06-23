from django.db import models

from rma.accounts.models import User


class DestructionListQuerySet(models.QuerySet):
    def reviewed_by(self, user: User):
        from .models import DestructionListReview

        reviewed = DestructionListReview.objects.filter(author=user).values(
            "destruction_list_id"
        )
        return self.filter(id__in=models.Subquery(reviewed))
