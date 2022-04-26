#!/usr/bin/env python

from itertools import combinations
from math import ceil
import re
import sys


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
        self.met = [[False] * self.people for p in range(self.people)]

    def new_meetings(self, group, person):
        return sum(not self.met[person][g] for g in group)

    def get_groups(self):
        groups = []
        unassigned = list(range(self.people))
        for r in range(self.rooms):
            group = set()
            while unassigned and len(group) < self.capacity:
                new_member = max(
                    unassigned,
                    key=lambda p: self.new_meetings(group, p))
                group.add(new_member)
                unassigned.remove(new_member)
            groups.append(group)
        return groups

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

    def optimal_meetings(self):
        n = self.capacity
        return self.rooms * n * (n - 1) / 2

    def solve(self):
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
            groups = self.get_groups()
        if optimal:
            print("Optimal")


def main(dzn_file):
    people, rooms, sessions = read_dzn(dzn_file)
    breakout = Breakout(people, rooms)
    breakout.solve()


if __name__ == '__main__':
    main(sys.argv[1])
