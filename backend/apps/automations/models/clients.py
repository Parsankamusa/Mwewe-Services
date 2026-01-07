from django.db import models


class Clients(models.Model):
    contract_id = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200, default="")
    contact_phone = models.CharField(max_length=200, default="")
    email = models.CharField(max_length=200, default="")
    region = models.CharField(max_length=200)
    branch_asoc = models.CharField(max_length=200)
    sub_contractor = models.CharField(max_length=200, null=True, default="")
    sub_contractor_alias = models.CharField(max_length=200, null=True, default="")
    site_id = models.CharField(max_length=200)
    premise_location = models.CharField(max_length=200)
    jobcard = models.CharField(max_length=200, null=True, default="")
    type_of_bins = models.CharField(max_length=200, null=True, default=None)
    quantity = models.IntegerField(null=True, default=None)
    sanitizers_quantity = models.IntegerField(null=True, default=None)
    urinal_mats_quantity = models.IntegerField(null=True, default=None)
    handsanitizers_quantity = models.IntegerField(null=True, default=None)
    frequency = models.CharField(max_length=200)
    contract_start_date = models.CharField(max_length=200)
    contract_end_date = models.CharField(max_length=200)
    services_required = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_inactive = models.BooleanField(default=False)
    is_prospect = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.contract_id

    class Meta:
        verbose_name_plural = "Clients"
        db_table = "clients"