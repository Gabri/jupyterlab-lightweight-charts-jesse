import pandas as pd
import numpy as np
import json
from IPython.display import Javascript, display

data_name_var_anchor = 'chart_data_anchor'


def plot(candles, data=pd.DataFrame(), data_anchor=pd.DataFrame(), config=[],
         config_anchor=[], dark_theme=False, width=980, height=700):
    init()
    inject_candles(candles)
    inject(data)
    inject(data_anchor, data_name_var=data_name_var_anchor)
    inject(config, name='config')
    inject(config_anchor, name='config', data_name_var=data_name_var_anchor)
    render(width, height, dark_theme)


### Internal utils
def _ix_to_time(ix):
    if isinstance(ix, pd.Timestamp):
        return int(ix.strftime('%s'))
    else:
        return int(ix)


# Use to process series into lw_data before using inject
def transform_series(series):
    return [
        {'time': _ix_to_time(ix), 'value': float(val)}
        for ix, val in series.iteritems()
    ]


# Use if you want low level control over what's injected
def init():
    display(Javascript("""
        if (typeof window.chart_data !== 'object') {
            window.chart_data = {}
        }
        if (typeof window.chart_data_anchor !== 'object') {
            window.chart_data_anchor = {}
        }
    """))


def inject_candles(candles):
    display(Javascript("""
        if (typeof window.chart_candles !== 'object') {
            window.chart_candles = {}
        }
        if (typeof window.chart_volume !== 'object') {
            window.chart_volume = {}
        }
    """))
    if candles is not None:
        display(Javascript(f'window.chart_candles = {candles.to_json(orient="records")};'))
        candles['color'] = np.where(candles['close'] > candles['open'], 'rgba(38,166,154,0.6)', 'rgba(255,56,55,0.6)')
        display(Javascript(f'window.chart_volume = {candles.filter(["time", "volume","color"]).rename(columns={"volume":"value"}).to_json(orient="records")};'))


def inject_json(data, name, data_name_var='chart_data'):
    display(Javascript(f'window.{data_name_var}["{name}"] = {json.dumps(data)};'))


# Use to automatically transform and inject pd.Series
def inject_series(series, name=None, data_name_var='chart_data'):
    return inject_json(transform_series(series), series.name if name is None else name,
                       data_name_var=data_name_var)


# Use to automatically transform and inject pd.DataFrame
def inject_df(df, data_name_var='chart_data'):
    for col in df.columns:
        inject_series(df[col], data_name_var=data_name_var)


def inject(data, name=None, data_name_var='chart_data'):
    if isinstance(data, pd.Series):
        inject_series(data, name, data_name_var)
    elif isinstance(data, pd.DataFrame):
        inject_df(data, data_name_var)
    else:
        inject_json(data, name, data_name_var)


def cleanup():
    display(Javascript("window.chart_data = undefined"))
    display(Javascript(f"window.{data_name_var_anchor} = undefined"))


def render(width=950, height=700, dark_theme=False):
    return display(Javascript(f"""
    // Describe dependencies
    require.config({{
        paths: {{
            'lightweight-charts': ['//unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production']
        }},
        shim: {{
            'lightweight-charts': {{
                exports: "LightweightCharts",
            }},
        }}
    }});
        
    require(['lightweight-charts'], function() {{
        // (Re-)create div to display the chart in
        $("#chart").remove();
        element.append("<div id='chart' style='margin-top: 1em;'></div>");
        
        const dark_theme = {'true' if dark_theme == True else 'false'}
        let chartOptions = {{
            width: {width}, 
            height: {height}
        }}
        if (dark_theme === true) {{
            chartOptions = {{
                layout: {{
                    backgroundColor: '#2b2b43',
                    textColor: 'rgba(255, 255, 255, 0.7)',
                }},
                grid: {{
                    vertLines: {{
                        color: 'rgba(255, 255, 255, 0.1)',
                    }},
                    horzLines: {{
                        color: 'rgba(255, 255, 255, 0.1)',
                    }},
                }},
                crosshair: {{
                    mode: LightweightCharts.CrosshairMode.Normal,
                    color: 'rgba(255, 255, 255, 0.85)',
                }},
                ...chartOptions
            }}
        }}

        // Create chart
        const chart = LightweightCharts.createChart('chart', chartOptions);
        
        // Adding candles
        var candleSeries = chart.addCandlestickSeries();
        candleSeries.setData(chart_candles)
        
        // Adding volume
        var volumeSeries = chart.addHistogramSeries({{
            color: '#26a69a',
            priceFormat: {{
                type: 'volume',
            }},
            priceScaleId: '',
            scaleMargins: {{
                top: 0.8,
                bottom: 0,
            }},
        }});
        volumeSeries.setData(chart_volume)
        
        // Adding indicators data
        // config and chart_data should be injected in advance by calling any inject_* function
        chart_data.config.forEach(it => {{
            const params = {{'title': it['name'], ...it['style']}}
            const data = chart_data[it['name']]

            chart[it['fn']](params).setData(data)
        }})
        
        // ANCHOR TF DATA : config and chart_data_anchor should be injected in advance by calling any inject_* function
        chart_data_anchor.config.forEach(it => {{
            const params = {{'title': it['name'], ...it['style']}}
            const data = chart_data_anchor[it['name']]

            chart[it['fn']](params).setData(data)
        }})
        
        // Apply Option settings
        chart.applyOptions({{
            priceScale: {{
                autoscale: true
            }},
            timeScale: {{
                timeVisible: true,
                secondsVisible: true,
                rightOffset: 5
            }},
        }});

        // Make prices fully visible
        document.querySelector("#chart > div > table > tr:nth-child(1) > td:nth-child(3) > div").style["left"] = "-30px";
        // Make legend fully visible
        document.querySelector("#chart > div > table > tr:nth-child(1) > td:nth-child(2) > div").style["left"] = "-30px"; 
        
    }})
    """))
