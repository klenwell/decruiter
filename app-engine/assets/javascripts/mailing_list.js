/*
 * Mailing List Javascript
 *
 */
var mailingListHandler = (function() {
  var enableRadioButtons = function() {
    $("div.btn-group label.mailing-list").on('click', function() {
      var clickedList = $(this).find('input').data('choice');
      console.debug('clicked', clickedList, $(this));
    });
  };

  // Private Methods
  var updateRecruiterMailingList = function() {

  };

  // Public API
  return {
    enableRadioButtons: enableRadioButtons
  };
})();

$(document).ready(function() {
  mailingListHandler.enableRadioButtons();
});
