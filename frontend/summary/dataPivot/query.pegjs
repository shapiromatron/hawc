Query
  = Or

Or
  = left:And "OR" right:Or {return options.orValues(left, right);} / And

And
  = left:Not "AND" right:And {return options.andValues(left, right);} / Not

Not
  = _ "NOT" _ value:Group {return options.negateValue(value);} / Group

Group
  = _ "(" _ query:Query _ ")" _ {return query;} / Integer

Integer
  = _ integer:[0-9]+ _ {return options.getValue(parseInt(integer.join(""), 10));}

_
  = [ \t\n\r]*
