#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


"""Dieses python-Modul stellt ein Programm für StuRa-Abstimmungen zur
Verfügung.

:copyright: 2015, Fabian Wenzelmann <fabianwenzelmann(at)posteo.de>, see
AUTHORS for more details
:license: GPL v 3, see LICENSE for more details.

Uses dominate package, licensed under GNU LESSER GENERAL PUBLIC LICENSE
Version 3.
"""

import math
from collections import defaultdict
from xml.etree.ElementTree import Element, SubElement
import xml.dom.minidom as minidom

from dominate import document
from dominate.tags import *


class WeightedVote(object):
    """Klasse für einen abstimmende Initiative / Fachbereich."""
    def __init__(self, name, weight):
        """
        Args:
            name (string): Name der Initiative / des Fachbereichs
            weight (int): Das Stimmgewicht
        """
        self.name = name
        self.weight = weight

    def __str__(self):
        return 'WeightedVote(name="%s", weight=%d)' % (self.name, self.weight)

    def __repr__(self):
        return str(self)


class MedianVote(WeightedVote):
    """Klasse für eine Stimme bei einer Median-Abstimmung."""
    def __init__(self, name, weight, value):
        """
        Args:
            name (string): Name der Initiative / des Fachbereichs
            weight (int): Das Stimmgewicht
            value (float): Der Betrag für den gestimmt wurde.
                None wenn der FB / die Ini nicht abgestimmt hat.
        """
        WeightedVote.__init__(self, name, weight)
        self.value = value


class SchulzeVote(WeightedVote):
    """Klasse für eine Stimme bei einer Schulze-Abstimmung."""
    def __init__(self, name, weight, ranking):
        """
        Args:
            name (string): Name der Initiative / des Fachbereichs
            weight (int): Das Stimmgewicht
            ranking (list<int>): Für jeden Abstimmungsgegenstand die
                Position dessen im Ranking. Es ist egal ob die Elemente
                geordnet sind oder nicht - sie müssen einfach nur die
                Reihenfolge angeben. Eine kleine Zahl bedeutet, dass
                dieser Abstimmungsgegenstand besser gewertet wird.
                None wenn der FB / die Ini nicht abgestimmt hat.
        """
        WeightedVote.__init__(self, name, weight)
        self.ranking = ranking


class PollSkel(object):
    """Oberklasse für ein Abstimmungsskellet. Dieses beschreibt
     eine Abstimmung ohne die Stimmen die abgegeben wurden,
     schreibt also beispielsweise nur vor, welche Gegenstände
     zur Abstimmung stehen oder welcher Betrag abgestimmt wird.

     Abstract methods:
      Die folgende(n) Methoden müssen von den Unterklassen
      implementiert werden:
        addToXmlTree(parent): Fügt einen Eintrag für die Abstimmung
          in den Abstimmungsbaum an der Stelle parent ein.
          Siehe Definition für das XML-Schema.
          Gibt den neu erstellten Knoten zurück.

        emptyPoll(): Erstellt eine leere Abstimmung in der
          Abstimmungen zugefügt werden können.
    """
    def __init__(self, name, percentRequired, allVotes):
        """
        Args:
            name (string): Der Name der Abstimmung
            percentRequired (float): Wie viel Prozent für eine Mehrheit
                notwendig sind, z.B. 50% für normale Abstimmungen oder
                75% für 3/4 Mehrheiten. Wert zwischen 0 und 1.
            allVotes (bool): Gibt an, ob alle Stimmberechtigten gewertet werden
                sollen oder nur jene die auch eine Stimme abgegeben haben.
                Das Verhalten hängt von dem später verwendeten Verfahren
                ab.
        """
        self.name = name
        self.percentRequired = percentRequired
        self.allVotes = allVotes

    def toXMLTree(self, parent):
        """Fügt die Abstimmung einem XML Baum zu.

           Die Methode gibt den neu erzeugten Knoten zurück.
           Subklassen können diesen dann weiter bearbeiten.
        Args:
            parent (node): Der Elternknoten
        """
        node = SubElement(parent, 'poll')
        node.text = self.name
        node.set('percent', str(self.percentRequired))
        node.set('allVotes', str(self.allVotes))
        return node


