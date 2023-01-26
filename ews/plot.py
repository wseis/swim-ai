import numpy
import plotly.express as px
import plotly.graph_objects as go

from plotly.offline import plot

from .messages import Message

def get_plot_specification_details(plot_name = None):
    # TODO: Read this from a yaml file (?)
    specs = {
        'barplot_feature_data_1': {
            'traces': {
                'marker_color': '#3185ff',
                'marker_line_color': '#3185ff',
                'marker_line_width': 2,
                'opacity': 0.6
            },
            'layout': {
                'font_family': 'Helvetica Neue, Helvetica, Arial, sans-serif',
                'font_color': 'black',
                'font': {'size': 14},
                'xaxis_title': 'Date',
                'yaxis_title': 'Value' # labelpoint.variable.name + ' ['+ labelpoint.variable.unit.abbreviation + ']',
                #'markersize': 12
            }
        },
        'barplot_feature_data_2': {
            'traces': {
                'marker_color': 'rgb(158,202,225)',
                'marker_line_color': 'rgb(8,48,107)',
                'marker_line_width': 1.5,
                'opacity': 0.6
            }
        },
        'scatter_plot_model_fit': {
            'scatter': {
                'color_discrete_sequence': ['#212c52','#75c3ff'],
            },
            'layout': {
                'font_family': 'Helvetica Neue, Helvetica, Arial, sans-serif',
                'font_color': 'black',
                'title': {'text': 'Model fit of Random Forest model'},
                'xaxis_title': 'measured data (sample)',
                'yaxis_title': 'fitted values (in sample fit)',
                #'markersize': 12,
                'legend': {
                    'yanchor': 'top',
                    'title': None,
                    'y': 0.99,
                    'xanchor': 'left',
                    'x': 0.01
                }
            },
            'traces': {
                'marker_size': 8,
                #['#75c3ff', 'red'],
                #'marker_line_color': '#212c52',
                #'marker_line_width': 1.5,
                #'opacity': 1
            }
        },
        'barplot_importances': {
            'layout': {
                'font_family': 'Helvetica Neue, Helvetica, Arial, sans-serif',
                'font_color': 'black',
                'title': {'text': Message.FEATURE_IMPORTANCE_OF_RF_MODEL},
                #'markercolor': '#212c52'
            },
            'traces': {
                'marker_color': '#75c3ff',
                'marker_line_color': '#75c3ff',
                'marker_line_width': 1.5,
                'opacity': 1
            }
        }
    }
    # If no plot name is given, return all specifications
    if plot_name is None:
        return specs
    # Otherwise return the specification for plot_name
    return specs[plot_name]

def create_barplot_feature_data_1(df, labelpoint, spec):
    fig = px.bar(df, 'date', 'value',  opacity=1)
    fig.update_traces(**spec['traces'])
    fig.update_layout(**spec['layout'])
    return plot_to_div(fig)

def create_barplot_feature_data_2(df, spec):
    fig = px.bar(df, 'date', 'value',  opacity=1)
    fig.update_traces(**spec['traces'])
    return plot_to_div(fig)

def create_scatter_plot_model_fit(df, spec):
    fig = px.scatter(df, x='meas', y='pred', color='split', **spec['scatter'])
    fig.update_layout(**spec['layout'])
    fig.update_traces(**spec['traces'])
    return plot_to_div(fig)

def create_barplot_importances(df, spec):
    fig = px.bar(df, y='feature', x='importance', orientation='h')
    fig.update_layout(**spec['layout'])
    fig.update_traces(**spec['traces'])
    return plot_to_div(fig)

def plot_to_div(fig):
    return  plot(fig, output_type='div')

def get_plot_specification_predictions():
    # TODO: Read this from a yaml file (?)
    rgba_grey_1 = 'rgba(68, 68, 68, 1)'
    rgba_grey_0_1 = 'rgba(68, 68, 68, 0.1)'
    return {
        'upper_bound': {
            'name': 'Upper prediciton intervall',
            'line': {'width': 0.5, 'color': rgba_grey_1},
            'fillcolor': rgba_grey_1
        },
        'mean': {
            'name': 'Predicted geomean',
            'marker': {'color': 'rgb(0, 86, 110)'},
            'line': {'width': 2, 'color': 'rgb(0, 86, 110)'},
            'fillcolor': rgba_grey_0_1
        },
        'measurements': {
            'name': 'Measurements',
            'marker': {'color': 'orange', 'size': 10, 'opacity': 1},
            'line': {'width': 2, 'color': 'red'},
            'fillcolor': rgba_grey_0_1
        },
        'lower_bound': {
            'name': 'Lower prediction intervall',
            'line': {'width': 0.5, 'color': rgba_grey_1}
        },
        'layout': {
            'title': 'Predicted E.coli data for test dataset',
            'yaxis': {'title': 'E.coli lg [MPN/100ML)', 'showlegend': True}
        }
    }

def plot_predicitons(df):

    specs = get_plot_specification_predictions()

    data = [
        plot_predictions_lower_bound(df, specs['lower_bound']),
        plot_predictions_mean(df, specs['mean']),
        plot_predictions_upper_bound(df, specs['upper_bound']),
        plot_predictions_measurements(df, specs['measurements'])
    ]

    layout_spec=specs['layout']

    layout = go.Layout(title=layout_spec['title'], yaxis=layout_spec['yaxis'])

    return go.Figure(data=data, layout=layout)

def plot_predictions_upper_bound(df, plot_spec):
    return go.Scatter(
        x=df['date'],
        y=df['P95'],
        mode='lines',
        name=plot_spec['name'],
        line=plot_spec['line'],
        fillcolor=plot_spec['fillcolor']
        #, fill='tonexty'
    )

def plot_predictions_mean(df, plot_spec):
    return go.Scatter(
        x=df['date'],
        y=df['mean'],
        mode='lines+markers',
        name=plot_spec['name'],
        marker=plot_spec['marker'],
        line=plot_spec['line'],
        fillcolor=plot_spec['fillcolor']
        #, fill='tonexty'
    )

def plot_predictions_measurements(df, plot_spec):
    return go.Scatter(
        x=df['date'],
        y=numpy.log10(df['value']),
        mode='markers',
        name=plot_spec['name'],
        marker=plot_spec['marker'],
        line=plot_spec['line'],
        fillcolor=plot_spec['fillcolor']
        #, fill='tonexty'
    )

def plot_predictions_lower_bound(df, plot_spec):
    return go.Scatter(
        x=df['date'],
        y=df['P2_5'],
        mode='lines',
        name=plot_spec['name'],
        line=plot_spec['line']
    )
