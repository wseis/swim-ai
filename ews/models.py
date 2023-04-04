from django.contrib.auth.models import User
from django.db import models
from djgeojson.fields import PointField
from djgeojson.fields import PolygonField
import unidecode


# BathingSpot
class BathingSpot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="bathing_spots")
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=200,
                                   default=" ")

    def __str__(self):
        return f"{self.name}"


# FeatureType
class FeatureType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


# Site
class Site(models.Model):
    name = models.CharField(max_length=64, unique=True)
    ref_name = models.CharField(max_length=64, null=True)
    geom = PointField(null=True)
    image = models.URLField(default=("http://die-erfolgskomplizen.de/"
                                     "wp-content/uploads/2018/02/bild-"
                                     "platzhalter-300x200px.gif"),
                            null=True)
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name="owner")
    feature_type = models.ForeignKey(FeatureType,
                                     on_delete=models.CASCADE,
                                     related_name="feature_type")
    random_string = models.CharField(max_length=50)
    broker_type = models.CharField(max_length=250)
    subscription_id = models.CharField(max_length=250)

    def get_broker_id(self):
        return "urn:ngsi-ld:{}:{}:{}".format(
            self.broker_type, self.id, unidecode.unidecode(self.name))

    def get_subscription_url(self):
        return "urn:ngsi-ld:{}:{}:{}{}".format(
            self.broker_type, self.id, self.name, self.random_string
        )

    def __str__(self):
        return f"{self.name.replace('_', ' ').capitalize()}"

    @property
    def popupContent(self):
        return '<a href="/detail/{}"><strong>{}</strong></a> <p>{}</p>'.format(
            self.id,
            self.name.replace('_', ' ').capitalize(),
            self.feature_type
        )

    @property
    def SiteType(self):
        return '{}'.format(self.feature_type)


# Unit
class Unit(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"


# Variable
class Variable(models.Model):
    name = models.CharField(max_length=255, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    abbreviation = models.CharField(max_length=6, null=True)
    description = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.name}"


# Method
class Method(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    link = models.URLField(null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        unique_together = ['name']


# FeatureData
class FeatureData(models.Model):
    date = models.DateTimeField("date")
    value = models.FloatField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE,
                             related_name="site")
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE,
                                 null=True,
                                 related_name="variable")
    method = models.ForeignKey(Method, on_delete=models.CASCADE,
                               null=True,
                               related_name="method")

    class Meta:
        unique_together = ('date', 'site', 'value', 'method')

    def __str__(self):
        return f"{self.site.name, self.variable, self.date, self.value }"


# SelectArea
class SelectArea(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             default=1, related_name="areas")
    name = models.CharField(max_length=64, unique=True)
    geom = PolygonField()
    feature_type = models.ForeignKey(FeatureType,
                                     on_delete=models.CASCADE,
                                     related_name="areas")

    @property
    def SiteType(self):
        return '{}'.format(self.feature_type)

    def __str__(self):
        return f"{self.name}"


# PredictionModel
class PredictionModel(models.Model):
    name = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="models")
    site = models.ManyToManyField(Site, related_name="models")
    area = models.ManyToManyField(SelectArea,
                                  related_name="models")
    fit = models.BinaryField(null=True)
    predict = models.BooleanField(default=False)
    algorithm = models.CharField(default="Random Forest",
                                 blank=True, max_length=100)

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_model_by_id_or_none(cls, model_id):
        try:
            model = cls.objects.get(pk=model_id)
        except cls.DoesNotExist:
            return None
        return model


# Prediction
class Prediction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    date_predicted = models.DateTimeField()
    model = models.ForeignKey(PredictionModel, on_delete=models.CASCADE)
    p2_5 = models.FloatField()
    p50 = models.FloatField()
    p90 = models.FloatField()
    p95 = models.FloatField()
    p97_5 = models.FloatField()
    classification = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.model}"


class EmailAlert(models.Model):
    start_time = models.DateTimeField()
    trigger_time = models.DateTimeField()
    target =  models.CharField(max_length=50)
    catchment =  models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.model}"

    