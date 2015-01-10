
"""
The way I should set this up is as a alternative to the % operator, where I can do stuff like @(item.get_center()) from within text and have it get replaced with (19291, 1293).
You can define any number of 'root ids,' for example root, and gamestate.
Then, you can use a SubFormatter to merge local ids like item (in a primitive) with the root nodes availible too.

Examples: In a primitive, you might post a message as:
 @{citem.parent.get_owner_name()}'s @{citem.parent.name} shot a @{citem.name}

and it would format to:
 John Smith's Raider shot a Basic Laser

using code like:
 root.formatter.format(unformatted_string, Formatter({"citem":item}))

meaning you are using the root formatter supplemented by a formatter defining citem as the primitive call's item attribute
"""