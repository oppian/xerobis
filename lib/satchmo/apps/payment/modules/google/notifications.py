'''
Created on 3 Mar 2009

@author: dalore
'''
from django.utils.translation import ugettext as _
from livesettings import config_get_group
from payment.utils import get_processor_by_key
from payment.views import confirm
from satchmo_store.shop.models import Cart, Order, OrderPayment
import auth
import re

#from payment.modules.base import PaymentRecorder

def notifiy_neworder(request, data):
    """
    Called when google reports a new order.
    
    Looks up the order from the private data and sets the status.
    Empties the cart.
    """
    # get params from data
    private_data = data['shopping-cart.merchant-private-data']
    order_id = re.search('satchmo-order id="(\d+)"', private_data).group(1)
    order = Order.objects.get(pk=order_id)
    payment_module = config_get_group('PAYMENT_GOOGLE')
    processor = get_processor_by_key('PAYMENT_GOOGLE')
    
    # record pending payment
    amount = data['order-total']
    pending_payment = processor.create_pending_payment(order)
    # save transaction id so we can find this order later
    pending_payment.capture.transaction_id = data['google-order-number']
    pending_payment.capture.save()
    
    # delete cart
    for cart in Cart.objects.filter(customer=order.contact):
        cart.delete()
        
    # set status
    order.add_status(status='New', notes=_("Received through Google Checkout."))
    
        
def do_charged(request, data):
    # find order from google id
    transaction_id = data['google-order-number']
    payment = OrderPayment.objects.filter(transaction_id__exact=transaction_id)[0]
    order = payment.order
    
    # Added to track total sold for each product
    for item in order.orderitem_set.all():
        product = item.product
        product.total_sold += item.quantity
        product.items_in_stock -= item.quantity
        product.save()
        
    # process payment
    processor = get_processor_by_key('PAYMENT_GOOGLE')
    order.add_status(status='Billed', notes=_("Paid through Google Checkout."))
    

def notify_statechanged(request, data):
    state = data['new-financial-order-state']
    if state == 'CHARGED':
        do_charged(request, data)
        
def notify_chargeamount(request, data):
    # find order from google id
    transaction_id = data['google-order-number']
    payment = OrderPayment.objects.filter(transaction_id__exact=transaction_id)[0]
    order = payment.order
    processor = get_processor_by_key('PAYMENT_GOOGLE')
    processor.record_payment(amount=data['latest-charge-amount'], transaction_id=transaction_id, order=order)

