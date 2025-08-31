from django.db import models


class Manufacturer(models.Model):
    name = models.CharField(null=True, max_length=50)
    address = models.CharField(null=True, max_length=200)
    contact_email = models.EmailField(null=True, max_length=50)

    def __repr__(self):
        return f"{self.name}"

class Medication(models.Model):
    name = models.CharField(null=False, max_length=100)
    manufacturer = models.ForeignKey(to=Manufacturer, null=True, on_delete=models.SET_NULL)
    description = models.TextField(null=True)

    def __repr__(self):
        return f"{self.name}, produced by: {self.producer}, {len(self.description)}"

