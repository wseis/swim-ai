import datetime
import json
import logging
import numpy
import pandas
import pickle
import uuid

from dateutil import parser
from decouple import config
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import IntegrityError
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_pandas.io import read_frame
from ews.tasks import contextBroker
from pprint import pformat
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from skranger.ensemble import RangerForestRegressor

from .forms import BathingSpotForm
from .forms import FeatureDataForm
from .forms import PredictionForm
from .forms import PredictionModelForm
from .forms import SelectAreaForm
from .forms import SiteForm

from .helper_classes.KRock import KRock
from .helper_classes.KRock import KRockError
from .helper_classes.CBroker import CBroker

from .helper_functions import create_daily_lagvars
from .helper_functions import get_feature_type_named
from .helper_functions import get_site_urls
from .helper_functions import import_data_from_model
from .helper_functions import json_response_error
from .helper_functions import json_response_status
from .helper_functions import predict_daterange
from .helper_functions import redirect_reverse

from .messages import Message

from .models import FeatureData
from .models import PredictionModel
from .models import SelectArea
from .models import Site
from .models import User

from .plot import get_plot_specification_details
from .plot import create_barplot_feature_data_1
from .plot import create_barplot_feature_data_2
from .plot import create_barplot_importances
from .plot import create_scatter_plot_model_fit

# Obtain a logger instance
logger = logging.getLogger('debug')


def http_response_form_not_valid(form):
    formatted_errors = pformat(form.errors)
    logger.debug("Form is not valid: " + formatted_errors)
    return HttpResponse(Message.FORM_NOT_VALID + formatted_errors)
    # return HttpResponse(Message.SUBMISSION_FAILED)


class BathingspotsView(View):

    def get(self, request):

        # Initialise array of entries
        entries = []

        # Try to get the feature type (returns None in case of db exception)
        feature_name = 'BathingSpot'
        feature_type = get_feature_type_named(feature_name)

        if feature_type is None:
            message = Message.ERROR_NO_FEATURE_TYPE_NAMED.format(feature_name)
        else:
            try:
                entries = Site.objects.filter(owner=request.user,
                                              feature_type=feature_type)
                message = Message.NO_BATHING_SPOTS
            except Site.DoesNotExist:
                message = Message.ERROR_QUERYING_BATHING_SPOTS

        return render(request, 'ews/index.html', {
            'entries': entries,
            'message': message
        })


def update_broker(request):
    x = contextBroker()
    return HttpResponse(Message.IT_WORKED + ': ' + pformat(x))


class SitesView(View):

    def get(self, request):
        return render(request, 'ews/sites.html', {
            'entries': Site.objects.filter(owner=request.user)
            # item': 'spot'
        })


class MlmodelsView(View):

    def get(self, request):
        return render(request, 'ews/models.html', {
            'entries': PredictionModel.objects.filter(user=request.user)
        })


class ModelConfigView(View):

    def post(self, request):

        logger.debug("Entering ModelConfigView::post()")
        form = PredictionModelForm(request.user, request.POST)

        if not form.is_valid():
            return http_response_form_not_valid(form)

        pmodel = PredictionModel()
        pmodel.user = request.user
        pmodel.name = form.cleaned_data['name']
        # pmodel.bathing_spot=form.cleaned_data['bathing_spot']
        pmodel.save()
        pmodel.site.set(form.cleaned_data['site'])
        pmodel.area.set(form.cleaned_data['area'])
        pmodel.save()

        CBroker.post_water_quality_predicted(pmodel.id, pmodel.name)

        return redirect_reverse('ews:mlmodels')

    def get(self, request):

        logger.debug("Entering ModelConfigView::get()")
        return render(request, 'ews/model_config.html', {
            'pmodel_form': PredictionModelForm(request.user)
        })


class ModelEditView(View):

    # hsonne: is "get" the correct request method? There was no distinction.
    def get(self, request, model_id):
        model = PredictionModel.objects.get(id=model_id)
        return render(request, 'ews/sites.html', {
            'entries': model.site.all(),
            'areas': model.area.all()
        })


