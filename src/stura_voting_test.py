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

    skel = MedianSkel('Test', 0.5, True, 1000)
    p = MedianPoll(skel)
    p.addVote(vote1)
    p.addVote(vote2)
    p.addVote(vote3)
    p.addVote(vote4)

    r = p.evaluate()

    assert r.requiredVotes == 5
    assert r.acceptedValue == 500


def test_median_two():
    # Beispiel von der StuRa-Homepage
    x = MedianVote('X', 1, 0)
    y = MedianVote('Y', 2, 150)
    z = MedianVote('Z', 3, 200)

    skel = MedianSkel('Test', 0.5, True, 200)
    p = MedianPoll(skel)
    p.addVote(x)
    p.addVote(y)
    p.addVote(z)

    r = p.evaluate()

    assert r.requiredVotes == 3
    assert r.acceptedValue == 150
