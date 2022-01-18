from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from fsm_admin.mixins import FSMTransitionMixin
from ordered_model.admin import OrderedModelAdmin
from solo.admin import SingletonModelAdmin

from .forms import ArchiveConfigForm, get_zaaktype_choices
from .models import (
    ArchiveConfig,
    DestructionList,
    DestructionListAssignee,
    DestructionListItem,
    DestructionListItemReview,
    DestructionListReview,
    DestructionListReviewComment,
    StandardReviewAnswer,
)


class DestructionListItemInline(admin.TabularInline):
    model = DestructionListItem
    fields = ("zaak", "status")
    readonly_fields = ("status",)
    extra = 1


class DestructionListReviewInline(admin.TabularInline):
    model = DestructionListReview
    fields = ("author", "text", "status")
    extra = 1


class DestructionListAssigneeInline(admin.TabularInline):
    model = DestructionListAssignee
    fields = ("assignee", "order")
    extra = 1


@admin.register(DestructionList)
class DestructionListAdmin(FSMTransitionMixin, admin.ModelAdmin):
    list_display = ("name", "author", "assignee", "status")
    readonly_fields = ("status",)
    fsm_field = ("status",)
    search_fields = ("name",)
    list_filter = ("status",)
    date_hierarchy = "created"
    raw_id_fields = ("author", "assignee")
    inlines = (
        DestructionListItemInline,
        DestructionListReviewInline,
        DestructionListAssigneeInline,
    )


@admin.register(DestructionListItem)
class DestructionListItemAdmin(FSMTransitionMixin, admin.ModelAdmin):
    list_display = ("destruction_list", "zaak")
    readonly_fields = ("status",)
    fsm_field = ("status",)
    search_fields = ("zaak",)
    list_filter = ("status",)
    raw_id_fields = ("destruction_list",)


class DestructionListItemReviewInline(admin.TabularInline):
    model = DestructionListItemReview
    fields = ("destruction_list_item", "text", "suggestion")
    extra = 1


@admin.register(DestructionListReview)
class DestructionListReviewAdmin(admin.ModelAdmin):
    list_display = ("destruction_list", "author")
    raw_id_fields = ("destruction_list", "author")
    date_hierarchy = "created"
    inlines = (DestructionListItemReviewInline,)


@admin.register(DestructionListReviewComment)
class DestructionListReviewCommentAdmin(admin.ModelAdmin):
    list_display = ("review", "created")
    readonly_fields = ("review", "created", "text")
    search_fields = ("review",)
    list_filter = ("review",)
    date_hierarchy = "created"
    raw_id_fields = ("review",)


@admin.register(DestructionListItemReview)
class DestructionListItemReviewAdmin(admin.ModelAdmin):
    list_display = ("destruction_list_review", "destruction_list_item")
    raw_id_fields = ("destruction_list_review", "destruction_list_item")
    list_filter = ("suggestion",)
    search_fields = ("destruction_list_item__zaak",)


@admin.register(DestructionListAssignee)
class DestructionListAssigneeAdmin(admin.ModelAdmin):
    list_display = ("destruction_list", "assignee")
    raw_id_fields = ("destruction_list", "assignee")


@admin.register(ArchiveConfig)
class ArchiveConfigAdmin(SingletonModelAdmin):
    change_form_template = "destruction/admin/change_solo_form.html"
    form = ArchiveConfigForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "archive_date",
                    "short_review_zaaktypes",
                    "link_to_zac",
                    "days_until_reminder",
                )
            },
        ),
        (
            _("Optional destruction case settings"),
            {
                "fields": (
                    "create_zaak",
                    "source_organisation",
                    "case_type",
                    "status_type",
                    "result_type",
                    "document_type",
                    "destruction_report_downloadable",
                ),
            },
        ),
    )

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if not extra_context:
            extra_context = {}

        extra_context.update({"zaaktypen": get_zaaktype_choices()})

        response = super().changeform_view(request, object_id, form_url, extra_context)
        return response


@admin.register(StandardReviewAnswer)
class StandardReviewAnswerAdmin(OrderedModelAdmin):
    list_display = ("reason", "move_up_down_links")
