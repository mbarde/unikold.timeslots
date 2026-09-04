document.addEventListener('DOMContentLoaded', function () {
  function checkCancelReservations() {
    var button = document.getElementById('btnCancelReservations');
    if (!button) {
      return;
    }
    var checked = document.querySelector('input[name="selectedSlot"]:checked');
    button.style.display = checked ? '' : 'none';
  }

  checkCancelReservations();
  document.querySelectorAll('input[name="selectedSlot"]').forEach(function (input) {
    input.addEventListener('change', checkCancelReservations);
  });
});
