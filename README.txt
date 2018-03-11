

getPartList.py - scrapes the parkrun website to get a list of participants over several runs (both runners and volunteers) as a json encoded file partlist.json.

partList2iddb.py takes partlist.json and creates a simpler json file of {id,name} records to use as a lookup databse.   Edit this manually to handle volunteers
who do not run, as they will be unknown in the db.

matchParts.py processes partlist.json and uses the id database iddb.json to
set the id of voluneers - this means that every participant in the file should
now have a name and id.

getPartStats.py - calculates statistics for each participant, and outputs as
partstats.json
