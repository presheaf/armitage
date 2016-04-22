# armitage
Netrunner tournament organizer.

To start a new tournament, make a directory for your tournament, make a newline-separated list of participants called "participants.txt".
To operate, call script as "python armitage.py dir action" where dir is the directory you made and action is 'new_round' to pair players for a new round,
or 'standings' to output standings (taking SoS into account, then randomly tiebreaking).
To input round results, open dir/rundeX.txt and replace 0-0 by the appropriate result.