class MedianSkel(PollSkel):
    """Skelett für eine Median-Abstimmung.
    Enthält zusätzlich maxValue, den maximal Betrag über den
    abzustimmen ist.
    """
    def __init__(self, name, percentRequired, allVotes, maxValue):
        """
        Args:
            maxValue (float): Der abzustimmende Betrag
        """
        PollSkel.__init__(self, name, percentRequired, allVotes)
        self.maxValue = maxValue

    def toXMLTree(self, parent):
        node = PollSkel.toXMLTree(self, parent)
        node.set('type', 'median')
        node.set('maxValue', str(self.maxValue))
        return node

    def emptyPoll(self):
        return MedianPoll(self)


class SchulzeSkel(PollSkel):
    """Skelett für eine Median-Abstimmung.
    Enthält zusätzlich options, eine Liste aller Abstimmungsgegenstände.
    """
    def __init__(self, name, percentRequired, allVotes, options):
        """
        Args:
            options (list<string>): Eine Beschreibung aller
                zur Abstimmung stehenden Gegenstände
        """
        PollSkel.__init__(self, name, percentRequired, allVotes)
        self.options = options

    def toXMLTree(self, parent):
        node = PollSkel.toXMLTree(self, parent)
        node.set('type', 'schulze')
        choicesNode = SubElement(node, 'options')
        for choice in self.options:
            choiceNode = SubElement(choicesNode, 'option')
            choiceNode.text = choice
        return node

    def emptyPoll(self):
        return SchulzePoll(self)


class Poll(PollSkel):
    """Oberklasse für eine Abstimmung.
    Im Gegensatz zu einem PollSkel gibt es zusätzlich
    die einzelnen Abstimmungen der Initiativen / Fachbereiche.
    Diese werden in einer Liste votes gespeichert welcher
    mittels der Methode addVote neue Abstimmungen zugefügt werden.
    Diese Votes sind Unterklassen der WeightedVoter Klasse
    welche zum aktuellen Abstimmungstyp passen müssen.

    Abstract methods:
      Die folgende(n) Methoden müssen von den Unterklassen
      implementiert werden:
        evaluate(): Werte die Abstimmung aus und gibt ein Objekt
            von der Klasse EvalResult zurück.
        makeVote(voter, str): Parst aus einem String das die Abstimmung.
            TODO error handling
    """
    def __init__(self, skel):
        """
        Args:
            skel (PollSkel): Das Skelett aus welchem der Poll
                                erzeugt werden soll.
        """
        PollSkel.__init__(self, skel.name, skel.percentRequired,
                          skel.allVotes)
        self.votes = []

    def addVote(self, vote):
        """Fügt eine Abstimmung eines Fachbereichs / Initiative hinzu.
        Die Unterklasse von WeightedVote muss zu dem aktuellen
        Abstimmungsverfahren passen.

        Args:
            vote (WeightedVote): Das Vote welches zugefügt werden soll.
        """
        self.votes.append(vote)


class EvalResult(object):
    """Oberklasse für alle Abstimmungsergebnisse.

    Abstract methods:
      Die folgende(n) Methode(n) müssen von den Unterklassen
      implementiert werden:
        htmlOutput(doc, poll): Erstellt eine HTML Ausgabe für den
                         Ausgang der Abstimmung.
    """
    def __init__(self, actualVotes):
        self.actualVotes = actualVotes


class MedianResult(EvalResult):
    """Klasse für ein Median Abstimmungsergebnis.
    """
    def __init__(self, actualVotes, requiredVotes, weightSum, acceptedValue):
        """
        Args:
            actualVotes (list): Liste aller tatsächlich bei der
                Auszählung beachteten Stimmen
            requiredVotes (int): Anzahl benötigter Stimmen
                für eine Mehrheit
            weightSum (int): Summe aller Stimmgewichte wie sie für
                Auszählung beachtet wurde
            acceptedValue (float): Ergebnis (Höhe)
        """
        EvalResult.__init__(self, actualVotes)
        self.requiredVotes = requiredVotes
        self.weightSum = weightSum
        self.acceptedValue = acceptedValue

    def htmlOutput(self, doc, poll):
        with doc:
            h2('Finanzantrag: "%s"' % poll.name)
            text = 'Benötigte Stimmen: Mehr als %.2f%% von %d Stimmen, ' + \
                    'also mehr als %d.'
            text %= (poll.percentRequired * 100, self.weightSum,
                     self.requiredVotes)
            div(text)
            if poll.allVotes:
               div('Enthaltungen wurden als Stimme für 0€ gewertet.')
            with div('Beantragt wurden %.2f€, genehmigt wurden ' % poll.maxValue):
                b('%.2f€.' % self.acceptedValue)


