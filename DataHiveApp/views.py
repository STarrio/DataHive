from django.shortcuts import render, redirect, reverse
from .forms import CronConfigForm
from .scripts import manage_load_cron
from .models import DataSet
from django.views.generic import DetailView

def index(request):
    return render(request, 'DataHiveApp/index.html')


def config(request):
    if request.method == 'POST':
        form = CronConfigForm(request.POST)

        if form.is_valid():
            data = form.data
            manage_load_cron.update_cron(**{'minutes': data['minutes'][0],
                                            'hours': data['hours'][0],
                                            'days': data['days'][0]})
            return render(request, 'DataHiveApp/configuration.html', {'form': form})

    else:
        data = manage_load_cron.get_current_cron_config()
        form = CronConfigForm(data) if data != {} else CronConfigForm({'minutes': 1, 'hours': 1, 'days': 1})

    return render(request, 'DataHiveApp/configuration.html', {'form': form})


class DataSetDetailView(DetailView):
    model = DataSet


def random_dataset(request):
    ds = DataSet.objects.order_by('?').first().id
    return redirect('/dataset/'+str(ds))
