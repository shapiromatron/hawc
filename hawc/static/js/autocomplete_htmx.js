(function () {
  $.fn.getFormPrefix = function () {
    /* Get the form prefix for a field.
     *
     * For example:
     *
     *     $(':input[name$=owner]').getFormsetPrefix()
     *
     * Would return an empty string for an input with name 'owner' but would return
     * 'inline_model-0-' for an input named 'inline_model-0-owner'.
     */
    var parts = $(this).attr("name").split("-");
    var prefix = "";

    for (var i in parts) {
      var testPrefix = parts.slice(0, -i).join("-");
      if (!testPrefix.length) continue;
      testPrefix += "-";

      var result = $(":input[name^=" + testPrefix + "]");

      if (result.length) {
        return testPrefix;
      }
    }

    return "";
  };

  $.fn.getFormPrefixes = function () {
    /*
     * Get the form prefixes for a field, from the most specific to the least.
     *
     * For example:
     *
     *      $(':input[name$=owner]').getFormPrefixes()
     *
     * Would return:
     * - [''] for an input named 'owner'.
     * - ['inline_model-0-', ''] for an input named 'inline_model-0-owner' (i.e. nested with a nested inline).
     * - ['sections-0-items-0-', 'sections-0-', ''] for an input named 'sections-0-items-0-product'
     *   (i.e. nested multiple time with django-nested-admin).
     */
    var parts = $(this).attr("name").split("-").slice(0, -1);
    var prefixes = [];

    for (i = 0; i < parts.length; i += 2) {
      var testPrefix = parts.slice(0, -i || parts.length).join("-");
      if (!testPrefix.length) continue;

      testPrefix += "-";

      var result = $(":input[name^=" + testPrefix + "]");

      if (result.length) prefixes.push(testPrefix);
    }

    prefixes.push("");

    return prefixes;
  };

  /*
   * This ensures the Language file is loaded and passes it our jQuery.
   */
  if (typeof dalLoadLanguage !== "undefined") {
    dalLoadLanguage($);
  } else {
    document.addEventListener("dal-language-loaded", function (e) {
      // `e.lang` is the language that was loaded.
      dalLoadLanguage($);
    });
  }

  // Fire init event for yl.registerFunction() execution.
  var event = new CustomEvent("dal-init-function");
  document.dispatchEvent(event);

  $.fn.excludeTemplateForms = function () {
    // exclude elements that contain '__prefix__' in their id
    // these are used by django formsets for template forms
    return this.not("[id*=__prefix__]").filter(function () {
      // exclude elements that contain '-empty-' in their ids
      // these are used by django-nested-admin for nested template formsets
      // note that the filter also ensures that 'empty' is not actually the related_name for some relation
      // by ensuring that it is not surrounded by numbers on both sides
      return !this.id.match(/-empty-/) || this.id.match(/-\d+-empty-\d+-/);
    });
  };

  /**
   * Initialize a field element. This function calls the registered init function
   * and ensures that the element is only initialized once.
   *
   * @param element The field to be initialized
   */
  function initialize(element) {
    if (typeof element === "undefined" || typeof element === "number") {
      element = this;
    }

    // The DAL function to execute.
    var dalFunction = $(element).attr("data-autocomplete-light-function");

    if (
      yl.functions.hasOwnProperty(dalFunction) &&
      typeof yl.functions[dalFunction] == "function"
    ) {
      // If the function has been registered call it.
      yl.functions[dalFunction]($, element);
    } else if (yl.functions.hasOwnProperty(dalFunction)) {
      // If the function exists but has not been registered wait for it to be registered.
      window.addEventListener(
        "dal-function-registered." + dalFunction,
        function (e) {
          yl.functions[dalFunction]($, element);
        }
      );
    } else {
      // Otherwise notify that the function should be registered.
      console.warn(
        'Your custom DAL function "' +
          dalFunction +
          '" uses a deprecated event listener that will be removed in future versions. https://django-autocomplete-light.readthedocs.io/en/master/tutorial.html#overriding-javascript-code'
      );
    }

    // Fire init event for custom function execution.
    // DEPRECATED
    $(element).trigger("autocompleteLightInitialize");

    // creates and dispatches the event to notify of the initialization completed
    var dalElementInitializedEvent = new CustomEvent(
      "dal-element-initialized",
      {
        detail: {
          element: element,
        },
      }
    );

    document.dispatchEvent(dalElementInitializedEvent);
  }
  htmx.onLoad(function (el) {
    $(el)
      .find("[data-autocomplete-light-function]")
      .excludeTemplateForms()
      .each(initialize);
  });
})();
