#!/usr/bin/env python

from itertools import combinations
from math import ceil
import re
import sys

from z3 import And, BoolSort, Function, IntSort, Not, Optimize, Or, Solver

LINE = re.compile(r'(\w+)\s*=\s*(\d+);')


def read_dzn(filename):
    vars = {}
    with open(filename) as f:
        for line in f:
            m = LINE.fullmatch(line.rstrip())
            k, v = m.group(1, 2)
            vars[k] = int(v)
    return vars['people'], vars['rooms'], vars['sessions']


class Breakout:

    def __init__(self, people, rooms, sessions):
        self.people = people
        self.rooms = rooms
        self.sessions = sessions
        # (loc i j k) is true if person i is in room j during session k
        self.loc = Function('loc', IntSort(), IntSort(), IntSort(), BoolSort())
        self.opt = Solver()

    def person_in_room(self, p, r, s):
        """Person p is in room r (and only room r) during session s"""
        clauses = [
            Not(self.loc(p, rr, s)) for rr in range(r)
        ] + [
            self.loc(p, r, s)
        ] + [
            Not(self.loc(p, rr, s)) for rr in range(r+1, self.rooms)
        ]
        return And(clauses)

    def one_room_per_session(self):
        """Everyone is in exactly one room per session"""
        for p in range(self.people):
            for s in range(self.sessions):
                self.opt.add(Or(*(
                    self.person_in_room(p, r, s)
                    for r in range(self.rooms))))

    def people_not_in_room(self, room, session, absent):
        for absentees in combinations(range(self.people), absent):
            yield And(*(Not(self.loc(p, room, session)) for p in absentees))

    def rooms_within_capacity(self):
        capacity = ceil(self.people / self.rooms)
        absent = self.people - capacity
        for r in range(self.rooms):
            for s in range(self.sessions):
                self.opt.add(Or(*self.people_not_in_room(r, s, absent)))

    def everyone_meets_everyone(self):
        for (p1, p2) in combinations(range(self.people), 2):
            self.opt.add(Or(*(
                And(self.loc(p1, room, session), self.loc(p2, room, session))
                for room in range(self.rooms)
                for session in range(self.sessions)
            )))

    def print_model(self):
        model = self.opt.model()
        for s in range(self.sessions):
            print(f"Session {s}")
            locations = []
            for p in range(self.people):
                for r in range(self.rooms):
                    if model.evaluate(self.loc(p, r, s)):
                        locations.append(r)
            print(locations)

            groups = []
            for r in range(self.rooms):
                group = set()
                for p in range(self.people):
                    if model.evaluate(self.loc(p, r, s)):
                        group.add(p)
                groups.append(group)
            print(groups)
            print()

    def solve(self):
        self.one_room_per_session()
        self.rooms_within_capacity()
        self.everyone_meets_everyone()
        # Break symmetries to improve solver speed?
        self.opt.check()


def main(dzn_file):
    people, rooms, sessions = read_dzn(dzn_file)
    breakout = Breakout(people, rooms, sessions)
    breakout.solve()
    breakout.print_model()


if __name__ == '__main__':
    main(sys.argv[1])
