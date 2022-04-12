int: people;
int: rooms;
int: roomsize = ceil(people / rooms);
int: sessions;
set of int: PEOPLE = 1..people;
set of int: ROOMS = 1..rooms;
set of int: SESSIONS = 1..sessions;

array[SESSIONS, PEOPLE] of var ROOMS: loc;
array[SESSIONS, ROOMS] of var set of PEOPLE: group;
array[PEOPLE, PEOPLE] of var bool: meet;
var people..people*people: meetings;

% Set up channel between representations
constraint forall(s in SESSIONS, r in ROOMS, p in PEOPLE)(loc[s, p] = r <-> p in group[s, r]);

% Rooms stay within capacity
constraint forall(s in SESSIONS, r in ROOMS)(card(group[s, r]) <= roomsize);

% Count who meets who
constraint forall(p in PEOPLE, q in PEOPLE)(meet[p, q] = exists(s in SESSIONS)(loc[s, p] = loc[s, q]));
meetings = sum(p in PEOPLE, q in PEOPLE)(meet[p, q]);

% Break symmetries to improve solver speed
constraint forall(s in SESSIONS)(loc[s, 1] = 1);
constraint forall(s in SESSIONS, r in 1..rooms-1)(min(group[s, r]) < min(group[s, r+1]));
constraint forall(p in PEOPLE)(loc[1, p] = ((p - 1) div roomsize) + 1);

solve maximize meetings;