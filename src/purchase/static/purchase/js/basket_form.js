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
