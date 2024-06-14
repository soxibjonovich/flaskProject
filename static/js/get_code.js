document.addEventListener("DOMContentLoaded", function() {
    // Select the button element
    const button = document.getElementById('delayedButton');

    // Function to enable the button
    function enableButton() {
        button.disabled = false;
    }

    // Wait for 15 seconds before enabling the button
    setTimeout(enableButton, 15000);
});
