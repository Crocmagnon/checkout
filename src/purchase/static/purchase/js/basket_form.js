window.incrementValue = function (id) {
    const element = document.getElementById(id);
    let value = parseInt(element.value);
    value = isNaN(value) ? 0 : value;
    value++;
    element.value = value;

    window.dispatchChanged(element);
};

window.decrementValue = function (id) {
    const element = document.getElementById(id);
    let value = parseInt(element.value);
    value = isNaN(value) ? 0 : value;
    value--;
    value = value < 0 ? 0 : value;
    element.value = value;

    window.dispatchChanged(element);
};

window.dispatchChanged = function (element) {
    const event = new Event("change", { bubbles: true });
    element.dispatchEvent(event);
};

window.onUpdateQuantity = function (event) {
    const { target } = event;
    const parent = target.closest(".card");
    const classes = ["bg-success", "text-white"];
    if (target.value > 0) {
        parent.classList.add(...classes);
    } else {
        parent.classList.remove(...classes);
    }
};

window.setupEventsListener = function () {
    const cards = document.querySelectorAll(".card input");
    cards.forEach((item) => {
        item.addEventListener("change", window.onUpdateQuantity);
        item.addEventListener("keyup", window.onUpdateQuantity);
    });
};

document.addEventListener("newUnpriced", function () {
    window.setupEventsListener();
});

window.setupEventsListener();
