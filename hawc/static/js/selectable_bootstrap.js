$.ui.djselectable.prototype.options.defaultClasses = {
  text: "form-control mb-2",
  combobox: "form-control mb-2",
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
