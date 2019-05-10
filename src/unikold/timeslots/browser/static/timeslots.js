require([
  'jquery'
], function($) {
  $(document).ready( function() {
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
