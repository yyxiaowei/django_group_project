from django.urls import path

from . import views

app_name = 'echarts'

urlpatterns = [
    path('', views.bar, name='chart_bar'),
    path('bar/',views.bar,name='chart_bar'),
    path('bar/<detail>/',views.bar,name='bar_detail'),
    path('line/',views.line,name='chart_line'),
    path('line/<detail>/',views.line,name='line_detail'),
]