from django.shortcuts import render, redirect, reverse
from .forms import CronConfigForm
from .scripts import manage_load_cron
from .models import DataSet
from django.views.generic import DetailView, ListView
from search_engine.whoosh_functions import search_doc

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
    template_name = 'DataHiveApp/dataset_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q")
        context['input'] = q
        return context

    def get_queryset(self):
        queryset = None
        if self.request.GET.get("q"):
            results = search_doc(self.request.GET.get("q"))
            if results:
                queryset = DataSet.objects.filter(pk__in=[result['dataset_id'] for result in results])
        else:
            queryset = DataSet.objects.all()
        return queryset



def random_dataset(request):
    ds = DataSet.objects.order_by('?').first().id
    return redirect('/dataset/'+str(ds))
