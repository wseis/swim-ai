from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = "ews"

urlpatterns=[
# List Views
path("bathingspots", login_required(views.BathingspotsView.as_view()), name="bathing_spots"),
path("sites", login_required(views.SitesView.as_view()), name="sites"),

# hsonne: why passing login_url?
path("", login_required(views.MlmodelsView.as_view(), login_url='login'), name="mlmodels"),

#authorization
#path("login", views.login_view, name="login"),
#path("logout", views.logout_view, name="logout"),
path("register", views.RegisterView.as_view(), name="register"),
path("broker", views.update_broker, name="broker"),

# create views

path("spot_create", login_required(views.SpotCreateView.as_view()), name="spot_create"),

path("model_config", login_required(views.ModelConfigView.as_view()), name="model_config"),

path("model_delete/<int:model_id>", views.delete_model, name="model_delete"),

# hsonne: login_required? decorator was missing above original model_edit()
path("model_edit/<int:model_id>", login_required(views.ModelEditView.as_view()), name="model_edit"),

path("add_site", login_required(views.AddSiteView.as_view()), name="add_site"),
path("site_delete/<int:site_id>", views.delete_site, name="site_delete"),
path("site_detail/<int:site_id>", views.site_detail, name="site_detail"),

path("selectarea_create", login_required(views.SelectareaCreateView.as_view()), name="selectarea_create"),

path("data_delete_all/<int:site_id>", views.data_delete_all, name="data_delete_all" ),
# ??
path("detail/<int:spot_id>", login_required(views.DetailView.as_view()), name = "detail"),
path("file_upload/<int:site_id>", login_required(views.FileUploadView.as_view()), name="file_upload"),
path('model_fit/<int:model_id>', views.model_fit, name ='model_fit'),
path('prediction_switch/<int:model_id>', views.prediction_switch, name ='prediction_switch'),

# hsonne: What is the difference between import_new_data and add_data?
path('import_new_data/<str:slug>', csrf_exempt(views.ImportNewDataView.as_view()), name = "import_new_data"),

# added by hsonne
path('add_data', login_required(views.AddDataView.as_view()), name = "add_data"),

path('api-get-predictions/<int:model_id>', views.api_get_predictions, name = "api_get_predictions"),
path('api-get-broker-urls/<int:model_id>', views.api_get_broker_urls, name = "api_get_broker_urls")

]