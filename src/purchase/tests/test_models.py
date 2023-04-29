from purchase.models import Basket, BasketItem
from purchase.tests.factories import (
    PaymentMethodFactory,
    ProductFactory,
)


def test_with_articles_count(db):
    products = [
        ProductFactory(),
        ProductFactory(),
        ProductFactory(),
    ]
    payment_method = PaymentMethodFactory()

    basket = Basket.objects.create(payment_method=payment_method)
    BasketItem.objects.create(
        basket=basket,
        product=products[0],
        quantity=1,
        unit_price_cents=1,
    )
    BasketItem.objects.create(
        basket=basket,
        product=products[1],
        quantity=2,
        unit_price_cents=2,
    )
    BasketItem.objects.create(
        basket=basket,
        product=products[2],
        quantity=3,
        unit_price_cents=3,
    )
    basket = Basket.objects.priced().with_articles_count().first()
    assert basket.articles_count == 6
    assert basket.price == 14
