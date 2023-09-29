from django.contrib import admin
from .models import CarMake, CarModel

class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 1  # Number of empty forms to display for adding new CarModel instances

class CarMakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    inlines = [CarModelInline]  # Add the CarModelInline class here

class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_make', 'car_type', 'year', 'dealer_id')
    list_filter = ('car_make', 'car_type', 'year')
    search_fields = ('name', 'car_make__name', 'dealer_id')

admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)