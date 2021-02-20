
%I am Here
here.

% Either I am here or Jane has a cat named patty
jane_has_cat_named_patty :- here.
% Either Jane does not have a cat named patty or John has a dog named curiosity
john_has_dog_named_curiosity :- jane_has_cat_named_patty.
% Either John does not have a dog named curiosity or Curiosity killed the cat
curiosity_killed_the_cat :- john_has_dog_named_curiosity.