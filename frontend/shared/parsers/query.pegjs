Query
  = Or

Or
  = left:And "OR"i right:Or {return options.orValues(left, right);} / And

And
  = left:Not "AND"i right:And {return options.andValues(left, right);} / Not

Not
  = _ "NOT"i _ value:Not {return options.negateValue(value);} / Group

Group
  = _ "(" _ query:Query _ ")" _ {return options.groupValues ? options.groupValues(query) : query;} / Integer

Integer
  = _ integer:[0-9]+ _ {return options.getValue(parseInt(integer.join(""), 10));}

_
  = [ \t\n\r]*
