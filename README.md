# logicAgent
A logic agent that can make inference from a knowledge base and determine whether the input statement is true.

The example below illustrates the format of the input file:
(sample01.txt)
Traitor(Anakin)
8
ViterbiSquirrel(x) && Secret(y) && Tells(x, y, z) && Hostile(z) =>
Traitor(x)
Knows(Sidious, Pine)
Resource(Pine)
Resource(x) && Knows(Sidious, x) => Tells(Anakin, x, Sidious)
Resource(x) => Secret(x)
Enemy(x, USC) => Hostile(x)
ViterbiSquirrel(Anakin)
Enemy(Sidious, USC)

query: Traitor(Anakin)

output content should be as follows:
(sample01.output.txt)
Ask: Traitor(Anakin)
Ask: ViterbiSquirrel(Anakin)
True: ViterbiSquirrel(Anakin)
Ask: Secret(_)
Ask: Resource(_)
True: Resource(Pine)
True: Secret(Pine)
Ask: Tells(Anakin, Pine, _)
Ask: Resource(Pine)
True: Resource(Pine)
Ask: Knows(Sidious, Pine)
True: Knows(Sidious, Pine)
True: Tells(Anakin, Pine, Sidious)
Ask: Hostile(Sidious)
Ask: Enemy(Sidious, USC)
True: Enemy(Sidious, USC)
True: Hostile(Sidious)
True: Traitor(Anakin)
Tru
