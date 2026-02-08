'''
Polling places

Jingwen Lu, Haixiao Luo

Main file for polling place simulation
'''

import random
import queue
import click
import util


class Voter:
    '''
    Class for representing a voter.

    Attributes:
        arrival_time: the time the voter arrives at the polls,
        voting_duration: the voting duration, that is, the amount
            of time the voter takes to vote,
        is_impatient: whether the voter is of the impatient sort
            (that is, will they leave if they have to wait too long),
        start_time: the time the voter is assigned to a voting booth
            (aka, the start time), assuming they vote,
        departure_time: the time the voter leaves the voting booth
            (aka, the departure time) assuming they vote, and
        has_voted: whether or not they voted.

    Methods: 
        set_start_time: 
            set the start time of voter
        set_departure_time:
            set the departure of voter
        set_has_voted:
            set the has_voted flag of voter
    '''

    def __init__(
            self,
            arrival_time,
            voting_duration,
            is_impatient,
            start_time = None,
            departure_time = None,
            has_voted = False
            ):
        '''
        Construct an instance of the voter
        '''

        self.arrival_time = arrival_time
        self.voting_duration = voting_duration
        self.is_impatient = is_impatient
        self.start_time = start_time
        self.departure_time = departure_time
        self.has_voted = has_voted

    def set_start_time(self, start_time):
        '''
        set the start time of the voter
        '''

        self.start_time = start_time

    def set_departure_time(self, departure_time):
        '''
        set the departure time of the voter
        '''

        self.departure_time = departure_time

    def set_has_voted(self):
        '''
        set the has_voted to True
        '''
        self.has_voted = True


class VotingBooths:
    '''Class for representing a bank of voting booths.

    Attributes: 
        num_booths: the number of booths

    Methods:
        is_booth_available: bool
            is there at least one unoccupied booth
        is_some_booth_occupied: bool
            is there at least one occupied booth
        enter_booth(v):
            add a voter to a booth. requires a booth to be available.
        time_next_free(): float
            when will a booth be free next (only called when all the
            booths are occupied)
        exit_booth():
             remove the next voter to depart from the booths and
             return the voter and their departure_time.
    '''

    def __init__(self, num_booths):
        '''
        Initialize the voting booths.

        Args:
            num_booths: (int) the number of voting booths in the bank
        '''

        self._num_booths = num_booths
        self._q = queue.PriorityQueue()

    def is_booth_available(self):
        '''Is at least one booth open'''
        return self._q.qsize() < self._num_booths

    def is_some_booth_occupied(self):
        '''Is at least one booth occupied'''
        return self._q.qsize() > 0

    def enter_booth(self, v):
        '''
        Add voter v to an open booth

        Args:
            v: (Voter) the voter to add to the booth.

        Requirements: there must be an open booth.
        '''
        assert self.is_booth_available(), "All booths in use"
        assert v.start_time, "Voter's start time must be set."

        dt = v.start_time + v.voting_duration
        self._q.put((dt, v))

    def time_next_free(self):
        '''
        When will the next voter leave?

        Returns: next departure time

        Requirements: there must be at least one occupied booth.
        '''
        assert self.is_some_booth_occupied(), "No booths in use"

        # PriorityQueue does not have a peek method.
        # So, do a get followed by a put.
        (dt, v) = self._q.get()
        self._q.put((dt, v))
        return dt


    def exit_booth(self):
        '''
        Remove voter with lowest departure time.

        Returns: the voter and the voter's departure time

        Requirements: there must be at least one occupied booth.
        '''
        assert self.is_some_booth_occupied(), "No booths in use"

        (dt, v) = self._q.get()
        return v, dt


