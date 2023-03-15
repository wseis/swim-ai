import datetime
import logging
import pprint
import pandas
import pickle
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
from django_pandas.io import read_frame
from ews.models import FeatureData
from ews.models import FeatureType
from ews.models import PredictionModel
from ews.models import Site
from shapely.geometry import shape
from .plot import plot_predicitons
from .messages import Message


# Obtain a logger instance
logger = logging.getLogger('debug')


def import_data_from_model(model):
    logger.debug('Entering import_data_from_model()')
    areas = read_frame(model.area.all())
    logger.debug('areas defined for model:\n' + pprint.pformat(areas))
    areavars = []
    for index, row in areas.iterrows():
        type = row['feature_type']
        if type is None:
            logger.debug('feature_type is None in area {}'
                         ' of model with id {}'.format(index, model.id))
        site_ids = get_sites_of_type_in_geom(type, model.user, row['geom'])
        data = read_frame(FeatureData.objects.filter(site__in=site_ids),
                          index_col='date')
        data['area'] = row['name']
        data['feature_type'] = type
        areavars.append(data)
    return areavars


def get_site_urls(model):
    areas = read_frame(model.area.all())
    ids = []
    for index, row in areas.iterrows():
        site_ids = get_sites_of_type_in_geom(row['feature_type'],
                                             model.user,
                                             row['geom'])
        sites = Site.objects.filter(id__in=site_ids)
        ids.append([{'name': i.name, 'ID': i.get_broker_id()} for i in sites])
    return [elem for sublist in ids for elem in sublist]


def get_sites_of_type_in_geom(type, owner, geom):
    logger.debug('Entering get_sites_of_type_in_geom({}, '
                 '{}, geom)'.format(type, owner))
    df = read_frame(Site.objects.filter(
        feature_type=get_feature_type_named(type),
        owner=owner
    ))
    logger.debug('Site objects of type {}'
                 'belonging to {}:'.format(type, owner))
    logger.debug(pprint.pformat(df))
    select = is_contained(df, polygon=shape(geom))
    logger.debug('select: ' + pprint.pformat(select))
    if not any(select):
        site_ids = []
    else:
        site_ids = df['id'][select]
    logger.debug('Returning site_ids:\n' + pprint.pformat(site_ids))
    return site_ids


def get_feature_type_named(name):
    if name is None:
        logger.debug('The name given to get_feature_type_named()'
                     'is None. Returning None.')
        return None
    try:
        object = FeatureType.objects.get(name=name)
    except Exception:
        logger.debug(Message.ERROR_NO_FEATURE_TYPE_NAMED.format(name))
        return None
    return object


def is_contained(df, polygon):
    select = []
    for index, row in df.iterrows():
        select.append(polygon.contains(shape(row['geom'])))
    return select


def create_daily_lagvars(areavars, remove_duplicates=False):

    lagvars = []

    for i in range(len(areavars)):
        ft = areavars[i].area.unique() + ' '\
             + areavars[i].feature_type.unique()
        if remove_duplicates:
            areavars[i] = areavars[i][~areavars[i].index.
                                      duplicated(keep='first')]
        d = areavars[i].pivot(columns='site', values='value')
        if len(d.columns) > 1:
            d = pandas.DataFrame(d.mean(axis=1, skipna=True))
        for j in [1, 2, 3, 4, 5]:
            df = pandas.DataFrame()
            df[ft + '_shift_' + str(j)] = d.rolling(window=j).mean().shift(1)
            lagvars.append(df)
    return pandas.concat(lagvars, axis=1)


def predict_range(startdate, enddate, model, rawdata):
    if startdate == enddate:
        startdate = startdate - datetime.timedelta(days=1)
    newdata = rawdata[startdate:enddate].dropna()
    rf = pickle.loads(model.fit)
    # creating predictions using each individual 1000 trees
    # (estimators) of the Random forest
    df = pandas.DataFrame({
        'mean': rf.predict(newdata),
        'P95': rf.predict_quantiles(newdata, quantiles=[0.95]),
        'P2_5': rf.predict_quantiles(newdata, quantiles=[0.025]),
        'P90': rf.predict_quantiles(newdata, quantiles=[0.90]),
        'P97_5': rf.predict_quantiles(newdata, quantiles=[0.975])
    })
    df.index = newdata.index
    df = df.reset_index()
    FIB = read_frame(FeatureData.objects.filter(site=model.site.all()[0]))
    FIB['date'] = FIB.date.round('D')
    return df.merge(FIB, on='date', how='left')


def predict_and_plot_daterange(start, end, model_id):
    return plot_predicitons(predict_daterange(start, end, model_id))


def predict_daterange(start, end, model_id):
    # creating list of dataframe(one for for each area)
    model = PredictionModel.objects.get(id=model_id)
    model_name = PredictionModel.objects.get(name=model.name)
    areavars = import_data_from_model(model=model_name)
    ndata = create_daily_lagvars(areavars)
    predictions = predict_range(startdate=start,
                                enddate=end,
                                model=model,
                                rawdata=ndata)
    return predictions


def json_response_status(text, status=200, safe=True):
    return JsonResponse({'status': text}, status=status, safe=safe)


def json_response_error(text, status=400):
    return JsonResponse({'error': text}, status=status)


def redirect_reverse(viewname, args=None):
    return HttpResponseRedirect(reverse(viewname, args=args))
