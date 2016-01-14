Dix Commenter
-------------

Usage:

    $ cat bidix.dix | ./main.py ruleset.txt > output.dix

How to write rules
------------------

Rules can match `<tags>`, text and groups.
Empty rule text will match all words.
i.e:

    <n>:

will comment all noun `e`s irrespective of what word they are. Same rules apply to the right side.
