def basket_item_on_save(sender, **kwargs):
    from purchase.models import CacheEtag

    CacheEtag.get_solo().refresh()