class Precinct(object):
    '''
    Class for representing precincts.

    Attributes: None

    Methods:
        simulate(seed, voting_booths, impatience_threshold):
            Simulate election day for the precinct using the
            specified seed, voting_booths, and impatience threshold.
    '''

    def __init__(self,
                 name,
                 hours_open,
                 num_voters,
                 arrival_rate,
                 voting_duration_rate,
                 impatience_prob
                 ):
        '''
        Constructor for the Precinct class

        Input:
            name: (str) Name of the precinct
            hours_open: (int) Hours the precinct will remain open
            num_voters: (int) Number of voters in the precinct
            arrival_rate: (float) Rate at which voters arrive
            voting_duration_rate: (float) Lambda for voting duration
            impatience_prob: (float) the probability that a voter
                will be impatient.
        '''

        self.name = name
        self.hours_open = hours_open
        self.num_voters = num_voters
        self.arrival_rate = arrival_rate
        self.voting_duration_rate = voting_duration_rate
        self.impatience_prob = impatience_prob


    def __generate_voters_list(self, rd_seed):
        '''
        A private method that generates a list of voters according to the
        configuration of the precinct

        Args:
            seed: a seed for the random number

        Returns: list of voters
        '''

        random.seed(rd_seed)
        voters_lst = []
        present_time = 0
        for _ in range(self.num_voters):
            gap, voting_duration, is_impatient = util.gen_voter_parameters(
                self.arrival_rate, self.voting_duration_rate,
                self.impatience_prob)
            present_time += gap
            if present_time > self.hours_open * 60:
                break
            voters_lst.append(Voter(present_time, voting_duration,
                                    is_impatient))
        return voters_lst


    def __release_finished_voters(self, voting_booths, current_time):
        '''
        Release all the voters that have finished voting at the current time
        
        Input: 
        voting_booths: VotingBooths
        current_time: float
        
        Return: None
        '''

        while voting_booths.is_some_booth_occupied():
            next_free_time = voting_booths.time_next_free()
            if next_free_time is None or next_free_time > current_time:
                break
            voting_booths.exit_booth()


    def __start_voting(self, voter, current_time, voting_booths):
        '''
        Vote. 
        
        Inputs:
        voter:Voter
        current_time: float
        voting_booths: VotingBooths
        
        Return: None
        '''

        start_time = current_time
        voter.set_start_time(start_time)
        voting_booths.enter_booth(voter)
        depart_time = start_time + voter.voting_duration
        voter.set_departure_time(depart_time)
        voter.set_has_voted()
        return None


    def __will_wait(self, voter, next_free_time, imp_threshold):
        '''
        Judge whether the voter will wait

        Input:
        voter: Voter
        next_free_time: (float) the next time that a booth will be available
        imp_threshold: (float) the impatient threshold
        
        Return: bool
        '''

        wait_time = next_free_time - voter.arrival_time
        wait_judge = (not voter.is_impatient) or (wait_time <=
                                                  imp_threshold)
        return wait_judge


    def simulate(self, rd_seed, voting_booths, impatience_threshold):
        '''
        Simulate election day for the precinct using the specified seed,
        voting_booths, and impatience threshold.

        Args:
            seed: (int) the seed for the random number generator
            voting_booths: (VotingBooths) the voting booths assigned to the
                precinct for the day
            impatience_threshold: (int) the number of minutes an impatient
            voter is willing to wait (inclusive)

        Returns: list of Voters
        '''

        voters_lst = self.__generate_voters_list(rd_seed)
        current_time = 0

        for voter in voters_lst:
            current_time = max(current_time, voter.arrival_time)

            self.__release_finished_voters(voting_booths, current_time)
            if voting_booths.is_booth_available():
                self.__start_voting(voter, current_time, voting_booths)
                continue

            next_free_time = voting_booths.time_next_free()
            if next_free_time is None:
                continue
            if self.__will_wait(voter, next_free_time, impatience_threshold):
                current_time = max(current_time, next_free_time)
                self.__release_finished_voters(voting_booths, current_time)
                self.__start_voting(voter, current_time, voting_booths)

        while voting_booths.is_some_booth_occupied():
            voting_booths.exit_booth()

        return voters_lst


def find_specific_threshold(seed, precinct, voting_booths):
    '''
    For a given precinct, find the impatience threshold at which
    all voters voted in a single trial with given seed.
    
    Args:
        seed (int): the initial seed for the random number generator
        precinct: (Precinct) the precinct to simulate
        voting_booths: (VotingBooths) the voting booth to simulate

    Return: (int) the threshold of the trial.    
    '''

    flag_continue = True
    threshold = -9
    while flag_continue:
        threshold += 10
        lst_voters = precinct.simulate(seed, voting_booths, threshold)
        for voter in lst_voters:
            if not voter.has_voted:
                break
            if voter is lst_voters[-1]:
                flag_continue = False
    return threshold


