from import_export import resources
from .models import FeatureData


class FeatureDataResource(resources.ModelResource):

    class Meta:
        model = FeatureData
        fields = ('id', 'date', 'value', 'site', 'variable')
