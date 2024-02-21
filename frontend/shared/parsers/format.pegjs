Format = Ternary / Statement

Ternary = c:Condition "?" t1:TernaryTrue ":" t2:TernaryFalse { return c ? t1 : t2; }
TernaryTrue = Ternary / TernaryStatement
TernaryFalse = Ternary / Statement

Statement = sections:Section* { return sections.join(""); }
TernaryStatement = sections:TernarySection* { return sections.join(""); }

Section = Placeholder / Filler
TernarySection = Placeholder / TernaryFiller


// Conditions
// ==========
Condition = Match
Match = "match(" id:ConditionIdentifier "," val:(String / Integer) ")" { return options.getValue(id) == val; }


// Block of characters
// ==========
Placeholder = "${" identifier:Identifier "}" { return options.getValue(identifier); }
Identifier = chars:NoEndBracket+ { return chars.join(""); }
ConditionIdentifier = chars:NoEndComma+ { return chars.join(""); }
Filler = chars:NoStartBracket+ { return chars.join(""); }
TernaryFiller = chars:NoEndTernary+ { return chars.join(""); }
String = "\"" chars:NoEndQuote* "\"" { return chars.join(""); }
Integer = integer:[0-9]+ { return parseInt(integer, 10); }

// Characters
// ==========
Charset = _EscapedChar / .
NoStartBracket = _EscapedChar / !"${" @.
NoEndBracket = _EscapedChar / [^}]
NoEndTernary = _EscapedChar / [^:]
NoEndQuote = _EscapedChar / [^"]
NoEndComma = _EscapedChar / [^,]
_EscapedChar = "\\" @.