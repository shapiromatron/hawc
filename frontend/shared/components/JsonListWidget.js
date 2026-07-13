function JsonListWidget() {
	this._initWidgetInDiv = function(widgetDiv, prefix) {
		this.prefix = prefix;
		this.widgetDiv = widgetDiv;
		this.schema = JSON.parse(widgetDiv.attr("data-schema"));

		let hook = this;
		this.widgetDiv.find("button").click(function() {
			hook.addRow();
			return false;
		});

		this.widgetDiv.find(".data-row, .template-row").each(function() {
			let dataRow = $(this);
			let controlCell = dataRow.find(".control-cell");
			let deleteBtn = $("<button/>").html("Delete").appendTo(controlCell);

			deleteBtn.click(function() {
				hook.onDeleteRowButtonClicked($(this));
				return false;
			});

			if (!dataRow.hasClass("template-row")) {
				hook.setDependentVisibilityForRow(dataRow);
			}
		});
	};

	this.setDependentVisibilityForRow = function(row) {
		// find the elements in the schema that only show in certain scenarios
		let showHideHelper = function(pfw, cfw, v) {
			if (pfw.find("input,select").val() == v) {
				cfw.removeClass("hidden");
			} else {
				cfw.addClass("hidden");
				cfw.find("input,select").val("");
			}
		};


		for (let i = 0 ; i < this.schema.length ; i++) {
			let fieldDef = this.schema[i];
			if (fieldDef["only_show_if"] !== undefined) {
				let childFieldWrapper = row.find("[data-for-field-name='" + fieldDef["name"] + "']");
				let parentFieldWrapper = row.find("[data-for-field-name='" + fieldDef["only_show_if"]["field"] + "']");

				parentFieldWrapper.change(function() {
					showHideHelper(parentFieldWrapper, childFieldWrapper, fieldDef["only_show_if"]["val"]);
				});
				showHideHelper(parentFieldWrapper, childFieldWrapper, fieldDef["only_show_if"]["val"]);
			}
		}
	};

	this.onDeleteRowButtonClicked = function(clickedButton) {
		let rowIdx = $(clickedButton).parents(".data-row").index(".data-row");
		this.deleteRowAtIndex(rowIdx);
	};

	/*
	 *
	 * delete a row and reorder any others as necessary
	 *
	 */
	this.deleteRowAtIndex = function(rowIdx) {
		// remove the row you clicked on...
		this.widgetDiv.find(".data-row:eq(" + rowIdx + ")").remove();

		let hook = this;

		// input types/attributes to update when a row is deleted...
		let fixers = [
			[ "label", "for" ],
			[ "input,select", "id" ],
			[ "input,select", "name" ],
		];
		
		// and reset the indices for any row that needs it
		setTimeout(function() {
			let newIdx = 0;
			hook.widgetDiv.find(".data-row").each(function() {
				let firstCellInRow = $(this).find(".field-cell:eq(0)");
				let cellName = firstCellInRow.find("input,select").attr("name");

				let lastDashIdx = cellName.lastIndexOf("-");
				let currIdx = Number(cellName.substring(lastDashIdx+1));
				let val = firstCellInRow.find("input").val();
				if (currIdx != newIdx) {
					$(this).find(".field-cell").each(function() {
						let cell = $(this);

						for (let i = 0 ; i < fixers.length ; i++) {
							let fixer = fixers[i];
							let selectorToFix = fixer[0];
							let attribToFix = fixer[1];

							let domEl = cell.find(selectorToFix);
							let currAttribVal = domEl.attr(attribToFix);
							let finalDashIdx = currAttribVal.lastIndexOf("-");
							let correctedVal = currAttribVal.substring(0, finalDashIdx+1) + newIdx;
							domEl.attr(attribToFix, correctedVal);
						}
					});
				}
				newIdx++;
			});
		}, 25);
	};

	/*
	 *
	 * add UI/listeners for the new row
	 *
	 */
	this.addRow = function() {
		let numElements = this.widgetDiv.find(".data-row").length;

		let fixers = [
			[ "label", "for" ],
			[ "input,select", "id" ],
			[ "input,select", "name" ],
		];

		let newRow = this.widgetDiv.find(".template-row:eq(0)").clone().addClass("data-row").removeClass("template-row");

		// set up delete btn
		let hook = this;
		newRow.find(".control-cell button").click(function() {
			hook.onDeleteRowButtonClicked($(this));
			return false;
		});

		newRow.find(".field-cell").each(function() {
			let cell = $(this);

			for (let i = 0 ; i < fixers.length ; i++) {
				let fixer = fixers[i];
				let selectorToFix = fixer[0];
				let attribToFix = fixer[1];

				let domEl = cell.find(selectorToFix);
				if (selectorToFix != "label") {
					domEl.val(""); // wipe the input
				}
				let currAttribVal = domEl.attr(attribToFix);
				let finalDashIdx = currAttribVal.lastIndexOf("-");
				let correctedVal = currAttribVal.substring(0, finalDashIdx+1) + numElements;
				domEl.attr(attribToFix, correctedVal);
			}
		});

		this.setDependentVisibilityForRow(newRow);





	/*


<div class="data-row">
	<div class="field-cell">
		<label for="id_testdesign-1-concentrations_tested-value-0">value: </label>
		<input type="number" id="id_testdesign-1-concentrations_tested-value-0" name="testdesign-1-concentrations_tested-value-0" value="0.9">
	</div>
	<div class="field-cell">
		<label for="id_testdesign-1-concentrations_tested-units-0">units: </label>
		<select id="id_testdesign-1-concentrations_tested-units-0" name="testdesign-1-concentrations_tested-units-0">
			<option value="OTH">other</option>
		</select>
	</div>
	<div class="field-cell">
		<label for="id_testdesign-1-concentrations_tested-units_other-0">units_other: </label>
		<input type="text" id="id_testdesign-1-concentrations_tested-units_other-0" name="testdesign-1-concentrations_tested-units_other-0" value="">
	</div>
	<div class="control-cell">
		<button>Delete</button>
	</div>
</div>


	 
	 
	 */
		/*
		let fixers = [
			[ "label", "for" ],
			[ "input,select", "id" ],
			[ "input,select", "name" ],
		];

		let newRow = this.widgetDiv.find(".data-row:eq(0)").clone();

		// set up delete btn
		let hook = this;
		newRow.find(".control-cell button").click(function() {
			hook.onDeleteRowButtonClicked($(this));
			return false;
		});

		newRow.find(".field-cell").each(function() {
			let cell = $(this);

			for (let i = 0 ; i < fixers.length ; i++) {
				let fixer = fixers[i];
				let selectorToFix = fixer[0];
				let attribToFix = fixer[1];

				let domEl = cell.find(selectorToFix);
				if (selectorToFix != "label") {
					domEl.val(""); // wipe the input
				}
				let currAttribVal = domEl.attr(attribToFix);
				let finalDashIdx = currAttribVal.lastIndexOf("-");
				let correctedVal = currAttribVal.substring(0, finalDashIdx+1) + numElements;
				domEl.attr(attribToFix, correctedVal);
			}
		});
		*/

		newRow.insertBefore(this.widgetDiv.find(".control-row"));
	};

	this.initializeWidgetUi = function(fieldPrefix) {
		let widgetDiv = $("div.hawc-json-list-widget[data-prefix='" + fieldPrefix + "']");
		this._initWidgetInDiv(widgetDiv, fieldPrefix);
	};

}

export default {
	widget_class: JsonListWidget
}