class SpotCreateView(View):

    def post(self, request):

        logger.debug("Entering SpotCreateView::post()")
        form = BathingSpotForm(request.POST)

        if not form.is_valid():
            return http_response_form_not_valid(form)

        spot = Site()
        spot.name = form.cleaned_data['name']
        spot.geom = form.cleaned_data['geom']
        spot.image = form.cleaned_data['image']
        spot.owner = request.user
        spot.feature_type = form.cleaned_data['feature_type']
        spot.save()

        return redirect_reverse('ews:bathing_spots')

    def get(self, request):

        logger.debug("Entering SpotCreateView::get()")
        return render(request, 'ews/create.html', {'form': BathingSpotForm()})


class DetailView(View):

    def post(self, request, spot_id):
        # feature_resource = FeatureDataResource()
        # dataset = Dataset()
        new_data = request.FILES['myfile']
        file_data = pandas.read_csv(new_data)

        for index, row in file_data.iterrows():
            data_dict = {
                'date': row['date'],
                'value': row['value'],
                'site': spot_id
            }
            try:
                form = FeatureDataForm(data_dict)
                if form.is_valid():
                    form.save()
            except Exception as e:
                HttpResponse(print(e))

        return redirect_reverse('ews:detail', args=[spot_id,])

    def get(self, request, spot_id):
        entries = Site.objects.get(id=spot_id)

        models = PredictionModel.objects\
            .filter(site=Site.objects.get(id=spot_id))

        feature_data = FeatureData.objects.filter(site_id=spot_id)
        fig = create_barplot_feature_data_1(
            df=read_frame(feature_data),
            labelpoint=feature_data.first(),
            spec=get_plot_specification_details('barplot_feature_data_1')
        )
        return render(request, 'ews/detail.html', {
            'entries': entries,
            'models': models,
            'fig': fig,
            'bathingspot': entries.feature_type.name == 'BathingSpot'
            # 'sites': sites
        })


class AddSiteView(View):

    def post(self, request):
        logger.debug('Entering AddSiteView::post()')
        form = SiteForm(request.POST)
        # form.owner=request.user
        if not form.is_valid():
            return http_response_form_not_valid(form)

        logger.debug('The form is valid.')
        logger.debug('')

        new_site = Site()
        new_site.name = form.cleaned_data['name']
        new_site.feature_type = form.cleaned_data['feature_type']
        new_site.geom = form.cleaned_data['geom']
        new_site.owner = request.user
        new_site.random_string = uuid.uuid4().hex[:40]

        # Determine the broker type from the name of the feature type and
        # set the broker type in the site object
        broker_type = CBroker\
            .feature_type_to_broker_type(new_site.feature_type.name)
        new_site.broker_type = broker_type

        # Save the site object. Only now we have an id for the site object.
        # This object id is required for the broker id
        new_site.save()
        logger.debug('new_site was saved.')

        # Get and show the broker id
        broker_id = new_site.get_broker_id()
        subscription_url = new_site.get_subscription_url()
        logger.debug("broker_id: {}".format(broker_id))

        if broker_type == 'WaterObserved':
            CBroker.post_water_observed(broker_id, broker_type)
            x = CBroker.subscribe_water_observed(broker_id,
                                             broker_type,
                                             subscription_url)
        elif new_site.feature_type.name in ['Rainfall']:
            broker_type = 'WeatherObserved'
            CBroker.post_weather_observed(broker_id, broker_type)
            x = CBroker.subscribe_weather_observed(broker_id,
                                               broker_type,
                                               subscription_url)
        else:
            broker_type = 'WaterQualityObserved'
            CBroker.post_water_quality_observed(broker_id, broker_type)
            x = CBroker.subscribe_water_quality_observed(broker_id,
                                                     broker_type,
                                                     subscription_url)
        # df = pandas.json_normalize(CBroker.get_subscriptions().json())
        # new_site.subscription_id = df.loc[df.description == broker_id]\
         #   .id.to_string().split(' ')[-1]
         
        new_site.subscription_id = x.headers["location"].split("/")[-1]
        new_site.save()
        
        KRock.create_and_assign_permissions(
            app_id=config('APP_ID'),
            broker_id=broker_id,
            resource=CBroker.lookup_url('rel_broker_attributes',
                                        broker_id=broker_id),
            resource_owner=new_site.owner.username
        )
        
        return redirect_reverse('ews:sites')

    def get(self, request):
        logger.debug("Entering AddSiteView::get()")
        return render(request, 'ews/add_site.html', {
            'form': SiteForm()})


