/*
 * Mailing List Javascript
 *
 */
var mailingListHandler = (function() {
  var enableRadioButtons = function() {
    $("div.btn-group label.mailing-list").on('click', function() {
      var $label = $(this);
      var clickedList = $label.find('input').data('choice');
      var recruiterId = $label.parents('tr').attr('id');
      var request = updateRecruiterMailingList(recruiterId, clickedList);

      request
        .fail(function(jqXHR, textStatus, errorThrown) {
          console.error('There was an error.');
          $label.removeClass('active');
        });
    });
  };

  // Private Methods
  var updateRecruiterMailingList = function(recruiterId, mailingList) {
    var url = '/admin/recruiter/mailing-list/';
    var data = {
      recruiter_id: recruiterId,
      mailing_list: mailingList,
      csrf_token: $('body').data('csrf-token')
    };

    return $.ajax({
      type: "POST",
      url: url,
      data: data,
      dataType: 'json'
    });
  };

  // Public API
  return {
    enableRadioButtons: enableRadioButtons
  };
})();

$(document).ready(function() {
  mailingListHandler.enableRadioButtons();
});
