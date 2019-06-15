from rest_framework import serializers
from .models import Request, Invoice, Campaign


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'


class ImportPdfSerializer(serializers.Serializer):
    invoice_id = serializers.IntegerField(min_value=1)


class CampaignSerializer(serializers.Serializer):
    campaignName = serializers.CharField(max_length=100)
    price = serializers.FloatField(min_value=0)


class InputInvoiceSerializer(serializers.Serializer):
    transactionId = serializers.CharField(max_length=40)
    paidOn = serializers.DateTimeField()
    totalPaid = serializers.FloatField()
    invoiceItems = CampaignSerializer(many=True)

    def create(self, validated_data):
        invoice = Invoice.objects.create(
            transaction_id=validated_data['transactionId'],
            dt_payment=validated_data['paidOn'],
            total=validated_data['totalPaid'])
        campaigns = [
            Campaign(invoice=invoice, name=item['campaignName'], price=item['price'])
            for item in validated_data['invoiceItems']
        ]
        Campaign.objects.bulk_create(campaigns)
        return invoice

    def update(self, instance, validated_data):
        instance.dt_payment = validated_data['paidOn']
        instance.total = validated_data['totalPaid']
        instance.save()

        instance.campaigns.all().delete()
        campaigns = [
            Campaign(invoice=instance, name=item['campaignName'], price=item['price'])
            for item in validated_data['invoiceItems']
        ]
        Campaign.objects.bulk_create(campaigns)

        return instance


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ('name', 'price', 'requests')


class InvoiceSerializer(serializers.ModelSerializer):
    campaigns = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'
