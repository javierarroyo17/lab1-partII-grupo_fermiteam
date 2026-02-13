from decimal import Decimal
from rest_framework import serializers
from ..models import Provider, Barrel, Invoice, InvoiceLine


class ProviderSerializer(serializers.ModelSerializer):
    billed_barrels = serializers.SerializerMethodField()
    barrels_to_bill = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = [
            "id",
            "name",
            "address",
            "tax_id",
            "billed_barrels",
            "barrels_to_bill",
        ]

    def get_billed_barrels(self, obj):
        return list(
            Barrel.objects
            .filter(provider=obj, billed=True)
            .values_list("id", flat=True)
        )

    def get_barrels_to_bill(self, obj):
        return list(
            Barrel.objects
            .filter(provider=obj, billed=False)
            .values_list("id", flat=True)
        )


class BarrelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barrel
        fields = ["id", "provider", "number", "oil_type", "liters", "billed"]


class InvoiceLineNestedSerializer(serializers.ModelSerializer):
    barrel_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = InvoiceLine
        fields = ["id", "barrel_id", "liters", "description", "unit_price"]


class InvoiceLineCreateSerializer(serializers.Serializer):
    barrel = serializers.PrimaryKeyRelatedField(queryset=Barrel.objects.all())
    liters = serializers.IntegerField(min_value=1)
    description = serializers.CharField(max_length=255)
    unit_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    def create(self, validated_data: dict) -> InvoiceLine:
        invoice = self.context["invoice"]
        return invoice.add_line_for_barrel(
            barrel=validated_data["barrel"],
            liters=validated_data["liters"],
            unit_price_per_liter=validated_data["unit_price"],
            description=validated_data["description"],
        )


class InvoiceSerializer(serializers.ModelSerializer):
    lines = InvoiceLineNestedSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ["id", "invoice_no", "issued_on", "lines", "total_amount"]

    def get_total_amount(self, obj: Invoice) -> Decimal:
        total = Decimal("0.00")
        for line in obj.lines.all():
            total += Decimal(line.liters) * line.unit_price
        return total
