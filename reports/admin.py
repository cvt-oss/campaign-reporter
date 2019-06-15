from django.contrib import admin

from .models import Code, Section, Request, Invoice, Campaign


class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'approved')
    list_filter = ('approved',)


class CampaignAdmin(admin.TabularInline):
    model = Campaign
    max_num = 0
    min_num = 0


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'dt_payment', 'total')
    date_hierarchy = 'dt_payment'
    inlines = [CampaignAdmin]


admin.site.register(Request, RequestAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Code)
admin.site.register(Section)
