from import_export import resources, fields
from .models import  Site, BathingSpot, FeatureData
from import_export.widgets import ForeignKeyWidget
#from django.contrib.auth.models import User
import datetime

class FeatureDataResource(resources.ModelResource):

    class Meta:
        model = FeatureData
        fields = ('id', 'date', 'value','site', 'variable')