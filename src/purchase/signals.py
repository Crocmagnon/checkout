def basket_item_on_save(sender, **kwargs):
    from purchase.models import Cache

    Cache.get_solo().refresh()
