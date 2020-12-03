$.ui.djselectable.prototype.options.defaultClasses = {
  text: "form-control mb-2",
  combobox: "form-control mb-2",
};

$.ui.djselectable.prototype._comboButtonTemplate = function (input) {
  // Wrap input with input-group
  $(input)
    .wrap('<div class="input-group-append" />')
    .wrap('<div class="input-group" />');
  // Return button
  return $("<button>").addClass(
    "btn btn-secondary btn-sm dropdown-toggle mb-2"
  );
};

$.ui.djselectable.prototype._removeButtonTemplate = function (item) {
  var icon = $('<i class="fa fa-times-circle"></i>');
  // Return button link with the chosen icon
  return $("<button type='button' class='btn btn-sm btn-secondary px-2 py-0' title='Remove item'>")
    .append(icon)
    .addClass("float-right");
};

(function () {
  let _create = $.ui.menu.prototype._create;
  $.ui.menu.prototype._create = function () {
    _create.apply(this);
    $(this.element).removeClass("ui-widget");
  };

  let _initDeck = $.ui.djselectable.prototype._initDeck;
  $.ui.djselectable.prototype._initDeck = function () {
    _initDeck.apply(this);
    this.deck.removeClass("ui-widget");
  };
})();