class SchulzeResult(EvalResult):
    """Klasse für ein Schulze Abstimmungsergebnis.
    """
    def __init__(self, actualVotes, requiredVotes, weightSum, ranks, d, p):
        """
        Args:
            actualVotes (list): Liste aller tatsächlich bei der
                Auszählung beachteten Stimmen
            requiredVotes (int): Anzahl benötigter Stimmen
                für eine Mehrheit
            weightSum (int): Summe aller Stimmgewichte wie sie für
                Auszählung beachtet wurde
            ranks (list<list>): Liste aller Gruppen (sortiert nach
                Bestes, 2. Bestes usw.). Jedes Element ist eine Liste
                mit den Index-Werten der Abstimmungen.
            d (list<list>): Matrix d aus dem Schulze-Algorithmus
            p (list<list>): Matrix p aus dem Schulze-Algorithmus
        """
        EvalResult.__init__(self, actualVotes)
        self.requiredVotes = requiredVotes
        self.weightSum = weightSum
        self.ranks = ranks
        self.d = d
        self.p = p

    def htmlOutput(self, doc, poll):
        with doc:
            h2('Abstimmung: "%s"' % poll.name)
            text = 'Benötigte Stimmen: Mehr als %.2f%% von %d Stimmen, ' + \
                    'also mehr als %d.'
            text %= (poll.percentRequired * 100, self.weightSum,
                     self.requiredVotes)
            div(text)
            if poll.allVotes:
                div('Enthaltungen wurden als Nein-Stimme gewertet.')
            div('Das folgende Ranking wurde abgestimmt:')
            with ol():
                for group in self.ranks:
                    li('Gruppe')
                    with ul():
                        for elem in group:
                            li(poll.options[elem])
            div('Übersicht über die Abstimmungsgegenstände:')
            br()
            posNo = len(poll.options) - 1
            if self.weightSum == 0:
                div('Es gab keine Stimmen.')
            else:
                with table(border="1"):
                    with tr():
                        th('Nr.')
                        th('Option')
                        th('% der Stimmen vor Nein')
                    for i, o in enumerate(poll.options):
                        with tr():
                            td(str(i + 1))
                            td(o)
                            td('%.2f' % ((self.d[i][posNo] / self.weightSum) * 100))


class MakeVoteException(Exception):
    """Wird geworfen, wenn ein Vote nicht geparsed werden kann.
       
       Diese Exception tritt auf, wenn eine Stimme aus deinem
       String erstellt werden soll aber dieser keine korrekte
       Syntax aufweist.
    """
    def __init__(self, msg):
        """
        Args:
            msg (string): Beschreibt den Fehler.
        """
        Exception.__init__(self, msg)


class MedianPoll(Poll):
    """Klasse für eine Median-Abstimmung.
    """
    def __init__(self, skel):
        """
        Args:
            skel (MedianSkel): Das Skelett aus dem die
                Abstimmung erzeugt werden soll.
        """
        Poll.__init__(self, skel)
        self.maxValue = skel.maxValue

    def evaluate(self):
        """Wertet das Median-Verfahren aus.

        Nicht abgegebene Votes werden, falls allVotes aktiviert ist,
        als 0 gezählt. Ist allVotes nicht aktiviert werden diese
        einfach ignoriert.
        """
        actualVotes = []
        weightSum = 0
        for vote in self.votes:
            if vote.value is not None:
                # einfach zufügen
                actualVotes.append(vote)
                weightSum += vote.weight
            else:
                # es ist None --> wenn allVotes aktiv mit 0 zufügen
                # ansonsten ignorieren
                if self.allVotes:
                    actualVotes.append(MedianVote(vote.name, vote.weight, 0.0))
                    weightSum += vote.weight
        requiredVotes = math.floor(weightSum * self.percentRequired)
        acceptedValue = None
        weightSoFar = 0
        keyFunc = lambda item: item.value
        actualVotes.sort(key=keyFunc, reverse=True)
        for vote in actualVotes:
            weightSoFar += vote.weight
            if weightSoFar > requiredVotes:
                acceptedValue = vote.value
                break
        return MedianResult(actualVotes, requiredVotes, weightSum, acceptedValue)

    def makeVote(self, voter, _str):
        """Erstellt ein MedianVote und parsed diesen aus dem String.
        
        Die Eingabe muss als float gelesen werden können, ansonsten
        wird eine
        """
        val = None
        _str = _str.strip()
        if _str:
            try:
                val = float(_str)
            except ValueError as e:
                raise MakeVoteException('Eingabe ist keine gültige Zahl: %s' % _str)
        return MedianVote(voter.name, voter.weight, val)


