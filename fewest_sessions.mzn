int: people;
int: rooms;
int: roomsize = ceil(people / rooms);
int: sessions;
set of int: PEOPLE = 1..people;
set of int: ROOMS = 1..rooms;
set of int: SESSIONS = 1..sessions;

array[SESSIONS, PEOPLE] of var ROOMS: loc;
array[SESSIONS, ROOMS] of var set of PEOPLE: group;
var SESSIONS: all_met;

% Set up channel between representations
constraint forall(s in SESSIONS, r in ROOMS, p in PEOPLE)(loc[s, p] = r <-> p in group[s, r]);

% Rooms stay within capacity
constraint forall(s in SESSIONS, r in ROOMS)(card(group[s, r]) <= roomsize);

% Everyone meets everyone else
constraint forall(p in PEOPLE, q in PEOPLE)(exists(s in SESSIONS)(loc[s, p] = loc[s, q] /\ s <= all_met));

% Break symmetries to improve solver speed
constraint forall(s in SESSIONS)(loc[s, 1] = 1);
constraint forall(s in SESSIONS, p in PEOPLE)(s > all_met -> loc[s, p] = ((p - 1) div roomsize) + 1);
constraint forall(s in SESSIONS, r in 1..rooms-1)(min(group[s, r]) < min(group[s, r+1]));
constraint forall(p in PEOPLE)(loc[1, p] = ((p - 1) div roomsize) + 1);

solve
% Uncomment the following lines to improve search times with Gecode.
% Chuffed and OR Tools will choke on them, COIN-BC will ignore them.
%   :: int_search(loc, dom_w_deg, indomain_random)
%   :: restart_luby(100)
  minimize all_met;