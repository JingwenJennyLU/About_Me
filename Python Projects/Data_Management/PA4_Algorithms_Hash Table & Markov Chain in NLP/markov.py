'''
MACS 30122: Markov models and hash tables
Jingwen Lu
'''

import sys
import math
import hash_table

HASH_CELLS = 57

class Markov:

    def __init__(self, k, s):
        '''
        Construct a new k-order Markov model using the statistics of string "s"

        Inputs:
            k (int): k-order
            s (str): a string
        
        Returns (none)
        '''
        self.k = k
        self.s = s

        self.S = len(set(s))

        self.hash_table = hash_table.Hashtable(HASH_CELLS, 0)
        circular_s = s + s[:k]

        for i in range(len(s)):
            k_str = circular_s[i : i + k]
            k1_str = circular_s[i : i + k + 1]

            self.hash_table[k_str] = self.hash_table[k_str] + 1
            self.hash_table[k1_str] = self.hash_table[k1_str] + 1



    def log_probability(self, s):
        '''
        Get the log probability of string "s", given the statistics of
        character sequences modeled by this particular Markov model
        This probability is *not* normalized by the length of the string.

        Inputs:
            s (str): a string
        
        Returns (float): log probability of string "s" without normalization
        '''
        total_log_prob = 0.0
        circular_s = s + s[:self.k]

        for i in range(len(s)):
            k_str = circular_s[i : i + self.k]
            k1_str = circular_s[i : i + self.k + 1]
            M = self.hash_table[k1_str]
            N = self.hash_table[k_str]
            prob = (M + 1) / (N + self.S)
            total_log_prob += math.log(prob)
        
        return total_log_prob


def identify_speaker(speaker_a, speaker_b, unknown_speech, k):
    '''
    Given sample text from two speakers, and text from an unidentified speaker,
    return a tuple with the *normalized* log probabilities of each of the
    speakers uttering that text under a "k" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.

    Inputs:
        speaker_a (str): a string of text uttered by speaker a
        speaker_b (str): a string of text uttered by speaker b
        unknown_speech (str): a string of text utterred by unknown speaker
        k (int): k-order
    
    Returns (tuple of float, float, str): first two items of tuples are normalized log
    probabilities for each speaker, third item is the conclusion
    '''
    
    model_a = Markov(k, speaker_a)
    model_b = Markov(k, speaker_b)
    log_prob_a = model_a.log_probability(unknown_speech)
    log_prob_b = model_b.log_probability(unknown_speech)
    L = len(unknown_speech)
    norm_prob_a = log_prob_a / L
    norm_prob_b = log_prob_b / L

    if norm_prob_a > norm_prob_b:
        conclusion = 'A'
    else:
        conclusion = 'B'

    return (norm_prob_a, norm_prob_b, conclusion)


def print_results(res_tuple):
    '''
    Given a tuple from identify_speaker, print formatted results to the screen
    '''
    (likelihood1, likelihood2, conclusion) = res_tuple

    print("Speaker A: " + str(likelihood1))
    print("Speaker B: " + str(likelihood2))

    print("")

    print("Conclusion: Speaker " + conclusion + " is most likely")


def go():
    '''
    Interprets command line arguments and runs the Markov analysis.
    Useful for hand testing.
    '''
    num_args = len(sys.argv)

    if num_args != 5:
        print("usage: python3 " + sys.argv[0] + " <file name for speaker A> " +
              "<file name for speaker B>\n  <file name of text to identify> " +
              "<order>")
        sys.exit(0)

    with open(sys.argv[1], "rU") as file1:
        speech1 = file1.read()

    with open(sys.argv[2], "rU") as file2:
        speech2 = file2.read()

    with open(sys.argv[3], "rU") as file3:
        speech3 = file3.read()

    res_tuple = identify_speaker(speech1, speech2, speech3, int(sys.argv[4]))

    print_results(res_tuple)


if __name__ == "__main__":
    go()
