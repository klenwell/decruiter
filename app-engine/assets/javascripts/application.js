/*
 * Applicaton Javascript
 *
 * Global javascript loaded by default with base template. Try to keep this lean
 * and relevant. Use controller-specific files for more localized functionality.
 */
var applicationHandler = (function() {
  var enableClickableRows = function() {
    $("tr.clickable").click(function() {
      window.document.location = $(this).data("href");
    });
  };

  var enableFormTriggerLocks = function() {
    $('form.trigger-lock').submit(function() {
      var $submitButton = $(this).find('input.trigger, button.trigger');
      $submitButton.prop('disabled', true);
    });
  };

  var enablePostableLinks = function() {
    /*
     * Builds form dynamically from anchor link with postable class based on
     * data attributes. Requires data-action attribute. For example:
     *
     * <a class="btn btn-primary postable" data-action="/endpoint/" input_data_id="1" d>Label</a>
     */
    var selector = "a.postable, button.postable";

    $(selector).click(function() {
      var action = $(this).data('action');
      var confirmation = $(this).data('confirm');

      if ( confirmation && !confirm(confirmation) ) {
        return false;
      }

      // Build dynamic form.
      var $form = $('<form />', { method: 'POST', action: action });

      // Add hidden input field from data-input_field_name=value attrs.
      $.each($(this).data(), function(key, value) {
        var splits = key.split('_');

        if ( splits[0] !== 'input' ) {
          return; // continue
        }

        splits.shift();
        var field = splits.join('_');
        var $input = $('<input />', { type: 'hidden', id: field, name: field, value: value });
        $form.append($input);
      });

      // Prevent double-submits and submit.
      $(this).off('click');
      $form.submit();
    });
  };

  var humanizeDateTimeFields = function() {
    $('.momentize').each(function(index, element) {
      var sourceDatetime = $(element).data('datetime');
      var sourceDate = $(element).data('date');

      if ( sourceDatetime ) {
        var momentObj = moment.utc(sourceDatetime);
      }
      else if ( sourceDate ) {
        var momentObj = moment.utc(sourceDate);
      }
      else {
        return;
      }

      var now = moment.utc();
      var timeDelta = momentObj.diff(now);
      var humanized = moment.duration(timeDelta).humanize(true);

      $(element).text(humanized);
    });
  };

  // Public API
  return {
    enableClickableRows: enableClickableRows,
    enableFormTriggerLocks: enableFormTriggerLocks,
    enablePostableLinks: enablePostableLinks,
    humanizeDateTimeFields: humanizeDateTimeFields
  };
})();

$(document).ready(function() {
  // These are the things that happen on every page load.
  applicationHandler.enableClickableRows();
  applicationHandler.enableFormTriggerLocks();
  applicationHandler.enablePostableLinks();
  applicationHandler.humanizeDateTimeFields();
});
