Format = Ternary / Statement

// Ternary
// ==========
Ternary = c:Condition "?" t1:TernaryTrue ":" t2:TernaryFalse { return c ? t1 : t2; }
TernaryTrue = Ternary / TernaryStatement
TernaryFalse = Ternary / TernaryStatement

// Statements
// ==========
Statement = sections:Section* { return sections.join(""); }
TernaryStatement = sections:TernarySection* { return sections.join(""); }

// Sections
// ==========
Section = Round / Placeholder / Filler
TernarySection = Placeholder / TernaryFiller

// Conditions
// ==========
Condition = Match / Exists
Match = "match(" id:ConditionIdentifier "," val:(String / Integer) ")" { return options.getValue(id) == val; }
Exists = "exists(" id:ConditionIdentifier ")" { return options.getValue(id) != null && options.getValue(id) != ""; }

// Block of characters
// ==========
Placeholder = "${" identifier:Identifier "}" { return options.getValue(identifier); }
Identifier = chars:IdentifierChar+ { return chars.join(""); }
ConditionIdentifier = chars:ConditionIdentifierChar+ { return chars.join(""); }
Filler = chars:FillerChar+ { return chars.join(""); }
TernaryFiller = chars:TernaryFillerChar+ { return chars.join(""); }
String = "\"" chars:StringChar* "\"" { return chars.join(""); }
Integer = integer:[0-9]+ { return parseInt(integer, 10); }
Round = "round(" id:ConditionIdentifier "," val:(Integer) ")" { return isFinite(parseFloat(options.getValue(id))) ? parseFloat(options.getValue(id)).toFixed(val) : ""; }

// Characters
// ==========
IdentifierChar = _EscapedChar / !"}" @.
ConditionIdentifierChar = _EscapedChar / !"," !")" @.
FillerChar = _EscapedChar / !"${" @.
TernaryFillerChar = _EscapedChar / !"${" !":" @.
StringChar = _EscapedChar / !"\"" @.
_EscapedChar = "\\" @.
