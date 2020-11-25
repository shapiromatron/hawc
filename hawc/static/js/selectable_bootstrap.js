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
  return $("<button>").addClass("btn btn-primary btn-sm dropdown-toggle mb-2");
};

$.ui.djselectable.prototype._removeButtonTemplate = function (item) {
  var icon = $("<i>").addClass("icon-remove-sign");
  // Return button link with the chosen icon
  return $("<a>").append(icon).addClass("btn btn-small pull-right");
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
