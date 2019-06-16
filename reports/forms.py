from django.contrib.auth.models import User
from django.forms import ModelForm, BooleanField, DateField, ModelChoiceField

from .models import Request, Campaign

class RequestAdminForm(ModelForm):
    approved = BooleanField(disabled=True)
    dt_approved = DateField(disabled=True)
    owner = ModelChoiceField(disabled=True, queryset=User.objects.all())

    class Meta:
        model = Request
        fields = '__all__'
        #exclude = ('owner', 'approved', 'dt_approved')


def label_for_request(request):
    # 1: {text} {similarity}
    return f"{request.id}: [{request.owner}] {request.text[:30]}"


class CampaignModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qset = Request.objects.filter(campaign__isnull=True)
        if 'instance' in kwargs:
            qset |= Request.objects.filter(campaign=kwargs['instance'])
        self.fields['request'].queryset = qset
        self.fields['request'].label_from_instance = label_for_request

    class Meta:
        model = Campaign
        exclude = ('id',)


