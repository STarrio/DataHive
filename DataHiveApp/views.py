from django.shortcuts import render
from .forms import CronConfigForm
from .scripts import manage_load_cron

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
