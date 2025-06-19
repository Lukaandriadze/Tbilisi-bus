import logging
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Cart
from busstop.models import BusStop
from buses.tasks import check_cart_notify_task  # Import your celery task

logger = logging.getLogger(__name__)

@login_required
def view_cart(request):
    items = Cart.objects.filter(user=request.user)
    return render(request, 'cart.html', {'items': items})

@login_required
def choose_bus_stop(request):
    if request.method == 'POST':
        bus_stop_id = request.POST.get('bus_stop_id')
        return redirect('cart:add_bus_time', stop_id=bus_stop_id)

    bus_stops = BusStop.objects.all()
    return render(request, 'to_add_cart.html', {'bus_stops': bus_stops})

@login_required
def add_cart_choose_bus_and_time(request, stop_id):
    stop = get_object_or_404(BusStop, stop_id=stop_id)
    url = f"https://transit.ttc.com.ge/pis-gateway/api/v2/stops/1:{stop.stop_id}/arrival-times"
    headers = {
        "x-api-key": "c0a2f304-551a-4d08-b8df-2c53ecd57f9f",
        "accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to get arrivals for stop {stop_id}: {e}")
        data = []

    arrivals = data if isinstance(data, list) else []
    short_names = sorted({item.get("shortName") for item in arrivals if item.get("shortName")})

    if request.method == "POST":
        selected_short_name = request.POST.get("bus_short_name")
        selected_time = request.POST.get("selected_time")

        try:
            selected_time_int = int(selected_time)
        except (ValueError, TypeError):
            selected_time_int = 0

        cart = Cart.objects.create(
            user=request.user,
            bus_stop=stop,
            bus=None,
            selected_time=selected_time_int,
            short_name=selected_short_name
        )

        # Launch the celery task asynchronously instead of thread
        check_cart_notify_task.delay(cart.id)

        return redirect("cart:view")

    return render(request, "cart_add_bus_time.html", {
        "stop": stop,
        "short_names": short_names,
    })

def delete_cart_item(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(Cart, id=item_id)
        item.delete()
    return redirect('cart:view')