def find_impatience_threshold(seed, precinct, num_booths, num_trials):
    '''
    For a given precinct, find the impatience threshold at which all
    voters are likely to vote.

    Args:
        seed (int): the initial seed for the random number generator
        precinct: (Precinct) the precinct to simulate
        num_booths: (int) number of voting booths to use in
            the simulations
        num_trials: (int) the number of trials to run

    Returns: (int) the median threshold from the trials

    '''

    assert num_trials > 0

    lst = []
    for trial in range(num_trials):
        rd_seed = seed + trial
        voting_booths = VotingBooths(num_booths)
        lst.append(find_specific_threshold(rd_seed, precinct, voting_booths))

    lst.sort()
    return lst[len(lst) // 2]


def find_specific_boothnum(seed, precinct, imp_threshold):
    '''
    For a given precinct, find the booth number needed at which
    all voters voted in a single trial with given seed.
    
    Args:
        seed (int): the initial seed for the random number generator
        precinct: (Precinct) the precinct to simulate
        impatience_threshold: (int) the impatience threshold

    Return: (int) the boothnum of the trial.    
    '''

    flag_continue = True
    boothnum = 0
    while flag_continue:
        boothnum += 1
        voting_booths = VotingBooths(boothnum)
        lst_voters = precinct.simulate(seed, voting_booths, imp_threshold)
        for voter in lst_voters:
            if not voter.has_voted:
                break
            if voter is lst_voters[-1]:
                flag_continue = False
    return boothnum


def find_voting_booths_needed(seed, precinct, imp_threshold, num_trials):
    '''
    For a given precinct, seed, and impatience threshold, predict the number of
    booths needed to make it likely that all the voters will vote.

    Args:
        seed (int): the initial seed for the random number generator
        precinct: (Precinct) the precinct to simulate
        impatience_threshold: (int) the impatience threshold
        num_trials: (int) the number of trials to run

    Returns: (int) the median number of booths needed from the trials.
    '''

    assert num_trials > 0

    lst = []
    for trial in range(num_trials):
        rd_seed = seed + trial
        lst.append(find_specific_boothnum(rd_seed, precinct, imp_threshold))

    lst.sort()
    return lst[len(lst) // 2]


@click.command(name="simulate")
@click.argument('precinct_file', type=click.Path(exists=True))
@click.option('--num-booths', type=int, default=1,
              help="number of voting booths to use")
@click.option('--impatience-threshold', type=float,
              default=1000, help="the impatience threshold")
@click.option('--print-voters', is_flag=True)
@click.option('--find-threshold', is_flag=True)
@click.option('--find-num-booths', is_flag=True)
@click.option('--num-trials', type=int, default=100,
              help="number trials to run")
def cmd(precinct_file, num_booths, impatience_threshold,
        print_voters, find_threshold, find_num_booths, num_trials):
    '''
    Run the program...
    '''
    #pylint: disable=too-many-locals
    p, seed = util.load_precinct(precinct_file)

    precinct = Precinct(p["name"],
                        p["hours_open"],
                        p["num_voters"],
                        p["arrival_rate"],
                        p["voting_duration_rate"],
                        p["impatience_prob"])

    if find_threshold:
        pt = find_impatience_threshold(seed, precinct, num_booths, num_trials)
        s = ("Given {} booths, an impatience threshold of {}"
             " would be appropriate for Precinct {}")
        print(s.format(num_booths, pt, p["name"]))
    elif find_num_booths:
        vbn = find_voting_booths_needed(seed, precinct,
                                        impatience_threshold, num_trials)
        s = ("Given an impatience threshold of {}, provisioning {}"
             " booth(s) would be appropriate for Precinct {}")
        print(s.format(impatience_threshold, vbn, p["name"]))
    elif print_voters:
        vb = VotingBooths(num_booths)
        voters = precinct.simulate(seed, vb, impatience_threshold)
        util.print_voters(voters)
    else:
        vb = VotingBooths(num_booths)
        voters = precinct.simulate(seed, vb, impatience_threshold)
        print("Precinct", p["name"])
        print("- {} voters voted".format(len(voters)))
        if len(voters) > 0:
            # last person might be impatient.  look
            # backwards for the first actual voter.
            last_voter_departure_time = None
            for v in voters[::-1]:
                if v.departure_time:
                    last_voter_departure_time = v.departure_time
                    break
            s = "- Polls closed at {} and last voter departed at {:.2f}."
            print(s.format(p["hours_open"]*60, last_voter_departure_time))
            nv = len([v for v in voters if not v.has_voted])
            print("- {} voters left without voting".format(nv))
            if not voters[-1].departure_time:
                print("  including the last person to arrive at the polls")


if __name__ == "__main__":
    cmd() # pylint: disable=no-value-for-parameter