class SchulzePoll(Poll):
    """Klasse für eine Schulze-Abstimmung.
    """
    def __init__(self, skel):
        """
        Args:
            skel (SchulzeSkel): Das Skelett aus dem die
                Abstimmung erzeugt werden soll.
        """
        Poll.__init__(self, skel)
        self.options = skel.options

    def evaluate(self):
        actualVotes = []
        weightSum = 0
        for vote in self.votes:
            if vote.ranking is not None:
                # einfach zufügen
                actualVotes.append(vote)
                weightSum += vote.weight
            else:
                # es ist None --> als Nein Stimme zählen
                # (Annahme: Nein ist letzte Option)
                if self.allVotes:
                    r = [1] * (len(self.options) - 1)
                    r.append(0)
                    actualVotes.append(SchulzeVote(vote.name, vote.weight, r))
                    weightSum += vote.weight
        requiredVotes = math.floor(weightSum * self.percentRequired)
        d = self.computeD(actualVotes)
        p = self.computeP(d)
        ranks = self.rankP(p)
        return SchulzeResult(actualVotes, requiredVotes, weightSum, ranks, d, p)

    def computeD(self, votes):
        """Berechnet die Matrix d wie sie hier beschrieben ist:
        <http://de.wikipedia.org/wiki/Schulze-Methode#Implementierung>
        """
        numChoices = len(self.options)
        d = [[0 for j in range(numChoices)] for i in range(numChoices)]
        for vote in votes:
            w = vote.weight
            ranking = vote.ranking
            for i in range(numChoices):
                for j in range(i + 1, numChoices):
                    if ranking[i] < ranking[j]:
                        d[i][j] += w
                    elif ranking[j] < ranking[i]:
                        d[j][i] += w
        return d

    def computeP(self, d):
        """Berechnet die Matrix p, Verfahren wie hier
        <http://de.wikipedia.org/wiki/Schulze-Methode#Implementierung>
        beschrieben.

        Args:
            d (Matrix von int): Die Matrix d
        """
        numChoices = len(self.options)
        p = [[0 for j in range(numChoices)] for i in range(numChoices)]
        for i in range(numChoices):
            for j in range(numChoices):
                if i != j:
                    if d[i][j] > d[j][i]:
                        p[i][j] = d[i][j]
                    else:
                        p[i][j] = 0
        for i in range(numChoices):
            for j in range(numChoices):
                if i != j:
                    for k in range(numChoices):
                        if i != k:
                            if j != k:
                                p[j][k] = max(p[j][k], min(p[j][i], p[i][k]))
        return p

    def rankP(self, p):
        """Sortiert die Matrix p, implementiert wie _rank_p hier
        <https://github.com/mgp/schulze-method/blob/master/schulze.py>

        Args:
            p (Matrix von int): Matrix p, berechnet durch computeP
        """
        numChoices = len(self.options)
        result = []
        candidateWins = defaultdict(list)
        for i in range(numChoices):
            numWins = 0
            for j in range(numChoices):
                if i != j:
                    candidateOneScore = p[i][j]
                    candidateTwoScore = p[j][i]
                    if candidateOneScore > candidateTwoScore:
                        numWins += 1
            lst = candidateWins[numWins]
            lst.append(i)
        keys = list(candidateWins.keys())
        keys.sort(reverse=True)
        for key in keys:
            result.append(candidateWins[key])
        return result

    def makeVote(self, voter, _str):
        ranking = None
        if _str:
            ranking = []
            for val in _str.split(' '):
                val = val.strip()
                if val:
                    try:
                        ranking.append(int(val))
                    except ValueError as e:
                        raise MakeVoteException('Ranking ist keine gültige Zahl: %s' % val)
            if len(ranking) != len(self.options):
                raise MakeVoteException('Falsche Anzahl von Gegenständen in der Stimme %s' % _str)
        return SchulzeVote(voter.name, voter.weight, ranking)
