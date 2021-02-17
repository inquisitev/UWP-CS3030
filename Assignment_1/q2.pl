%Rules into predicate logic - A
%   clear(Block_A) is true if no block is placed on top of Block_A
%   on(Block_A, Block_B) is true if Block_A is placed on top of Block_B
%
%   move Block_A from Block_B to Block_C
%   clear(Block_A), clear(Block_C), Block_C \= table, on(Block_A, Block_B) -> on(Block_A, Block_C)
%
%   move Block_A from Block_B to table
%   clear(Block_A), on(Block_A, Block_B) -> on(Block_A, table)
%

% B
%   on(A,C) :- clear(A), clear(C), C \= table, on(A, B)
%   on(A,table) :- clear(A), on(A,B)

%D
  on(a,b)
  on(b,table)
  on(c,table)
  clear(a)
  clear(c)

  on(A,C) :- clear(A), clear(C), C \= table, on(A, B)
  on(A,table) :- clear(A), on(A,B)