def delete_site(request, site_id):
    site = Site.objects.get(id=site_id)
    ft = site.feature_type
    CBroker.delete_broker(broker_id=site.get_broker_id())
    CBroker.delete_subscription(subscription_id=site.subscription_id)
    site.delete()

    if ft == get_feature_type_named('BathingSpot'):
        return redirect_reverse('ews:bathing_spots')

    return redirect_reverse('ews:sites')


def delete_model(request, model_id):
    model = PredictionModel.objects.get(id=model_id)

    CBroker.delete_water_quality(model_id=model.id, model_name=model.name)

    model.delete()
    return redirect_reverse('ews:mlmodels')


def data_delete_all(request, site_id):
    FeatureData.objects.filter(site=Site.objects.get(id=site_id)).delete()
    return redirect_reverse('ews:detail', args=[site_id,])


class AddDataView(View):

    def post(self, request):
        form = FeatureDataForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect_reverse('ews:add_site')

    def get(self, request):
        return render(request, 'ews/add_data.html', {
            'form': FeatureDataForm()
        })


class FileUploadView(View):

    def post(self, request, site_id):

        new_data = request.FILES['myfile']
        file_data = pandas.read_csv(new_data)

        for index, row in file_data.iterrows():
            data_dict = {
                'date': row['date'],
                'value': row['value'],
                'site': site_id
            }

            try:
                form = FeatureDataForm(data_dict)
                if form.is_valid():
                    form.save()
            except Exception as e:
                HttpResponse(print(e))

        return redirect_reverse('ews:site_detail', args=[site_id,])

    def get(self, request, site_id):
        return render(request, 'ews/import.html', {
            'site_id': site_id
        })


@login_required
def site_detail(request, site_id):
    df = read_frame(FeatureData.objects.filter(site_id=site_id))
    entry = Site.objects.get(id=site_id)

    specs = get_plot_specification_details('barplot_feature_data_2')
    fig = create_barplot_feature_data_2(df, spec=specs)
    return render(request, 'ews/site_detail.html', {
                  'fig': fig,
                  'entry': entry})


class SelectareaCreateView(View):

    def post(self, request):

        form = SelectAreaForm(request.POST)

        if not form.is_valid():
            return http_response_form_not_valid(form)

        selectarea = SelectArea()
        selectarea.user = request.user
        selectarea.name = form.cleaned_data['name']
        selectarea.geom = form.cleaned_data['geom']
        selectarea.feature_type = form.cleaned_data['feature_type']
        selectarea.save()

        logger.debug("selectarea was saved: " + pformat(selectarea))

        return redirect_reverse('ews:selectarea_create')

    def get(self, request):
        return render(request, 'ews/selectarea_create.html', {
            'form': SelectAreaForm(),
            'areas': SelectArea.objects.all(),
            'entries': Site.objects.filter(owner=request.user)
        })


