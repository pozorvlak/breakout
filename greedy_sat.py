#!/usr/bin/env python

from itertools import combinations
from math import ceil
import re
import sys

from z3 import And, AtMost, Function, If, Int, IntSort, Optimize, Or


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
        # (loc i) == j if person i is in room j
        self.loc = Function('loc', IntSort(), IntSort())
        self.met = [[False] * people for p in range(people)]
        self.already_met = Int('already_met')
        self.opt = Optimize()

    def loc_within_range(self):
        for p in range(self.people):
            self.opt.add(self.loc(p) >= 0)
            self.opt.add(self.loc(p) < self.rooms)

    def people_not_in_room(self, room, absent):
        for absentees in combinations(range(self.people), absent):
            yield And(*(self.loc(p) != room for p in absentees))

    def rooms_within_capacity(self):
        for r in range(self.rooms):
            clauses = (self.loc(p) == r for p in range(self.people))
            self.opt.add(AtMost(*clauses, self.capacity))

    def first_person_in_first_room(self):
        self.opt.add(self.loc(0) == 0)

    def get_groups(self):
        model = self.opt.model()
        groups = [set() for i in range(self.rooms)]
        for p in range(self.people):
            i = model.evaluate(self.loc(p)).as_long()
            groups[i].add(p)
        return groups

    def get_locations(self):
        model = self.opt.model()
        return [model.evaluate(self.loc(p)) for p in range(self.people)]

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

    def new_meetings(self):
        return sum(
            If(self.loc(p1) == self.loc(p2), 1, 0)
            for p1 in range(self.people)
            for p2 in range(p1 + 1, self.people)
            if not self.met[p1][p2])

    def optimal_meetings(self):
        n = self.capacity
        return self.rooms * n * (n - 1) / 2

    def solve(self):
        self.loc_within_range()
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
            goal = self.new_meetings()
            # print(goal)
            self.opt.push()
            self.opt.maximize(goal)
            self.opt.check()
            groups = self.get_groups()
            self.opt.pop()
        if optimal:
            print("Optimal")


def main(dzn_file):
    people, rooms, sessions = read_dzn(dzn_file)
    breakout = Breakout(people, rooms)
    breakout.solve()


if __name__ == '__main__':
    main(sys.argv[1])
