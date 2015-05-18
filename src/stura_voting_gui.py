#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# stura_voting_gui.py
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

import tkinter
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
import datetime

from stura_voting_io import *


stura_voting_copyright = """Copyright (C) 2015 Fabian Wenzelmann <fabianwenzelmann(at)posteo.de>

stura-voting is free software: you
can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation
either version 3 of the License, or (at your option) any later version.

stura-voting is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License
along with stura-voting.

If not, see <http://www.gnu.org/licenses/>.
"""

class SturaMainFrame(tkinter.Frame):
    def __init__(self, master=None):
        # none gui variables
        self.polls = []
        self.voters = []
        
        tkinter.Frame.__init__(self, master)
        master.title('StuRa Abstimmungen')
        votersLabel = tkinter.Label(self, text='Abstimmende')
        votersButton = tkinter.Button(self, text='Datei öffnen', command=self.openVoters)
        scrollbar1 = tkinter.Scrollbar(self, orient=tkinter.VERTICAL)
        votersDisplay = tkinter.Listbox(self, yscrollcommand=scrollbar1.set)
        self.votersDisplay = votersDisplay
        scrollbar1.config(command=votersDisplay.yview)
        numVoters = self.numVoters = tkinter.StringVar()
        numVoters.set('ges.: 0')
        numVotersLabel = tkinter.Label(self, textvariable=numVoters)
        votersLabel.grid(row=0, column=0, sticky='W')
        votersButton.grid(row=1, column=0, sticky='WE')
        votersDisplay.grid(row=2, column=0)
        numVotersLabel.grid(row=3, column=0, sticky='W')
        
        pollsLabel = tkinter.Label(self, text='Abstimmungen')
        pollsOpen = tkinter.Button(self, text='Datei öffnen', command=self.openPolls)
        pollsSave = tkinter.Button(self, text='Datei speichern', command=self.savePolls)
        createTableButton = tkinter.Button(self, text='Tabelle erstellen', command=self.createTable)
        evaluateButton = tkinter.Button(self, text='Auswerten', command=self.evaluate)
        pollsDisplay = tkinter.Listbox(self)
        self.pollsDisplay = pollsDisplay
        numPolls = self.numPolls = tkinter.StringVar()
        numPolls.set('ges.: 0')
        numPollsLabel = tkinter.Label(self, textvariable=numPolls)
        pollsLabel.grid(row=0, column=1, columnspan=4, sticky='W')
        pollsOpen.grid(row=1, column=1)
        pollsSave.grid(row=1, column=2)
        createTableButton.grid(row=1, column=3)
        evaluateButton.grid(row=1, column=4)
        pollsDisplay.grid(row=2, column=1, columnspan=4, sticky='WE')
        numPollsLabel.grid(row=3, column=1, sticky='W')
        
        self.grid()
    
    def openVoters(self):
        file_opt = {}
        file_opt['defaultextension'] = '.csv'
        file_opt['filetypes'] = [('csv files', '.csv'), ('all files', '.*')]
        file_opt['initialdir'] = '.'
        file_opt['parent'] = self
        name = filedialog.askopenfilename(**file_opt)
        if not name:
            return
        voters = None
        try:
            voters = parseVoters(name)
        except VoterParseException as e:
            messagebox.showerror('Datei öffnen fehlgeschlagen', str(e))
            return
        self.votersDisplay.delete(0, tkinter.END)
        self.votersDisplay.insert(0, *['%s: %d' % (v.name, v.weight) for v in voters])
        self.numVoters.set('ges.: %d' % len(voters))
        self.voters = voters

    def openPolls(self):
        file_opt = {}
        file_opt['defaultextension'] = '.xml'
        file_opt['filetypes'] = [('xml files', '.xml'), ('all files', '.*')]
        file_opt['initialdir'] = '.'
        file_opt['parent'] = self
        name = filedialog.askopenfilename(**file_opt)
        if not name:
            return
        polls = None
        try:
            polls = parsePolls(name)
        except PollParseException as e:
            messagebox.showerror('Datei öffnen fehlgeschlagen', str(e))
            return
        self.pollsDisplay.delete(0, tkinter.END)
        self.pollsDisplay.insert(0, *[p.name for p in polls])
        self.polls = polls
        self.updatePollsNum()


    def savePolls(self):
        file_opt = {}
        file_opt['defaultextension'] = '.xml'
        file_opt['filetypes'] = [('xml files', '.xml'), ('all files', '.*')]
        file_opt['initialdir'] = '.'
        file_opt['parent'] = self
        name = filedialog.asksaveasfilename(**file_opt)
        if not name:
            return
        writePollsToXML(name, self.polls)

    def updatePollsNum(self):
        self.numPolls.set('ges.: %d' % len(self.polls))
    
    def createTable(self):
        file_opt = {}
        file_opt['defaultextension'] = '.csv'
        file_opt['filetypes'] = [('csv files', '.csv'), ('all files', '.*')]
        file_opt['initialdir'] = '.'
        file_opt['parent'] = self
        name = filedialog.asksaveasfilename(**file_opt)
        if not name:
            return
        createInputCSV(name, self.polls, self.voters)

    def evaluate(self):
        ask = messagebox.askyesno('Fortfahren?', 'Sind alle aktuellen Dateien geöffnet?')
        if not ask:
            return
        now = datetime.datetime.now()
        init = 'Abstimmungen StuRa vom %02d.%02d.%d' % (now.day, now.month, now.year)
        title = simpledialog.askstring('Titel', 'Titel für Ausgabe eingeben', parent=self, initialvalue=init)
        if title is None:
            return
        file_opt = {}
        file_opt['defaultextension'] = '.csv'
        file_opt['filetypes'] = [('csv files', '.csv'), ('all files', '.*')]
        file_opt['initialdir'] = '.'
        file_opt['parent'] = self
        name = filedialog.askopenfilename(**file_opt)
        if not name:
            return
        polls = readTable(name, self.voters, self.polls)
        results = []
        for poll in polls:
            results.append(poll.evaluate())
        messagebox.showinfo('Auswertung', 'Abstimmungen wurden ausgewertet, Speicherort auswählen.')
        file_opt = {}
        file_opt['defaultextension'] = '.html'
        file_opt['filetypes'] = [('html files', '.html'), ('all files', '.*')]
        file_opt['initialdir'] = '.'
        file_opt['parent'] = self
        name = filedialog.asksaveasfilename(**file_opt)
        if not name:
            messagebox.showwarning('Hinweis', 'Auswertung wurde nicht gespeichert')
            return
        html = str(pollsToHtml(title, zip(polls, results)))
        with open(name, 'w') as f:
            f.write(html)

if __name__ == '__main__':
    root = tkinter.Tk()
    frame = SturaMainFrame(master=root)
    frame.mainloop()
