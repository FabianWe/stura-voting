#!/usr/bin/env python3

# stura_voting_io.py
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

from xml.etree.ElementTree import Element, SubElement
import xml.dom.minidom as minidom
import csv

from stura_voting import *
import xml_functions


class VoterParseException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class PollParseException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def parseVoters(path, delimiter=';'):
    result = []
    try:
        with open(path, 'r') as f:
            for num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                splitted = line.split(delimiter)
                if len(splitted) != 2:
                    raise VoterParseException('Ungültige Syntax in Zeile ' +
                                              str(num))
                name, val = splitted
                try:
                    val = int(val)
                except ValueError as e:
                    raise VoterParseException('Fehler in Zeile ' + str(num) +
                                              '. ' + val + ' ist keine Zahl.')
                result.append(WeightedVote(name, val))
    except EnvironmentError as e:
        raise VoterParseException(str(e))
    return result


def writePollsToXML(path, polls):
    root = Element('polls')
    for poll in polls:
        poll.toXMLTree(root)
    with open(path, 'w') as f:
        f.write(xml_functions.prettify(root))


def getGeneralInformation(node):
    attributes = node.attributes
    name = node.firstChild.nodeValue.strip()
    percent = None
    try:
        percent = float(attributes['percent'].value)
    except ValueError as e:
        raise PollParseException(str(e))
    allVotes = attributes['allVotes'].value
    if allVotes == 'True':
        allVotes = True
    else:
        allVotes = False
    return name, percent, allVotes


def parseMedianSkel(node):
    attributes = node.attributes
    name, percent, allVotes = getGeneralInformation(node)
    maxValue = float(attributes['maxValue'].value)
    return MedianSkel(name, percent, allVotes, maxValue)


def parseSchulzeSkel(node):
    name, percent, allVotes = getGeneralInformation(node)
    options = []
    choicesElem = xml_functions.getSingletonElement(node, 'options')
    for choiceElem in choicesElem.getElementsByTagName('option'):
        options.append(choiceElem.firstChild.nodeValue.strip())
    return SchulzeSkel(name, percent, allVotes, options)


def parsePolls(path):
    dom = minidom.parse(path)
    root = xml_functions.getSingletonElement(dom, 'polls')
    result = []
    for pollElem in root.getElementsByTagName('poll'):
        _type = pollElem.attributes['type'].value
        if _type == 'schulze':
            result.append(parseSchulzeSkel(pollElem))
        elif _type == 'median':
            result.append(parseMedianSkel(pollElem))
        else:
            raise PollParseException('Unbekannter Abstimmungstyp "%s"' % _type)
    return result


def createInputCSV(path, polls, voters, _del=';'):
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=_del)
        firstRow = ['']
        firstRow.extend(e.name for e in polls)
        writer.writerow(firstRow)
        for voter in voters:
            row = [voter.name]
            row.extend([''] * len(polls))
            writer.writerow(row)


def readTable(path, voters, skels):
    votersMap = {v.name: v for v in voters}
    polls = [s.emptyPoll() for s in skels]
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        head = next(reader)[1:]
        allLines = list(reader)
        for line in allLines:
            vName = line[0]
            for p, val in zip(polls, line[1:]):
                voter = votersMap[vName]
                p.addVote(p.makeVote(voter, val))
    return polls
