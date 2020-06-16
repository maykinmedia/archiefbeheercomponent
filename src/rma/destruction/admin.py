from django.contrib import admin

from fsm_admin.mixins import FSMTransitionMixin

from .models import (
    DestructionList,
    DestructionListAssignee,
    DestructionListItem,
    DestructionListItemReview,
    DestructionListReview,
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
