#!/usr/bin/env python

from itertools import combinations
from math import ceil
import re
import sys

from z3 import And, BoolSort, Function, If, Int, IntSort, Not, Optimize, Or


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

    def __init__(self, people, rooms):
        self.people = people
        self.rooms = rooms
        self.capacity = ceil(self.people / self.rooms)
        # (loc i j) is true if person i is in room j
        self.loc = Function('loc', IntSort(), IntSort(), BoolSort())
        self.met = [[False] * people for p in range(people)]
        self.already_met = Int('already_met')
        self.opt = Optimize()

    def person_in_room(self, p, r):
        """Person p is in room r (and only room r)"""
        clauses = [
            Not(self.loc(p, rr)) for rr in range(r)
        ] + [
            self.loc(p, r)
        ] + [
            Not(self.loc(p, rr)) for rr in range(r+1, self.rooms)
        ]
        return And(clauses)

    def one_room_per_session(self):
        """Everyone is in exactly one room per session"""
        for p in range(self.people):
            self.opt.add(Or(*(
                self.person_in_room(p, r)
                for r in range(self.rooms))))

    def people_not_in_room(self, room, absent):
        for absentees in combinations(range(self.people), absent):
            yield And(*(Not(self.loc(p, room)) for p in absentees))

    def rooms_within_capacity(self):
        absent = self.people - self.capacity
        for r in range(self.rooms):
            self.opt.add(Or(*self.people_not_in_room(r, absent)))

    def first_person_in_first_room(self):
        self.opt.add(self.person_in_room(0, 0))

    def get_groups(self):
        model = self.opt.model()
        groups = []
        for r in range(self.rooms):
            group = set()
            for p in range(self.people):
                if model.evaluate(self.loc(p, r)):
                    group.add(p)
            groups.append(group)
        return groups

    def get_locations(self):
        model = self.opt.model()
        locations = []
        for p in range(self.people):
            for r in range(self.rooms):
                if model.evaluate(self.loc(p, r)):
                    locations.append(r)
        return locations

    def update_meetings(self, groups):
        new_meetings = 0
        for group in groups:
            for p1 in group:
                for p2 in group:
                    if not self.met[p1][p2] and p1 < p2:
                        # print(f"New meeting! {p1} and {p2}")
                        new_meetings += 1
                    self.met[p1][p2] = True
        return new_meetings

    def initial_groups(self):
        groups = []
        for i in range(self.rooms):
            lo = i * self.capacity
            hi = min(lo + self.capacity, self.people)
            groups.append(set(range(lo, hi)))
        return groups

    def shared_room(self, p1, p2):
        return And(*(self.loc(p1, r) == self.loc(p2, r)
                     for r in range(self.rooms)))

    def new_meetings(self):
        return sum(
            If(self.shared_room(p1, p2), 1, 0)
            for p1 in range(self.people)
            for p2 in range(p1 + 1, self.people)
            if not self.met[p1][p2])

    def optimal_meetings(self):
        n = self.capacity
        return self.rooms * n * (n - 1) / 2

    def solve(self):
        self.one_room_per_session()
        self.rooms_within_capacity()
        # Break symmetries to improve solver speed
        self.first_person_in_first_room()
        print("Set up problem")
        groups = self.initial_groups()
        optimal = True
        while True:
            new_meetings = self.update_meetings(groups)
            optimal = optimal and (new_meetings == self.optimal_meetings())
            print(groups, new_meetings, "Optimal" if optimal else "")
            total_meetings = sum(sum(m) for m in self.met)
            if (total_meetings == self.people ** 2) or (new_meetings == 0):
                print(f"Total meetings: {total_meetings}/{self.people ** 2}")
                break
            self.opt.maximize(self.new_meetings())
            self.opt.check()
            groups = self.get_groups()
        if optimal:
            print("Optimal")


def main(dzn_file):
    people, rooms, sessions = read_dzn(dzn_file)
    breakout = Breakout(people, rooms)
    breakout.solve()


if __name__ == '__main__':
    main(sys.argv[1])
