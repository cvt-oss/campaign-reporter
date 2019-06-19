import csv

from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpResponse
from django.utils.translation import gettext as _

from .forms import CampaignModelForm, RequestAdminForm
from .models import Code, Section, Request, Invoice, Campaign


class RequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'approved', 'dt_start', 'dt_end', 'dt_created')
    search_fields = ('id', 'text')
    list_filter = ('approved',)
    date_hierarchy = 'dt_created'
    form = RequestAdminForm

    fieldsets = (
        (_('Request'), {
            'fields': ('profile', 'link', 'text', 'dt_start', 'dt_end',
                       'budget', 'code', 'section', 'target_group',
                       'note', 'email')
        }),
        (_('Status'), {
            'fields': ('owner', 'approved', 'dt_approved')
        }),
    )


    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['form'] = ModelForm
        return super().get_form(request, obj, **kwargs)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return super().has_change_permission(request, obj)
        if obj and request.user == obj.owner and obj.approved:
            # read only for already approved requests
            return False
        return super().has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(RequestAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)


class CampaignAdmin(admin.TabularInline):
    model = Campaign
    max_num = 0
    min_num = 0
    form = CampaignModelForm


def get_report(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=report.csv'
    writer = csv.writer(response)
    writer.writerow([
        'Profile', 'Text', 'Start', 'End', 'Budget', 'Code', 'Section', 'Target group', 'Note',
        'Transaction ID', 'Name', 'Price', 'Request ID'])
    for invoice in queryset:
        for row in invoice.get_rows():
            writer.writerow(row)
    return response
get_report.short_description = _('Download excel report')


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'dt_payment', 'total')
    date_hierarchy = 'dt_payment'
    inlines = [CampaignAdmin]
    actions = [get_report]


class CodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    search_fields = ('name',)
    list_filter = ('active',)


admin.site.register(Request, RequestAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Code, CodeAdmin)
admin.site.register(Section, CodeAdmin)
