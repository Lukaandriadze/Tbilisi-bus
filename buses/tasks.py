# your_app/tasks.py
import time
import requests
import logging
from celery import shared_task
from users.tasks import send_email_async
from cart.models import Cart

logger = logging.getLogger(__name__)

@shared_task
def check_cart_notify_task(cart_id):
    logger.info(f"Starting notification task for Cart {cart_id}")

    while True:
        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            logger.warning(f"Cart {cart_id} does not exist anymore, stopping task")
            break

        if cart.notified:
            logger.info(f"Cart {cart_id} already notified, stopping task")
            break

        stop_id = cart.bus_stop.stop_id
        url = f"https://transit.ttc.com.ge/pis-gateway/api/v2/stops/1:{stop_id}/arrival-times"
        headers = {
            "x-api-key": "c0a2f304-551a-4d08-b8df-2c53ecd57f9f",
            "accept": "application/json"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error(f"Failed to get arrival times for stop {stop_id}: {e}")
            data = []

        if not isinstance(data, list):
            data = []

        for arrival in data:
            if arrival.get('shortName') == cart.short_name:
                realtime = arrival.get('realtimeArrivalMinutes')
                logger.info(f"Checking arrival for Cart {cart_id}: bus {cart.short_name} arrives in {realtime} mins (wanted {cart.selected_time})")
                if realtime == cart.selected_time:
                    try:
                        send_email_async.delay(
                            subject=f"ავტობუსი {cart.short_name} მოვა",
                            message=f"ავტობუსი {cart.short_name} მოვა {cart.selected_time} წუთში.",
                            recipient_email=cart.user.email
                        )
                        cart.notified = True
                        cart.save(update_fields=['notified'])
                        logger.info(f"Notification sent for Cart {cart_id}")
                        cart.delete()
                        return
                    except Exception as e:
                        logger.error(f"Failed to send email for Cart {cart_id}: {e}")
        time.sleep(10)
