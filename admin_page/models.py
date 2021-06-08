from django.db import models

# Create your models here.


class AdminCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    url = models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        db_table = 'admin_category'