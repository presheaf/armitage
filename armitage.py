import sys, os, random



PARTICIPANT_LIST_FN = "participants.txt"
ROUND_FN_TEMPLATE = "runde{}.txt"
BYE_NAME = "BYE"




class Tournament(object):
    def __init__(self, directory):
        self.directory = directory
        os.chdir(directory)
        self.parse_directory(directory)


        
    def parse_directory(self, directory):
        """Opens participant list and all rounds from a given directory."""

        

        with open(PARTICIPANT_LIST_FN) as f:
            players = map(lambda s: s.strip(),
                          f.readlines())
        if len(players) %2 == 1:
            with open(PARTICIPANT_LIST_FN, "a") as f:
                f.write(BYE_NAME)

        rounds = filter(lambda s: s[:5] == ROUND_FN_TEMPLATE[:5],
                        os.listdir("."))

        if len(rounds) == 0:
            last_round = 0
        else:
            last_round = max(map(lambda s: int(s[5]),
                                 rounds))
        
        if last_round != len(rounds):
            raise Exception("Strange round numbering")

        scores = {player: 0
                  for player in players}

        have_played = {player: []
                       for player in players}

        results = []
        for r in rounds:
            with open(r) as f:
                current_round = []
                games = map(lambda s: s.strip(), f.readlines())
                
                for g in games:
                    ps, result = g.split(";")
                    p1, p2 = ps.split("-")
                    s1, s2 = map(int, result.split("-"))

                    current_round.append((p1, p2, s1, s2))
                    scores[p1] += s1
                    scores[p2] += s2
                    have_played[p1].append(p2)
                    have_played[p2].append(p1)
                    
                results.append(current_round)

        self.results = results
        self.scores = scores
        self.have_played = have_played
        self.players = self.scores.keys()

    def num_rounds(self):
        return len(self.results)

    def strength_of_schedule(self):
        return {p1: sum([self.scores[p2] 
                        for p2 in self.players
                        if p2 in self.have_played[p1]])
                for p1 in self.players}

    def standings(self, tiebreak=False):
        """
        Returns list of players sorted by scores, with option to break 
        ties by SoS. Ties between players with equal score (and 
        if applicable equal SoS) are broken randomly.
        """
        standings = self.players

        # Ensures players are sorted randomly, but same way each time.
        # Potentially undesirable because players could manipulate order of
        # participant list to ensure winning if tied on SoS.
        
        random.seed("Exile")
        random.shuffle(standings)      
        
        if tiebreak:
            sos = self.strength_of_schedule()
            standings = sorted(standings,
                               key=lambda p: -sos[p]) 
        
        standings = sorted(standings,
                           key=lambda p: -self.scores[p])
        
        if BYE_NAME in self.players:
            standings.remove(BYE_NAME)
            standings.append(BYE_NAME)

        return standings

    def new_round(self):
        """Generates new round and prints pairings to file."""
        standings = self.standings(tiebreak=False)
        next_round_fn = ROUND_FN_TEMPLATE.format(self.num_rounds() + 1)

        if next_round_fn in os.listdir("."):
            raise Exception("file {} already exists".format(os.path.join(self.directory,
                                                                         next_round_fn)))

        with open(next_round_fn, 'w') as f:
            unmatched = {p: True
                         for p in self.players}
            for n in range(len(self.players)):
                p1 = standings[n]
                if not unmatched[p1]:
                    continue
                for p2 in standings[n+1:]:
                    if not (unmatched[p2] and
                            not p2 in self.have_played[p1]):
                        continue
                    unmatched[p2] = False
                    unmatched[p1] = False
                    if not (p1 == BYE_NAME or p2 == BYE_NAME):
                        f.write("{}-{};0-0\n".format(p1, p2))
                    else:
                        if p1 == BYE_NAME: # should never happen
                            print "turns out this actually can happen"
                            p1 = p2
                        f.write("{}-BYE;4-0\n".format(p1))
                    break
                if unmatched[p1]:
                    raise Exception("Couldn't match player {}".format(p1))

        print "\n\ngenerated new round in {}:\n\n".format(next_round_fn)
        with open(next_round_fn) as f:
            for line in f.readlines():
                print "--{} vs. {}--".format(*line.split(";")[0].split("-"))

    
if __name__ == "__main__":
    try:
        tournament_dir = sys.argv[1]
        action = sys.argv[2]
    except:
        raise Exception("Please call as 'python tournament.py TOURNAMENT_DIRECTORY "
                        "ACTION' where ACTION is 'standings' or 'new_round'")


    t = Tournament(tournament_dir)
    if action == "standings":
        standings = filter(lambda p: p != BYE_NAME,
                           t.standings(tiebreak=True))
        scores = t.scores
        sos = t.strength_of_schedule()
        print "-"*40
        print "{:20}{:>7}{:>10}".format("", "Points", "   SoS")
        print "-"*40
        for p in standings:
            print "{:20}{:7}{:>10}".format(p, scores[p], sos[p])
        print "-"*40

    elif action == "new_round":
        t.new_round()

    else:
        raise Exception("what is {}?".format(action))
