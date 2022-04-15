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


def loc(i, j, k):
    """(l i j k) is true if person i is in room j during session k"""
    return f"(l {i} {j} {k})"


def nott(clause):
    """Negation of clause"""
    return f"(not {clause})"


def andd(clauses):
    """Conjunction of clauses"""
    return "(and " + " ".join(clauses) + ")"


def orr(clauses):
    """Disjunction of clauses"""
    return "(or " + " ".join(clauses) + ")"


def person_in_room(p, r, s, rooms):
    """Person p is in room r (and only room r) during session s"""
    clauses = [
        nott(loc(p, s, rr)) for rr in range(r)
    ] + [
        loc(p, s, r)
    ] + [
        nott(loc(p, s, rr)) for rr in range(r+1, rooms)
    ]
    return andd(clauses)


def one_room_per_session(people, rooms, sessions):
    """Everyone is in exactly one room per session"""
    for p in range(people):
        for s in range(sessions):
            print(orr(person_in_room(p, r, s, rooms) for r in range(rooms)))


def people_not_in_room(room, session, people, absent):
    for absentees in combinations(range(people), absent):
        yield andd(nott(loc(p, room, session)) for p in absentees)


def rooms_within_capacity(people, rooms, sessions):
    capacity = ceil(people / rooms)
    absent = people - capacity
    for r in range(rooms):
        for s in range(sessions):
            print(orr(people_not_in_room(r, s, people, absent)))


def everyone_meets_everyone(people, rooms, sessions):
    for (p1, p2) in combinations(range(people), 2):
        print(orr(
            andd([loc(p1, room, session), loc(p2, room, session)])
            for room in range(rooms) for session in range(sessions)
        ))


def main(dzn_file):
    people, rooms, sessions = read_dzn(dzn_file)
    # (l i j k) is true if person i is in room j during session k
    print("(declare-fun l (Int Int Int) Bool)")
    print("(assert (and")
    one_room_per_session(people, rooms, sessions)
    rooms_within_capacity(people, rooms, sessions)
    everyone_meets_everyone(people, rooms, sessions)
    # Break symmetries to improve solver speed?
    print("))")
    print("(check-sat)")
    print("(get-model)")


if __name__ == '__main__':
    main(sys.argv[1])
