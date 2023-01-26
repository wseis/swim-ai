from ews.models import BathingSpot, Site, FeatureData, FeatureType, PredictionModel, Prediction
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit
from djgeojson.fields import PointField, MultiPolygonField
from leaflet.forms.widgets import LeafletWidget
from .models import SelectArea

class BathingSpotForm(forms.ModelForm):
    def __init__(self,  *args, **kwargs):
        super(BathingSpotForm, self).__init__(*args, **kwargs)
        self.fields['name'].help_text = "Please enter the name of the bathing spot / bathing area"
        self.fields['image'].help_text = "you can provide a URL to a picture of the bathing spot"
        self.fields['feature_type'].empty_label = None
        self.fields['feature_type'].help_text = "This field has a default value"
        self.fields['feature_type'].queryset = FeatureType.objects.filter(name = "BathingSpot")
        #self.fields['feature_type'].type = "hidden"
        #self.fields['bathing_spot'].queryset = BathingSpot.objects.filter(user = user)
        
        self.helper = FormHelper()
    
    class Meta:
        model = Site
        fields=[ "name",  "geom", "image", "feature_type"]
        widgets={'geom': LeafletWidget()}


class SiteForm(forms.ModelForm): 
    def __init__(self,  *args, **kwargs):
   
        super(SiteForm, self).__init__(*args, **kwargs)
        self.fields['name'].help_text = "Please enter the name of the predictor variable"
        #self.fields['image'].help_text = "you can provide a URL to a picture of the bathing spot"
        self.fields['feature_type'].empty_label = None
        self.fields['feature_type'].help_text = "Please select feature type"
        self.fields['feature_type'].queryset = FeatureType.objects.exclude(name = "BathingSpot")
        #self.fields['bathing_spot'].queryset = BathingSpot.objects.filter(user = user)
        self.fields['geom'].label = "<strong> Select location </strong>"
        self.fields['feature_type'].label = "<strong> Define which type of variable data the site provides </strong>"
        self.fields['name'].label = "<strong> Give the site an explanatory name </strong>"
        
        self.helper = FormHelper()
    class Meta:
        model = Site
        fields=[ "name",  "geom", "feature_type"]
        widgets={'geom': LeafletWidget()}


class FeatureDataForm(forms.ModelForm):
    class Meta:
        model = FeatureData
        fields=["date", "value", "site"]

class PredictionModelForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(PredictionModelForm, self).__init__(*args, **kwargs)
        self.fields['area'].help_text = "Please select the areas you've created, which you want to use to model calibration"
        self.fields['area'].label = "<strong> Select features from defined feature groups </strong>"
        self.fields['site'].label = "<strong> Select a bathing spot for which the model should be calibrated </strong>"
        self.fields['name'].label = "<strong> Give the model an explanatory name </strong>"
        
        self.fields['site'].empty_label = None
        #self.fields['bathing_spot'].empty_label = None
        self.fields['site'].help_text = "Please select the bathing water for which you want to create a prediction model"
        self.fields['site'].queryset = Site.objects.filter(owner = user, feature_type__in= FeatureType.objects.filter(name = "BathingSpot"))
        self.fields['area'].queryset = SelectArea.objects.filter(user = user)
        self.fields['area'].required = True        
        #self.fields['bathing_spot'].queryset = BathingSpot.objects.filter(user = user)
        
        #self.helper = FormHelper()
    class Meta:
        model =  PredictionModel
        fields=[ "site", "area","name"]
        widgets={"area": forms.CheckboxSelectMultiple()}




class PredictionModelForm2(forms.Form):
    name=forms.CharField(label="Enter a informative name")
    bathing_spot=forms.ModelChoiceField(queryset= BathingSpot.objects.all())
    rain_site = forms.ModelMultipleChoiceField(queryset=Site.objects.all())
    flow_site = forms.ModelMultipleChoiceField(queryset=Site.objects.all())

    def __init__(self, user, *args, **kwargs):
        super(PredictionModelForm2, self).__init__(*args, **kwargs)
        self.fields['rain_site'].queryset = Site.objects.filter(owner = user, feature_type = 1)
        self.fields['flow_site'].queryset = Site.objects.filter(owner = user, feature_type = 4)
        self.fields['bathing_spot'].queryset = BathingSpot.objects.filter(user = user)
        self.helper = FormHelper()


class SelectAreaForm(forms.ModelForm):

    class Meta:
        model = SelectArea
        fields = ('name', 'geom', 'feature_type')
        widgets = {'geom': LeafletWidget()}


class DateInput(forms.DateInput):
    input_type = 'date'

class PredictionForm(forms.ModelForm):
    
    class Meta:
        model = Prediction
        fields = ('date_predicted', )
    
        widgets = {
                'date_predicted': DateInput(),
            }