import time

import freezegun
from django.urls import reverse
from pytest_django.live_server_helper import LiveServer
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from common.models import User
from purchase.models import Basket
from purchase.tests.factories import (
    USER_PASSWORD,
    BasketWithItemsFactory,
    CashierFactory,
    PaymentMethodFactory,
    ProductFactory,
)


@freezegun.freeze_time("2022-09-24 19:01:00+0200")
def test_cashier_create_and_update_basket(  # noqa: PLR0915
    live_server: LiveServer,
    selenium: WebDriver,
):
    wait = WebDriverWait(selenium, 10)
    assert Basket.objects.count() == 0

    # Setup data
    cashier = CashierFactory()
    products = [
        ProductFactory(),
        ProductFactory(),
        ProductFactory(),
    ]
    unpriced_products = [
        ProductFactory(unit_price_cents=0),
        ProductFactory(unit_price_cents=0),
        ProductFactory(unit_price_cents=0),
    ]
    payment_methods = [
        PaymentMethodFactory(),
        PaymentMethodFactory(),
        PaymentMethodFactory(),
    ]

    login(live_server, selenium, cashier)

    # Assert products are displayed
    redirect_url = live_reverse(live_server, "purchase:new")
    wait.until(lambda driver: driver.current_url == redirect_url)
    displayed_products = selenium.find_elements(By.CSS_SELECTOR, ".card.h-100")
    assert len(displayed_products) == len(products)
    for product, displayed_product in zip(products, displayed_products, strict=True):
        assert (
            product.name
            == displayed_product.find_element(By.CLASS_NAME, "card-title").text
        )

    # Assert quantity of all products is 0
    for displayed_product in displayed_products:
        quantity_input = displayed_product.find_element(By.CLASS_NAME, "numberinput")
        quantity = int(quantity_input.get_attribute("value"))
        assert quantity == 0

    # Click on - on product 1
    displayed_product = displayed_products[0]
    displayed_product.find_element(By.CLASS_NAME, "btn-danger").click()

    # Assert quantity is still 0
    quantity_input = displayed_product.find_element(By.CLASS_NAME, "numberinput")
    quantity = int(quantity_input.get_attribute("value"))
    assert quantity == 0

    # Click two times on + on product 1
    button_plus = displayed_product.find_element(By.CLASS_NAME, "btn-success")
    button_plus.click()
    button_plus.click()

    # Assert quantity is 2
    quantity_input = displayed_product.find_element(By.CLASS_NAME, "numberinput")
    quantity = int(quantity_input.get_attribute("value"))
    assert quantity == 2

    # Adjust manually quantity for product 2: 4
    displayed_product = displayed_products[1]
    quantity_input = displayed_product.find_element(By.CLASS_NAME, "numberinput")
    chain = ActionChains(selenium)
    chain.double_click(quantity_input).perform()
    quantity_input.send_keys("4")

    # Add non-fixed priced product
    select = Select(selenium.find_element(By.ID, "product_to_add"))
    unpriced_product = unpriced_products[1]
    select.select_by_value(str(unpriced_product.pk))
    selenium.find_element(By.ID, "add_product").click()
    selenium.find_element(By.ID, "add_product").click()
    elements = selenium.find_elements(
        By.CSS_SELECTOR,
        f"[data-product-id='{unpriced_product.pk}']",
    )
    for elem in elements:
        assert (
            elem.find_element(By.CLASS_NAME, "card-title").text == unpriced_product.name
        )
    price_input = elements[0].find_element(By.CLASS_NAME, "numberinput")
    chain = ActionChains(selenium)
    chain.double_click(price_input).perform()
    price_input.send_keys("237")
    price_input = elements[1].find_element(By.CLASS_NAME, "numberinput")
    chain = ActionChains(selenium)
    chain.double_click(price_input).perform()
    price_input.send_keys("401")

    # Don't add payment method
    # Save
    selenium.find_element(By.ID, "submit-id-submit").click()

    # Assert entries saved in DB (new basket with proper products)
    assert Basket.objects.count() == 1
    basket = Basket.objects.priced().first()
    assert basket.payment_method is None
    assert basket.items.count() == 4
    assert basket.items.get(product=products[0]).quantity == 2
    assert (
        basket.items.get(product=products[0]).unit_price_cents
        == products[0].unit_price_cents
    )
    assert basket.items.get(product=products[1]).quantity == 4
    assert (
        basket.items.get(product=products[1]).unit_price_cents
        == products[1].unit_price_cents
    )
    unpriced_basket_items = basket.items.filter(product=unpriced_product).order_by(
        "unit_price_cents",
    )
    assert len(unpriced_basket_items) == 2
    assert unpriced_basket_items[0].quantity == 1
    assert unpriced_basket_items[0].unit_price_cents == 237
    assert unpriced_basket_items[1].quantity == 1
    assert unpriced_basket_items[1].unit_price_cents == 401

    # Assert redirected to basket update view
    redirect_url = live_reverse(live_server, "purchase:update", pk=basket.pk)
    wait.until(lambda driver: driver.current_url == redirect_url)

    # Assert message in green for successful basket creation
    created_message = selenium.find_element(By.CSS_SELECTOR, ".messages .alert-success")
    assert created_message.text == "Panier correctement créé."

    # Assert message in red for missing payment method
    missing_payment = selenium.find_element(By.CSS_SELECTOR, ".alert.alert-danger")
    assert missing_payment.text == "Moyen de paiement manquant."

    # Assert ID, price, date & product quantities
    # Selected products have a green background
    title = selenium.find_element(By.TAG_NAME, "h1")
    assert title.text == f"Panier n°{basket.pk} {basket.price/100:.2f}€"
    date = selenium.find_element(By.CLASS_NAME, "metadata")
    assert date.text == "24 septembre 2022 19:01"

    displayed_products = selenium.find_elements(By.CSS_SELECTOR, ".card.h-100")
    displayed_product = displayed_products[0]
    assert "bg-success" in displayed_product.get_attribute("class")
    quantity_input = displayed_product.find_element(By.CLASS_NAME, "numberinput")
    quantity = int(quantity_input.get_attribute("value"))
    assert quantity == 2
    displayed_product = displayed_products[1]
    assert "bg-success" in displayed_product.get_attribute("class")
    quantity_input = displayed_product.find_element(By.CLASS_NAME, "numberinput")
    quantity = int(quantity_input.get_attribute("value"))
    assert quantity == 4
    displayed_product = displayed_products[2]
    assert "bg-success" not in displayed_product.get_attribute("class")
    quantity_input = displayed_product.find_element(By.CLASS_NAME, "numberinput")
    quantity = int(quantity_input.get_attribute("value"))
    assert quantity == 0

    elements = selenium.find_elements(
        By.CSS_SELECTOR,
        f"[data-product-id='{unpriced_product.pk}']",
    )
    assert len(elements) == 2, "Unpriced products should be displayed"

    # Click on - on product 2
    displayed_product = displayed_products[1]
    displayed_product.find_element(By.CLASS_NAME, "btn-danger").click()

    # Assert quantity is 3
    quantity_input = displayed_product.find_element(By.CLASS_NAME, "numberinput")
    quantity = int(quantity_input.get_attribute("value"))
    assert quantity == 3

    # Add payment method
    selenium.find_element(By.TAG_NAME, "html").send_keys(Keys.END)
    time.sleep(1)
    selenium.find_element(By.ID, f"id_payment_method_{payment_methods[1].pk}").click()

    # Save
    selenium.find_element(By.ID, "submit-id-submit").click()

    # Assert changed in DB
    assert Basket.objects.count() == 1
    basket = Basket.objects.priced().first()
    assert basket.payment_method == payment_methods[1]
    assert basket.items.count() == 4
    assert basket.items.get(product=products[0]).quantity == 2
    assert (
        basket.items.get(product=products[0]).unit_price_cents
        == products[0].unit_price_cents
    )
    assert basket.items.get(product=products[1]).quantity == 3
    assert (
        basket.items.get(product=products[1]).unit_price_cents
        == products[1].unit_price_cents
    )
    unpriced_basket_items = basket.items.filter(product=unpriced_product).order_by(
        "unit_price_cents",
    )
    assert len(unpriced_basket_items) == 2
    assert unpriced_basket_items[0].quantity == 1
    assert unpriced_basket_items[0].unit_price_cents == 237
    assert unpriced_basket_items[1].quantity == 1
    assert unpriced_basket_items[1].unit_price_cents == 401

    # Assert redirected to same view
    redirect_url = live_reverse(live_server, "purchase:update", pk=basket.pk)
    wait.until(lambda driver: driver.current_url == redirect_url)

    # Assert message in green for successful basket update
    created_message = selenium.find_element(By.CSS_SELECTOR, ".messages .alert-success")
    assert created_message.text == "Panier correctement modifié."

    # Assert no more red message
    missing_payment = selenium.find_elements(By.CSS_SELECTOR, ".alert.alert-danger")
    assert len(missing_payment) == 0


