Hydra is a service that accepts connections from incoming clients and makes
these clients available to a virtual midi port interface.

For example, you could have some music track playing from a midi sequencer 
program such as ableton, and have these clients be able to control some 
midi instrument as determined by whatever you have programmed in the 
sequencer.

It keeps a list of all connected clients.
Communications are 2 way between the midi ports and client.
The system will arbitrarily choose one of the clients to control the midi
instrument if 



There is also the HydraHead android app that works in conjuntion with the 
service. The app allows for auto connecting to some wireless access
point so there is no configuration needed for client users to connect to
the performance.
