#!/usr/bin/env python3

# stura_voting.py
#
# Copyright (C) 2015 Fabian Wenzelmann <fabianwenzelmann(at)posteo.de>
#
# This file is part of stura-voting.
#
# stura-voting is free software: you
# can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# stura-voting is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with stura-voting.
#
# If not, see <http://www.gnu.org/licenses/>.
#

from stura_voting import *


def test_median_one():
    # irgendwas selbst ausgedachtes
    vote1 = MedianVote('Fachbereich Bla', 4, 200)
    vote2 = MedianVote('Fachbereich Blubb', 3, 1000)
    vote3 = MedianVote('Fachbereich Foo', 2, 700)
    vote4 = MedianVote('Initiative Irgendwas', 2, 500)

    skel = MedianSkel('Median Test', 0.5, True, 1000)
    p = MedianPoll(skel)
    p.addVote(vote1)
    p.addVote(vote2)
    p.addVote(vote3)
    p.addVote(vote4)

    r = p.evaluate()

    assert r.requiredVotes == 5
    assert r.acceptedValue == 500


def test_median_two():
    # Beispiel von der StuRa Homepage
    x = MedianVote('X', 1, 0)
    y = MedianVote('Y', 2, 150)
    z = MedianVote('Z', 3, 200)

    skel = MedianSkel('Median Test', 0.5, True, 200)
    p = MedianPoll(skel)
    p.addVote(x)
    p.addVote(y)
    p.addVote(z)

    r = p.evaluate()

    assert r.requiredVotes == 3
    assert r.acceptedValue == 150


def test_schulze_one():
    # Beispiel von der StuRa Homepage
    options = ['Person A', 'Person B', 'Person C', 'Person D',
               'Person E', 'nein']
    skel = SchulzeSkel('Schulze Test', 0.5, True, options)

    v1 = SchulzeVote('X', 1, [0, 0, 0, 0, 0, 1])
    v2 = SchulzeVote('Y', 2, [0, 0, 1, 3, 0, 2])
    v3 = SchulzeVote('Z', 3, [1, 1, 0, 2, 2, 3])

    p = SchulzePoll(skel)
    p.addVote(v1)
    p.addVote(v2)
    p.addVote(v3)

    r = p.evaluate()
    assert r.d == [[0, 0, 2, 5, 3, 6],
                   [0, 0, 2, 5, 3, 6],
                   [3, 3, 0, 5, 3, 6],
                   [0, 0, 0, 0, 0, 4],
                   [0, 0, 2, 2, 0, 6],
                   [0, 0, 0, 2, 0, 0]]


def test_schulze_two():
    # Beispiel von Wikipedia:
    # <http://de.wikipedia.org/wiki/Schulze-Methode#Beispiel_1>
    options = ['A', 'B', 'C', 'D', 'E']
    skel = SchulzeSkel('SchulzeTest', 0.5, True, options)

    v1 = SchulzeVote('I', 5, [0, 2, 1, 4, 3])
    v2 = SchulzeVote('II', 5, [0, 4, 3, 1, 2])
    v3 = SchulzeVote('III', 8, [3, 0, 4, 2, 1])
    v4 = SchulzeVote('IV', 3, [1, 2, 0, 4, 3])
    v5 = SchulzeVote('V', 7, [1, 3, 0, 4, 2])
    v6 = SchulzeVote('VI', 2, [2, 1, 0, 3, 4])
    v7 = SchulzeVote('VII', 7, [4, 3, 1, 0, 2])
    v8 = SchulzeVote('VIII', 8, [2, 1, 4, 3, 0])

    p = SchulzePoll(skel)
    p.addVote(v1)
    p.addVote(v2)
    p.addVote(v3)
    p.addVote(v4)
    p.addVote(v5)
    p.addVote(v6)
    p.addVote(v7)
    p.addVote(v8)

    r = p.evaluate()
    assert r.d == [[0, 20, 26, 30, 22],
                   [25, 0, 16, 33, 18],
                   [19, 29, 0, 17, 24],
                   [15, 12, 28, 0, 14],
                   [23, 27, 21, 31, 0]]

    assert r.p == [[0, 28, 28, 30, 24],
                   [25, 0, 28, 33, 24],
                   [25, 29, 0, 29, 24],
                   [25, 28, 28, 0, 24],
                   [25, 28, 28, 31, 0]]

    assert r.ranks == [[4], [0], [2], [1], [3]]


def test_schulze_three():
    # Beispiel von Wikipedia:
    # <http://de.wikipedia.org/wiki/Schulze-Methode#Beispiel_2>
    options = ['A', 'B', 'C', 'D']
    skel = SchulzeSkel('SchulzeTest', 0.5, True, options)

    v1 = SchulzeVote('I', 3, [0, 1, 2, 3])
    v2 = SchulzeVote('II', 2, [1, 2, 3, 0])
    v3 = SchulzeVote('III', 2, [3, 1, 2, 0])
    v4 = SchulzeVote('IV', 2, [3, 1, 0, 2])

    p = SchulzePoll(skel)
    p.addVote(v1)
    p.addVote(v2)
    p.addVote(v3)
    p.addVote(v4)

    r = p.evaluate()
    assert r.d == [[0, 5, 5, 3],
                   [4, 0, 7, 5],
                   [4, 2, 0, 5],
                   [6, 4, 4, 0]]

    assert r.p == [[0, 5, 5, 5],
                   [5, 0, 7, 5],
                   [5, 5, 0, 5],
                   [6, 5, 5, 0]]
    print(r.ranks)

test_schulze_three()
