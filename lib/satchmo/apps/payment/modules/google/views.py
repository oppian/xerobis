from django import http
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from livesettings import config_get_group, config_value
from payment.config import payment_live
from payment.views import confirm, payship
from satchmo_store.shop.models import Cart, Contact, Order
from satchmo_utils.dynamic import lookup_url, lookup_template
import auth
import base64
import hmac
import logging
import notifications
import sha
import urllib

# TODO: This module doesn't seem to actually record any payments.

log = logging.getLogger("payment.modules.google.processor")

class GoogleCart(object):
    def __init__(self, order, payment_module, live):
        self.settings = payment_module
        self.cart_xml = self._cart_xml(order)
        self.signature = self._signature(live)

    def _cart_xml(self, order):
        template = get_template(self.settings["CART_XML_TEMPLATE"].value)

        shopping_url = lookup_url(self.settings, 'satchmo_checkout-success', True, self.settings.SSL.value)
        edit_url = lookup_url(self.settings, 'satchmo_cart', True, self.settings.SSL.value)
        ctx = Context({"order" : order,
                       "continue_shopping_url" : shopping_url,
                       "edit_cart_url" : edit_url,
                       "currency" : self.settings.CURRENCY_CODE.value,
                       })
        return template.render(ctx)

    def _signature(self, live):
        if live:
            merchkey = self.settings.MERCHANT_KEY.value
        else:
            merchkey = self.settings.MERCHANT_TEST_KEY.value

        s = hmac.new(merchkey, self.cart_xml, sha)
        rawsig = s.digest()
        return rawsig

    def encoded_cart(self):
        return base64.encodestring(self.cart_xml)[:-1]

    def encoded_signature(self):
        sig = base64.encodestring(self.signature)[:-1]
        log.debug("Sig is: %s", sig)
        return sig

def pay_ship_info(request):
    return payship.simple_pay_ship_info(request, config_get_group('PAYMENT_GOOGLE'), 'shop/checkout/google/pay_ship.html')
pay_ship_info = never_cache(pay_ship_info)

def confirm_info(request):
    payment_module = config_get_group('PAYMENT_GOOGLE')

    controller = confirm.ConfirmController(request, payment_module)
    if not controller.sanity_check():
        return controller.response
    
    live = payment_live(payment_module)
    gcart = GoogleCart(controller.order, payment_module, live)
    log.debug("CART:\n%s", gcart.cart_xml)

    if live:
        merchant_id = payment_module.MERCHANT_ID.value
        url_template = payment_module.POST_URL.value
    else:
        merchant_id = payment_module.MERCHANT_TEST_ID.value
        url_template = payment_module.POST_TEST_URL.value
        
    post_url = url_template % {'MERCHANT_ID' : merchant_id}
    default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')
    
    ctx = {
        'post_url': post_url,
        'google_cart' : gcart.encoded_cart(),
        'google_signature' : gcart.encoded_signature(),
        'PAYMENT_LIVE' : live
    }
    
    controller.extra_context = ctx
    controller.confirm()
    return controller.response

confirm_info = never_cache(confirm_info)



def notification(request):
    """
    View to receive notifcations from google about order status
    """
    data = request.POST
    log.debug(data)
    
    # check the given merchant id
    log.debug("Google Checkout Notification")
    response = auth.do_auth(request)
    if response:
        return response
    
    # ok its authed, get the type and serial
    type = data['_type']
    serial_number = data['serial-number'].strip()
    
    log.debug("type: %s" % type)
    log.debug("serial-number: %s" % serial_number)
    
    # check type
    if type == 'new-order-notification':
        notifications.notifiy_neworder(request, data)
    elif type == 'order-state-change-notification':
        notifications.notify_statechanged(request, data)
    elif type == 'charge-amount-notification':
        notifications.notify_chargeamount(request, data)

    ack = '<notification-acknowledgment xmlns="http://checkout.google.com/schema/2" serial-number="%s"/>' % serial_number 
    response = http.HttpResponse(content=ack, content_type="text/xml; charset=UTF-8")
    log.debug(response)
    return response

notification = never_cache(notification)

def success(request):
    """
    The order has been succesfully processed.  This can be used to generate a receipt or some other confirmation
    """
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        return bad_or_missing(request, _('Your order has already been processed.'))
        
    del request.session['orderID']
    context = RequestContext(request, {'order': order})
    return render_to_response('shop/checkout/success.html', context)
success = never_cache(success)