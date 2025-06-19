from django.shortcuts import render, get_object_or_404
from .models import BusStop
from django.core.paginator import Paginator
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
@login_required
def bus_stop_list(request):
    search_query = request.GET.get('search', '')
    sort_order = request.GET.get('sort', 'asc')
    bus_stops = BusStop.objects.all()

    if search_query:
        bus_stops = bus_stops.filter(arrival_time__istartswith=search_query)

    if sort_order == 'desc':
        bus_stops = bus_stops.order_by('-stop_id')  # შენიშვნა: - ნიშნით ვსორტირებთ კლებადობით
    else:
        bus_stops = bus_stops.order_by('arrival_time')

    paginator = Paginator(bus_stops, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'bus_stops.html', {
        'bus_stops': page_obj,
        'search_query': search_query,
        'sort_order': sort_order,
    })
@login_required
def bus_stop_detail(request, stop_id):
    bus_stop = get_object_or_404(BusStop, stop_id=stop_id)
    url = f"https://transit.ttc.com.ge/pis-gateway/api/v2/stops/1:{bus_stop.stop_id}/arrival-times?locale=ka&ignoreScheduledArrivalTimes=false"

    headers = {
        "x-api-key": "c0a2f304-551a-4d08-b8df-2c53ecd57f9f",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    bus_details = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        arrivals = []
        for route in data:
            arrivals.append({
                'shortName': route.get('shortName'),
                'headsign': route.get('headsign'),
                'realtimeArrivalMinutes': route.get('realtimeArrivalMinutes'),
                'isRealtime': route.get('realtime', False)
            })
        arrivals.sort(key=lambda x: x['realtimeArrivalMinutes'] if x['realtimeArrivalMinutes'] is not None else float('inf'))
        bus_details = arrivals
    except requests.exceptions.RequestException as e:
        print(f"Error fetching arrival times: {e}")
        bus_details = []

    return render(request, 'bus_stop_detail.html', {
        'bus_stop': bus_stop,
        'bus_details': bus_details
    })
