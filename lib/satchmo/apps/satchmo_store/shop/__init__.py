from satchmo_settings import get_satchmo_setting
import logging
# import app_plugins

log = logging.getLogger('satchmo_store.shop')

if get_satchmo_setting('MULTISHOP'):
    log.debug('patching for multishop')
    from threaded_multihost import multihost_patch

# register = app_plugins.Library()
# 
# def admin_tools(point, *args, **kwargs):
#     'A section on the sidebar of the admin screen'
#     return { }
# 
# register.plugin_point(takes_context=False)(admin_tools)
# 
# def shop_sidebar(point, context, user, *args, **kwargs):
#     'A section on the sidebar of the base screen'
#     return { }
# 
# register.plugin_point(takes_context=True, takes_user=True)(shop_sidebar)
