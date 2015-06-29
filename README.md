# stura-voting
Tools for different voting procedures developed for the Students' Council of 
the University Freiburg.

Provides a GUI for applying the following voting Methods:
- schulze method for voting based on preferences
- median of given values

# Using the Tool

Using the tool is a 3-step process.
1. Voter aquisition (and vote weight)
2. Collecting motions
3. Aggregate actual votes and calculate result

## 1. Voter aquisition

First, the programm needs to know how many voters are invloved 
and how much their vote weights.

To provide the voters, create a .csv file (e.g. with libreoffice) 
where the first column contains the voters (e.g. "voterOne") and 
the second column contains the weight of the votees vote (e.g. 
"1"). You can then load this file under "Abstimmende" with the 
button "Datei öffnen".

## 2. Collecting Motions

Second, the programm needs to know which motions are to be voted 
on so it can create a aggregation table from the voters and the 
motions.

You can create new motions with the buttons on the right 
("Median zufügen" or "Schulze zufügen"). They will be added 
automatically under "Abstimmungen". The programm will present you 
with a window, where you can set relevant parameters and add 
options to the motion.
Save the motions with "Datei speichern" and reload with "Datei 
öffnen".
To create a aggregation table, press "Tabelle erstellen".

## 3. Aggregating votes

Lastly, you enter the votes into the table and the programms can 
then calculate results, which are saved in a .html file in an 
easy readable format.

Open the aggregation table (e.g. with libreoffice calc) and add 
the votes into the relevant field. Preferences are added with a 
space seperating the numbers (e.g. "1 3 2 4"). Save the file (ass 
.csv!).

Lastly, press "Auswerten". Now, you can enter a titel for the 
vote and then provide the filepath to the aggregation 
table. Save the result. To view the results, open the result file 
in a browser (or other programm that can read .html files).
