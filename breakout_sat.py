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


def person_in_room(loc, p, r, s, rooms):
    """Person p is in room r (and only room r) during session s"""
    clauses = [
        Not(loc(p, rr, s)) for rr in range(r)
    ] + [
        loc(p, r, s)
    ] + [
        Not(loc(p, rr, s)) for rr in range(r+1, rooms)
    ]
    return And(clauses)


def one_room_per_session(opt, loc, people, rooms, sessions):
    """Everyone is in exactly one room per session"""
    for p in range(people):
        for s in range(sessions):
            opt.add(Or(
                *(person_in_room(loc, p, r, s, rooms) for r in range(rooms))))


def people_not_in_room(loc, room, session, people, absent):
    for absentees in combinations(range(people), absent):
        yield And(*(Not(loc(p, room, session)) for p in absentees))


def rooms_within_capacity(opt, loc, people, rooms, sessions):
    capacity = ceil(people / rooms)
    absent = people - capacity
    for r in range(rooms):
        for s in range(sessions):
            opt.add(Or(*people_not_in_room(loc, r, s, people, absent)))


def everyone_meets_everyone(opt, loc, people, rooms, sessions):
    for (p1, p2) in combinations(range(people), 2):
        opt.add(Or(*(
            And(loc(p1, room, session), loc(p2, room, session))
            for room in range(rooms) for session in range(sessions)
        )))


def print_model(model, loc, people, rooms, sessions):
    for s in range(sessions):
        locations = []
        for p in range(people):
            for r in range(rooms):
                if model.evaluate(loc(p, r, s)):
                    locations.append(r)
        print(locations)

        groups = []
        for r in range(rooms):
            group = set()
            for p in range(people):
                if model.evaluate(loc(p, r, s)):
                    group.add(p)
            groups.append(group)
        print(groups)


def main(dzn_file):
    people, rooms, sessions = read_dzn(dzn_file)
    # (loc i j k) is true if person i is in room j during session k
    loc = Function('loc', IntSort(), IntSort(), IntSort(), BoolSort())
    opt = Solver()
    one_room_per_session(opt, loc, people, rooms, sessions)
    rooms_within_capacity(opt, loc, people, rooms, sessions)
    everyone_meets_everyone(opt, loc, people, rooms, sessions)
    # Break symmetries to improve solver speed?
    print(opt.check())
    print_model(opt.model(), loc, people, rooms, sessions)


if __name__ == '__main__':
    main(sys.argv[1])