def login(
    live_server: LiveServer,
    selenium: WebDriver,
    cashier: User,
    url: str = "/",
) -> None:
    # Go to page
    url = live_url(live_server, url)
    selenium.get(url)
    # Login
    selenium.find_element(By.ID, "id_username").send_keys(cashier.username)
    selenium.find_element(By.ID, "id_password").send_keys(USER_PASSWORD)
    selenium.find_element(By.ID, "id_password").send_keys(Keys.RETURN)


@freezegun.freeze_time("2022-09-24 19:03:00+0200")
def test_baskets_list(live_server: LiveServer, selenium: WebDriver):
    wait = WebDriverWait(selenium, 10)

    # Setup test data
    cashier = CashierFactory()
    _ = [
        ProductFactory(),
        ProductFactory(),
        ProductFactory(),
    ]
    _ = [
        PaymentMethodFactory(),
        PaymentMethodFactory(),
        PaymentMethodFactory(),
    ]
    with freezegun.freeze_time("2022-09-24 19:01:00+0200"):
        basket_with_payment_method = BasketWithItemsFactory()
        basket_with_payment_method = Basket.objects.priced().get(
            pk=basket_with_payment_method.pk,
        )
    with freezegun.freeze_time("2022-09-24 19:02:00+0200"):
        basket_no_payment_method = BasketWithItemsFactory(payment_method=None)
        basket_no_payment_method = Basket.objects.priced().get(
            pk=basket_no_payment_method.pk,
        )

    # Login
    url = reverse("purchase:list")
    login(live_server, selenium, cashier, url)

    # Assert first basket (last created) has yellow background
    # Assert basket info displayed
    displayed_baskets = selenium.find_elements(By.CSS_SELECTOR, ".card.h-100")
    first_basket = displayed_baskets[0]
    assert "bg-warning" in first_basket.get_attribute("class")
    text = first_basket.text.replace("\n", " ")
    assert f"n°{basket_no_payment_method.pk} " in text
    expected_articles_count = basket_no_payment_method.items.count()
    assert f" {expected_articles_count} article" in text
    expected_price = basket_no_payment_method.price / 100
    assert f" {expected_price:.2f}€" in text
    expected_payment_method = "-"
    assert f" {expected_payment_method} " in text
    assert "19:02" in text

    # Assert second basket (first created) doesn't have yellow background
    # Assert basket info displayed including payment method
    second_basket = displayed_baskets[1]
    assert "bg-warning" not in second_basket.get_attribute("class")
    text = second_basket.text.replace("\n", " ")
    assert f"n°{basket_with_payment_method.pk} " in text
    expected_articles_count = basket_with_payment_method.items.count()
    assert f" {expected_articles_count} article" in text
    expected_price = basket_with_payment_method.price / 100
    assert f" {expected_price:.2f}€" in text
    expected_payment_method = basket_with_payment_method.payment_method.name
    assert f" {expected_payment_method} " in text
    assert "19:01" in text

    # Click on delete on second basket
    second_basket.find_element(By.CLASS_NAME, "btn-danger").click()

    # Confirm deletion
    selenium.find_element(By.CLASS_NAME, "btn-danger").click()

    # Assert object deleted in DB
    assert Basket.objects.count() == 1
    assert Basket.objects.first() == basket_no_payment_method

    # Assert redirected to list view
    wait.until(
        lambda driver: driver.current_url == live_reverse(live_server, "purchase:list"),
    )

    # Click on edit on remaining basket
    displayed_baskets = selenium.find_elements(By.CSS_SELECTOR, ".card.h-100")
    displayed_baskets[0].find_element(By.CLASS_NAME, "btn-primary").click()

    # Assert redirected to edit view
    redirect_url = live_reverse(
        live_server,
        "purchase:update",
        pk=basket_no_payment_method.pk,
    )
    wait.until(lambda driver: driver.current_url == redirect_url)


def live_reverse(live_server: LiveServer, url_name: str, **kwargs) -> str:
    path = reverse(url_name, kwargs=kwargs)
    return live_url(live_server, path)


def live_url(live_server: LiveServer, path: str) -> str:
    return live_server.url + path
