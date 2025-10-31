from django.contrib import admin
from .models import Category, Task
from django.utils import timezone
from datetime import timedelta


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("category_id", "category_name", "user")
	search_fields = ("category_name",)
	list_filter = ("user",)


class WeekFilter(admin.SimpleListFilter):
	title = "Week"
	parameter_name = "week"

	def lookups(self, request, model_admin):
		return (
			("this", "This week"),
			("last", "Last week"),
			("next", "Next week"),
		)

	def queryset(self, request, queryset):
		value = self.value()
		if not value:
			return queryset
		today = timezone.localdate()
		start = today - timedelta(days=today.weekday())  # Monday
		if value == "this":
			end = start + timedelta(days=6)
		elif value == "last":
			start = start - timedelta(days=7)
			end = start + timedelta(days=6)
		elif value == "next":
			start = start + timedelta(days=7)
			end = start + timedelta(days=6)
		else:
			return queryset
		return queryset.filter(date__gte=start, date__lte=end)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = (
		"task_id",
		"task_name",
		"user",
		"category",
		"priority",
		"status",
		"deadline_date",
		"date",
		"hour",
	)
	search_fields = ("task_name", "description")
	list_filter = (WeekFilter, "priority", "status", "category", "user")
	date_hierarchy = "date_created"
	ordering = ("-date_created",)
