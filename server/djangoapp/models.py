from django.db import models
from django.utils.timezone import now


# Create your models here.

class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    # You can add other fields here as needed, for example:
    # year_founded = models.PositiveIntegerField()
    # headquarters = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    dealer_id = models.IntegerField()
    name = models.CharField(max_length=100)
    
    CAR_TYPES = (
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('WAGON', 'WAGON'),
        # Add more choices as needed
    )
    car_type = models.CharField(max_length=10, choices=CAR_TYPES)
    year = models.DateField()
    
    # You can add any other fields you need here
    
    def __str__(self):
        return f"{self.car_make.name} - {self.name}"
        

# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
