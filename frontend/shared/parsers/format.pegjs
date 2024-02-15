Statement = sections:Section* {return sections.join("")}

Section = Placeholder / $(!"${" .)+

Placeholder = "${" identifier:Identifier "}" {return options.getValue(identifier)}

Identifier = $[a-z _-]i+