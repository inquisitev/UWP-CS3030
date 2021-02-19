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

% initial state
on(a,b).
on(b,table).
on(c,table).
clear(a).
clear(c).
 

% discovered format function at https://stackoverflow.com/questions/34635689/output-formatting-in-prolog
% Block X is on Block Y provided that X is clear, Y is clear, Y is on some block Z, and Y is not the table
on(X, Y) :- clear(X), clear(Y), on(X, Z), neq_table(Y), format("move ~w from ~w to ~w ~n", [X, Y, Z]).
 
% Block C is clear provided that A is clear, A is on some block X, and C is not the table
clear(C) :- clear(A), on(A, Z), neq_table(C),format("move ~w from ~w to the table ~n", [A, Z]) .
 
% Block C is clear provided that A is clear, A is on some block X, and C is not the table
on(A,table) :- clear(A), on(A, Z), neq_table(C), format("move ~w from ~w to the table ~n", [A, Z]) .
neq_table(X) :- X \= table.

