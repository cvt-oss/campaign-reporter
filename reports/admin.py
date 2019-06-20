import csv

from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpResponse
from django.utils.translation import gettext as _

from .forms import CampaignModelForm, RequestAdminForm
from .models import Code, Section, Request, Invoice, Campaign


class WithCampaignFilter(admin.SimpleListFilter):
    title = _('with campaign')
    parameter_name = 'with_campaign'

    def lookups(self, request, model_admin):
        return (
            ('with', _('With campaign')),
            ('without', _('Without campaign')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'with':
            return queryset.filter(campaign__isnull=False)
        elif self.value() == 'without':
            return queryset.filter(campaign__isnull=True)


class RequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'approved', 'dt_start', 'dt_end', 'dt_created', 'get_invoice')
    search_fields = ('id', 'text')
    list_filter = ('approved', WithCampaignFilter)
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

    def get_invoice(self, obj):
        if obj.campaign:
            return obj.campaign.invoice
        else:
            return None
    get_invoice.short_description = _('Invoice')

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
    can_delete = False


def get_report(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=report.csv'
    writer = csv.writer(response)
    writer.writerow([
        'Transaction ID', 'Name', 'Price'
        'Profile', 'Text', 'Start', 'End', 'Budget', 'Code', 'Section', 'Target group', 'Note'])
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
