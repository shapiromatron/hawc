function JsonListWidget() {
	this._initWidgetInDiv = function(widgetDiv, prefix) {
		this.prefix = prefix;
		this.widgetDiv = widgetDiv;
		this.schema = JSON.parse(widgetDiv.attr("data-schema"));
		console.log("INIT:", this.schema);

		let hook = this;
		this.widgetDiv.find("button").click(function() {
			hook.addRow();
			return false;
		});

		this.widgetDiv.find(".data-row").each(function() {
			let dataRow = $(this);
			let controlCell = dataRow.find(".control-cell");
			let deleteBtn = $("<button/>").html("Delete").appendTo(controlCell);

			deleteBtn.click(function() {
				hook.onDeleteRowButtonClicked($(this));
				return false;
			});
		});
	};

	this.onDeleteRowButtonClicked = function(clickedButton) {
		let rowIdx = $(clickedButton).parents(".data-row").index();
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
				let cellName = firstCellInRow.find("input").attr("name");

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
							console.log("  [" + selectorToFix + "]/[" + attribToFix + "]: FIX '" + currAttribVal + "' -> '" + correctedVal + "'");
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
		// console.log(this.schema);

		let numElements = this.widgetDiv.find(".data-row").length;

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
