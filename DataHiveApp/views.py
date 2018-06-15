from django.shortcuts import render, redirect
from .forms import CronConfigForm
from .scripts import manage_load_cron
from .models import DataSet
from django.views.generic import DetailView, ListView
from search_engine.whoosh_functions import search_doc
from django.http import StreamingHttpResponse
import requests


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


class DataSetListView(ListView):
    model = DataSet
    paginate_by = 20
    template_name = 'DataHiveApp/dataset_list.html'

    def get_queryset(self):
        queryset = []
        if self.request.GET.get("q"):
            results = search_doc(self.request.GET.get("q"))
            if results:
                queryset = DataSet.objects.filter(pk__in=[result['dataset_id'] for result in results])
        else:
            queryset = DataSet.objects.all().order_by('?')

        return queryset


def download_from_url(request, file_url):
    r = requests.get(file_url, stream=True)
    resp = StreamingHttpResponse(streaming_content=r)
    file_name = file_url.split("/")[-1]
    resp['Content-Disposition'] = 'attachment;filename="'+file_name+'"'
    return resp


def random_dataset(request):
    ds = DataSet.objects.order_by('?').first().id
    return redirect('/dataset/'+str(ds))