class RegisterView(View):

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmation = request.POST['confirmation']

        # Ensure password matches confirmation
        if password != confirmation:
            return render(request, 'ews/register.html', {
                'message': Message.PASSWORDS_MUST_MATCH
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            KRock.create_user_and_role(config('APP_ID'),
                                       username,
                                       password,
                                       email)
        except IntegrityError:
            return render(request, 'ews/register.html', {
                'message': Message.USERNAME_ALREADY_TAKEN
            })
        except KRockError as err:
            return render(request, 'ews/register.html', {
                'message': err.message
            })

        login(request, user)
        return redirect_reverse('ews:mlmodels')

    def get(self, request):
        return render(request, 'ews/register.html')


def model_fit(request, model_id):
    logger.debug('Entering model_fit(model_id={})'.format(model_id))

    model = PredictionModel.get_model_by_id_or_none(model_id)

    if model is None:
        return HttpResponse(Message.MODEL_NOT_FOUND)

    areavars = import_data_from_model(model)

    logger.debug('areavars:\n' + pformat(areavars))

    # Helper function to render error page
    def render_error(request, message):
        return render(request, 'ews/models.html', {
             'entries': PredictionModel.objects.filter(user=request.user),
             'message': message
        })

    if areavars[0].empty:
        return render_error(request,
                            Message.ERROR_AREAS_WITHOUT_PREDICTORS_OR_DATA)

    res = create_daily_lagvars(areavars, remove_duplicates=True)

    res = res[res.index.month.isin([5, 6, 7, 8, 9])].reset_index()

    logger.debug('res after filtering for summer months:\n' + pformat(res))

    if res.empty:
        return render_error(request, Message.ERROR_NO_DATA_FOR_SUMMER_MONTHS)

    FIB = read_frame(FeatureData.objects.filter(site=model.site.all()[0]))
    FIB['date'] = FIB.date.round('D')
    logger.debug('FIB:\n' + pformat(FIB))

    d = FIB.merge(res, on='date').drop(['variable', 'method'], axis=1)
    logger.debug('d:\n' + pformat(d))

    if d.empty:
        return render_error(request, Message.ERROR_NO_COMMON_DATES)
    D = d.dropna()
    D = D.sort_values('date')
    y = numpy.log10(D['value'])
    X = D.drop(['date', 'value', 'id', 'site'], axis=1)
    X = X.apply(pandas.to_numeric, downcast='float')
    y = y.apply(pandas.to_numeric, downcast='float')
    Xdf = X
    tscv = TimeSeriesSplit(n_splits=2)

    X = numpy.array(X)
    y = numpy.array(y)

    for train_index, test_index in tscv.split(X):

        logger.debug('train_index:\n' + pformat(train_index))
        logger.debug('test_index:\n' + pformat(test_index))

        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

    test_dates = D.iloc[test_index].date
    logger.debug('test_dates:\n' + pformat(test_dates))

    testdates_min = test_dates.min().date()
    testdates_max = test_dates.max().date()

    logger.debug('testdates_min:\n' + pformat(testdates_min))
    logger.debug('testdates_max:\n' + pformat(testdates_max))

    if model.fit is None:
        rf = RangerForestRegressor(quantiles=True,
                                   n_estimators=1000,
                                   importance='impurity',
                                   mtry=5,
                                   min_node_size=10)
        rf.fit(X_train, y_train)
        # rf = RandomForestRegressor(n_estimators = 1000, min_samples_leaf = 2)

        # enable quantile regression on instantiation
        # rfr = RangerForestRegressor(quantiles=True,n_estimators= 500)
        # fr.fit(X_train, y_train)

        # rf.fit(X_train, y_train)
        model.fit = pickle.dumps(rf)
        model.save()

    rf = pickle.loads(model.fit)

    df_test = pandas.DataFrame({
        'meas': y_test,
        'pred': rf.predict_quantiles(X_test, quantiles=[.5]).round(3),
        'split': 'out of sample',
        'P95': rf.predict_quantiles(X_test, quantiles=[0.95]).round(3),
        'P90': rf.predict_quantiles(X_test, quantiles=[0.9]).round(3),
        'P2_5': rf.predict_quantiles(X_test, quantiles=[0.025]).round(3),
        'P97_5': rf.predict_quantiles(X_test, quantiles=[0.975]).round(3)
    })

    df_test['belowP95'] = df_test['meas'] < df_test['P95']
    df_test['belowP90'] = df_test['meas'] < df_test['P90']
    df_test['belowP97_5'] = df_test['meas'] <= df_test['P97_5']
    df_test['aboveP2_5'] = df_test['meas'] >= df_test['P2_5']
    df_test['measured_contamination'] = df_test['meas'] >= numpy.log10(1800)
    df_test['predicted_contamination'] = df_test['P90'] >= numpy.log10(900)
    df_table = df_test[df_test['meas'].isna() is False]
    ct_total = pandas.crosstab(df_table['predicted_contamination'],
                               df_table['measured_contamination'])
    ct_rel = pandas.crosstab(df_table['predicted_contamination'],
                             df_table['measured_contamination'],
                             normalize='columns').round(2)

    ratios = {
        'belowP95': numpy.mean(df_test['belowP95']).round(2)*100,
        'in95': numpy.mean(df_test['belowP97_5']
                           & df_test['aboveP2_5']).round(2)*100,
        'belowP90': numpy.mean(df_test['belowP90']).round(2)*100,
        'N_alerts': numpy.sum(df_test['predicted_contamination']),
        'N_highMeasurements': numpy.sum(df_test['measured_contamination']),
        'true_positive': ct_total.loc[True, True],
        'truely_predicted_contaminations': ct_rel.loc[True, True],
    }

    df_train = pandas.DataFrame({
        'meas': y_train,
        'pred': rf.predict_quantiles(X_train, quantiles=[0.5]),
        'split': 'in sample'
    })

    importances = pandas.Series(data=rf.feature_importances_,
                                index=Xdf.columns)

    # Sort importances
    importances_sorted = importances.sort_values()
    importances_df = importances_sorted.reset_index()
    importances_df.columns = ['feature', 'importance']

    return render(request, 'ews/model_fit.html', {
        'bathingspot': model.site.all()[0],
        'entries': Site.objects.filter(owner=request.user),
        'model': model,
        'areas': model.area.all(),
        'R2_training': rf.score(X_train, y_train).round(2),
        'R2_test': rf.score(X_test, y_test).round(2),
        'N_test': len(y_test),
        'N_train': len(y_train),
        'MSE_test': mean_squared_error(rf.predict(X_test),
                                       y_test).round(2),
        'MSE_training': mean_squared_error(rf.predict(X_train),
                                           y_train).round(2),
        'model_fit': create_scatter_plot_model_fit(
            df=pandas.concat([df_test, df_train]),
            spec=get_plot_specification_details('scatter_plot_model_fit')
        ),
        'model_id': model_id,
        'form': PredictionForm(),
        'ratios': ratios,
        'testdates_min': str(testdates_min),
        'testdates_max': str(testdates_max),
        'feature_importance': create_barplot_importances(
            df=importances_df,
            spec=get_plot_specification_details('barplot_importances')
        )
    })


@login_required
def prediction_switch(request, model_id):
    model = PredictionModel.objects.get(id=model_id)
    model.predict = not model.predict
    model.save()
    return json_response_status(str(model.predict))


class ImportNewDataView(View):

    def post(self, request, slug):
        site_id = slug.split(':')[-2]

        try:
            Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            return json_response_status('forbidden', status=402)

        if not Site.objects.get(id=site_id).get_subscription_url() == slug:
            return json_response_status('forbidden', status=402)

        get_response = CBroker\
            .get_slug_attributes(slug=Site.objects.get(id=site_id)
                                 .get_broker_id())  # beforre slug = slug
        d = pandas.json_normalize(get_response.json())
        dt = parser.parse(d['dateObserved.value'][0])
        date = dt.strftime('%Y-%m-%d %H:%M:%S')
        fd = FeatureData()
        fd.date = date
        fd.site = Site.objects.get(id=site_id)

        # Set column depending on broker_type
        column = {
            'WeatherObserved': 'precipitation.value',
            'WaterObserved': 'flow.value',
            'WaterQualityObserved': 'escherichia_coli.value'
        }[fd.site.broker_type]

        fd.value = d[column][0]

        try:
            fd.save()
        except fd.DoesNotExist:
            return json_response_error('data import failed')

        return json_response_status('ok')

    # hsonne: Better not define this function?
    def get(self, request, slug):
        return HttpResponse(Message.PAGE_NOT_FOUND)


@login_required(login_url='/login')
def api_get_predictions(request, model_id):

    if request.method != 'POST':
        return json_response_error(Message.POST_REQUEST_REQUIRED)

    # Query for requested model
    try:
        model = PredictionModel.objects.get(pk=model_id)
    except PredictionModel.DoesNotExist:
        return json_response_error(Message.MODEL_NOT_FOUND, status=404)

    # Check if user is also owner of the model
    if request.user != model.user:
        # TODO: This it not the correct message, is it?
        return json_response_error(Message.CHANGE_POST_NOT_ALLOWED)

    data = json.loads(request.body)
    predict = predict_daterange(start=datetime.datetime
                                .strptime(data['start_date'], '%Y-%m-%d'),
                                end=datetime.datetime
                                .strptime(data['end_date'], '%Y-%m-%d'),
                                model_id=model_id).to_json(orient='records')
    return JsonResponse(json.loads(predict), status=200, safe=False)


@login_required(login_url='/login')
def api_get_broker_urls(request, model_id):

    try:
        model = PredictionModel.objects.get(pk=model_id)
    except PredictionModel.DoesNotExist:
        return json_response_error(Message.MODEL_NOT_FOUND, status=404)

    if not request.user == model.user:
        return json_response_error(Message.CHANGE_POST_NOT_ALLOWED)

    return JsonResponse(get_site_urls(model), status=200, safe=False)
