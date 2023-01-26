from django.contrib.gis import admin
from .models import BathingSpot, Site, Method, Unit, FeatureData,  FeatureType, PredictionModel, SelectArea, Variable, Prediction
from import_export.admin import ImportExportModelAdmin
from leaflet.admin import LeafletGeoAdmin
from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdminMixin


@admin.register(FeatureData)
class featuredataAdmin(ImportExportModelAdmin):
    list_display=("id", "date", "value", "site", "variable", "method")



@admin.register(Method)
class featuredataAdmin(ImportExportModelAdmin):
    list_display=("id", "name")


@admin.register(Unit)
class featuredataAdmin(ImportExportModelAdmin):
    list_display=("id", "name")


#@admin.register(Bathing)
class BathingSpotAdmin(admin.ModelAdmin):
    list_display=("id", "name", "user")

   

class FeatureTypeAdmin(admin.ModelAdmin):
    list_display=("id", "name")

    

#class SiteAdmin(admin.ModelAdmin):
 #   list_display=("id", "name", "owner", "feature_type")

  #  pass
#admin.site.register(Site, LeafletGeoAdmin)
class SiteAdmin(LeafletGeoAdmin):
    list_display=("id", "name", "feature_type")


class ProfileAdmin(admin.ModelAdmin):
    list_display=("id", "user")


class SelectAreaAdmin(LeafletGeoAdmin):
    list_display=("id", "name", "feature_type")

@admin.register(Prediction)
class predictionAdmin(admin.ModelAdmin):
    list_display=("id", "created_at", "date_predicted",  "classification")

#admin.site.register(Prediction,PredictionAdmin)

admin.site.register(BathingSpot,BathingSpotAdmin)
admin.site.register(Site, SiteAdmin)
#admin.site.register(Profile, ProfileAdmin)
admin.site.register(Variable)
admin.site.register(SelectArea, SelectAreaAdmin)
admin.site.register(PredictionModel)
admin.site.register(FeatureType, FeatureTypeAdmin)
#admin.site.register(Method)
