from django.shortcuts import render, get_object_or_404
from .models import Buses
from django.core.paginator import Paginator
import requests
from django.contrib.auth.decorators import login_required
from django.http import Http404
@login_required
def bus_stop_list(request):
    search_query = request.GET.get('search', '')
    sort_order = request.GET.get('sort', 'asc')
    buses = Buses.objects.all()
    
    if search_query:
        buses = buses.filter(name__istartswith=search_query)
    
    if sort_order == 'desc':
        buses = buses.order_by('name')  
    else:
        buses = buses.order_by('BusNam')  
    
    paginator = Paginator(buses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'Page2_bus_stop.html', {
        'buses': page_obj, 
        'search_query': search_query
    })
@login_required
def bus_stop_detail(request, stop_id):
    bus_stop = get_object_or_404(Buses, stop_id=stop_id)
    
    url = f"https://transit.ttc.com.ge/pis-gateway/api/v3/routes/{bus_stop.stop_id}/stops?patternSuffix=1:01&locale=ka"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "connection": "keep-alive",
        "cookie": "cookiesession1=678A3E121E4B4F564603CE2F2F0A5A5D; _ga=GA1.1.1039088914.1745765788; _ga_XKN7FJ75X8=GS1.1.1745840153.6.1.1745850395.0.0.0",
        "host": "transit.ttc.com.ge",
        "referer": "https://transit.ttc.com.ge/",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "x-api-key": "c0a2f304-551a-4d08-b8df-2c53ecd57f9f"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        data = response.json()
        
        stops_data = []
        if isinstance(data, list):
            for stop in data:
                if "name" in stop:
                    stops_data.append({
                        'name': stop["name"],
                        'other_data': stop  
                    })
        elif isinstance(data, dict) and "stops" in data:
            for stop in data["stops"]:
                if "name" in stop:
                    stops_data.append({
                        'name': stop["name"],
                        'other_data': stop 
                    })
        
        return render(request, 'Page2_bus_detail.html', {
            'bus_stop': bus_stop,
            'stops_data': stops_data,
            'api_data': data 
        })
        
    except requests.exceptions.RequestException as e:
        raise Http404(f"Failed to fetch stop details: {str(e)}")
    
