from django.contrib import admin

from fsm_admin.mixins import FSMTransitionMixin

from .models import (
    DestructionList,
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


@admin.register(DestructionList)
class DestructionListAdmin(FSMTransitionMixin, admin.ModelAdmin):
    list_display = ("name", "author", "assignee", "status")
    readonly_fields = ("status",)
    fsm_field = ["status"]
    inlines = [DestructionListItemInline, DestructionListReviewInline]


@admin.register(DestructionListItem)
class DestructionListItemAdmin(FSMTransitionMixin, admin.ModelAdmin):
    list_display = ("destruction_list", "zaak")
    readonly_fields = ("status",)
    fsm_field = ["status"]


class DestructionListItemReviewInline(admin.TabularInline):
    model = DestructionListItemReview
    fields = ("destruction_list_item", "text", "suggestion")
    extra = 1


@admin.register(DestructionListReview)
class DestructionListReviewAdmin(admin.ModelAdmin):
    list_display = ("destruction_list", "author")
    inlines = [DestructionListItemReviewInline]


@admin.register(DestructionListItemReview)
class DestructionListItemReviewAdmin(admin.ModelAdmin):
    list_display = ("destruction_list_review", "destruction_list_item")
