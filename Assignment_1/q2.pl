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

% D

on(a,b).
on(b,table).
on(c,table).
clear(a).
clear(c).
 
on(X, Y) :- clear(X), clear(Y), on(X, Z), neq_table(Y), format("move ~w from ~w to ~w ~n", [X, Y, Z]).
% on(A,C) :- clear(A), clear(C), on(A,_), C \= table. 
 
clear(C) :- clear(A), on(A, Z), neq_table(C),format("move ~w from ~w to the table ~n", [A, Z]) .
%clear(C) :- clear(A), C \= table, on(A,_).
 
on(A,table) :- clear(A), on(A, Z), neq_table(C), format("move ~w from ~w to the table ~n", [A, Z]) .
neq_table(X) :- X \= table.


%
% My program is not printing for some reason???
% what conditions will generate a false output?
%
