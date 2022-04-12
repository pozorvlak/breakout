# Breakout

No, not [that Breakout](https://en.wikipedia.org/wiki/Breakout_(video_game)).

Suppose you have an event (probably online these days), full of people who don't yet know each other. You want to split them up into smaller breakout rooms, and rotate them between rooms until everyone's met everyone else. How best to do this?

This is an example of a [block design](https://en.wikipedia.org/wiki/Block_design) problem. Specifically, you want an S(2, k, n) [Steiner system](https://en.wikipedia.org/wiki/Steiner_system), where each room holds k people and there are n people in total. Unfortunately, finding block designs is one of those problems, all too common in combinatorics, that looks straightforward but quickly gobbles up enormous amounts of computation. But when have we ever let that stop us?

This repo contains two MiniZinc programs:
 - `fewest_sessions.mzn`, which attempts to find the smallest number of sessions needed for everyone to meet everyone else. It requires you to specify an upper bound on the number of sessions; setting this too high will result in long runtimes, and setting it too low will result in you getting the answer `UNSATISFIABLE` and having to try again.
 - `most_meetings.mzn`, which tries to maximise how many people meet each other in a fixed number of sessions. Unlike `fewest_sessions.mzn`, which will only accept perfection, this will usually produce *some* answer fairly quickly.

## Installation and usage

Install [MiniZinc](https://www.minizinc.org/software.html), and open the project file `breakout.mzp` in the MiniZinc IDE. Choose the tab with either `fewest_sessions.mzn` or `most_meetings.mzn` and click the "Run" button. This brings up a dialog that allows you to enter the number of people, rooms and sessions, or to choose a file containing suitable values. MiniZinc will then search for solutions, printing out a new solution each time it improves on its previous best answer. Leave it running until it either finds an optimal solution (indicated by a `================` under the output) or you get bored.

MiniZinc allows you to choose between different solver backends, and this sometimes makes a dramatic difference. Of the solvers I've tried, I've generally found Chuffed is fastest for `fewest_sessions.mzn`, though Gecode with eight threads and the provided search annotations (uncomment the lines between `solve` and `minimize`) sometimes gives it a run for its money. The fastest solver I've found for `most_meetings.mzn` is Gecode with as many threads as you can throw at it. The project includes configurations to run Gecode and OR-Tools with 8 threads, which should be available from the "Solver configuration" dropdown in the toolbar.

This repo was inspired by Mike Prior-Jones, who begged me not to waste my time on this problem. Sorry, Mike.
