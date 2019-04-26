require([
  'jquery'
], function($) {
  $(document).ready( function() {
    $('#formSubmitTimeslots, #formCancelTimeslots').submit( function(el) {
      $(this).find('button[type="submit"]').addClass('disabled');
      return true;
    });
    function checkCancelReservations() {
      if ( $('input[name=selectedSlot]:checked').val() ) {
        $('#btnCancelReservations').show();
      } else {
        $('#btnCancelReservations').hide();
      }
    }
    checkCancelReservations();
    $('input[name=selectedSlot]').change( checkCancelReservations );
  });
});
