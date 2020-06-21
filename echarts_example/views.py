from django.shortcuts import render
from pyecharts.charts import Bar, Line
from pyecharts.faker import Faker,POPULATION
from pyecharts import options as opts
import math

def bar(request,**kwargs):
    popu = (
        Bar()
            .add_xaxis([p[0] for p in POPULATION[1:]])
            .add_yaxis('国家',['%.2f' % (p[1]/100000) for p in POPULATION[1:]])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="世界人口(十万)"),
                yaxis_opts=opts.AxisOpts(offset=-10),
                datazoom_opts=opts.DataZoomOpts(is_show=True,range_start=0,range_end=1)
            )
    )
    bar = (
        Bar()
           .add_xaxis(Faker.choose())
           .add_yaxis("商家A", Faker.values())
           .add_yaxis("商家B", Faker.values())
           .set_global_opts(
               title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"),
            )
    )
    if kwargs:
        return render(request,'echarts_example/bar_detail.html',{
            'myEchart':locals()[kwargs['detail']].dump_options(),
        })
    
    return render(request,'echarts_example/bar.html',{
            'myEchart':bar.dump_options(),
            'population': popu.dump_options,
            })
    

def line(request,**kwargs):
    option = {
        'title': { 'text': 'ECharts 入门示例' },
        'legend': {'data': ['销量']},
        'xAxis': { 'data': ["衬衫","羊毛衫","雪纺衫","裤子","高跟鞋","袜子"]},
        'yAxis': {},
        'series': [
            {'name': '销量', 'type':'line', 'data': [5, 20, 36, 10, 10, 20] }
        ]
    }
    if kwargs:
        return render(request,'echarts_example/line_detail.html',{
            'myEchart':locals()[kwargs['detail']],
        })
    return render(request,'echarts_example/line.html',{
            'option': option
        })
