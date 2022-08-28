document.addEventListener("dal-init-function", function () {
  yl.registerFunction("select2text", function ($, element) {
    var $element = $(element);

    // Templating helper
    function template(text, is_html) {
      if (is_html) {
        var $result = $("<span>");
        $result.html(text);
        return $result;
      } else {
        return text;
      }
    }

    function result_template(item) {
      var is_data_html =
        $element.attr("data-html") !== undefined ||
        $element.attr("data-result-html") !== undefined;

      if (item.create_id) {
        var $result = $("<span>").addClass("dal-create");
        if (is_data_html) {
          return $result.html(item.text);
        } else {
          return $result.text(item.text);
        }
      } else {
        return template(item.text, is_data_html);
      }
    }

    function selected_template(item) {
      if (item.selected_text !== undefined) {
        return template(
          item.selected_text,
          $element.attr("data-html") !== undefined ||
            $element.attr("data-selected-html") !== undefined
        );
      } else {
        return result_template(item);
      }
    }

    var ajax = null;
    if ($element.attr("data-autocomplete-light-url")) {
      ajax = {
        url: $element.attr("data-autocomplete-light-url"),
        dataType: "json",
        delay: 1000,

        data: function (params) {
          var data = {
            q: params.term, // search term
            page: params.page,
            create: false,
            forward: yl.getForwards($element),
          };

          return data;
        },
        transport: function (params, success, failure) {
            var $input = $element.data("select2").dropdown.$search,
            $request = $.ajax(params);

            $request.then(function(data){
                // add current input to results
                data.results.unshift({id:$input.val(),text:$input.val()})
                return success(data);
            });
            $request.fail(failure);

            return $request;
        },
        processResults: function (data, page) {
            $.each(data.results, function (index, value) {
                value.id = value.text;
            });

            return data;
        },
        cache: true,
      };
    }

    $element.select2({
      debug: true,
      containerCssClass: ":all:",
      placeholder: $element.attr("data-placeholder") || "",
      language: $element.attr("data-autocomplete-light-language"),
      minimumInputLength: $element.attr("data-minimum-input-length") || 0,
      allowClear: !$element.is("[required]"),
      templateResult: result_template,
      templateSelection: selected_template,
      ajax: ajax,
      with: null,
    });

    var $input = $element.data("select2").dropdown.$search;

    $element.data("select2").listeners["query"].unshift(function (e) {
      $element.data("select2").trigger("results:all", {
        data: {
          results: [{ id: $input.val(), text: $input.val(), selected: true }],
        },
        query: {},
      });
    });
    $input.on("input", function(e){
      $element.empty();
      $element.append(new Option($input.val(), $input.val(), false, true));
    })
    $element.on("select2:open", function(e){
      // not working as intended; trying to retrigger query with old input
      // manually triggering query here still performs initial query for some reason
      $input.val($element.val()).trigger("input");
    });
  });
});
