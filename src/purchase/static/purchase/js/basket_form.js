window.incrementValue = function (id) {
    let value = parseInt(document.getElementById(id).value);
    value = isNaN(value) ? 0 : value;
    value++;
    document.getElementById(id).value = value;
};

window.decrementValue = function (id) {
    let value = parseInt(document.getElementById(id).value);
    value = isNaN(value) ? 0 : value;
    value--;
    value = value < 0 ? 0 : value;
    document.getElementById(id).value = value;
};
