def basket_item_on_save(sender, **kwargs):  # noqa: ARG001
    from purchase.models import Cache

    Cache.get_solo().refresh()
