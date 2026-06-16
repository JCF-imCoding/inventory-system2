// 🔹 Show item details popup
function showDetails(name, description, category) {
    document.getElementById("popup-name").innerText = name;
    document.getElementById("popup-description").innerText = description;
    document.getElementById("popup-category").innerText = category;

    document.getElementById("popup").style.display = "block";
}


// 🔹 Close item details popup
function closePopup() {
    document.getElementById("popup").style.display = "none";
}

// 🔹 Show "item added to cart" confirmation popup
function showCartPopup() {
    document.getElementById("cart-popup").style.display = "block";
}

// 🔹 Close cart confirmation popup
function closeCartPopup() {
    document.getElementById("cart-popup").style.display = "none";
}

// 🔹 Show checkout completion popup
function showCheckoutPopup() {
    document.getElementById("checkout-popup").style.display = "block";
}

// 🔹 Close checkout popup
function closeCheckoutPopup() {
    document.getElementById("checkout-popup").style.display = "none";
}

// 🔹 Show return confirmation popup
function showReturnPopup() {
    document.getElementById("return-popup").style.display = "block";
}

// 🔹 Close return confirmation popup
function closeReturnPopup() {
    document.getElementById("return-popup").style.display = "none";
}

// 🔹 Redirect user to home page
function goHome() {
    window.location.href = "/home-page";
}

// 🔹 Adjust return quantity using + / - buttons
function adjustReturn(button, change) {
    // Find the input next to the button
    const input = button.parentElement.querySelector('input[type="number"]');

    let current = parseInt(input.value);
    let min = parseInt(input.min);
    let max = parseInt(input.max);

    let newValue = current + change;

    // ✅ Clamp between min and max
    if (newValue < min) newValue = min;
    if (newValue > max) newValue = max;

    input.value = newValue;
}

// 🔹 Close error popup
function closeErrorPopup() {
    document.getElementById("error-popup").style.display = "none";
}
