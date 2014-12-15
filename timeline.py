"""
Find Top 10 most common emailers/Stalkers.
This program will take a txt file and output email addresses and number of emails sent by that email id
To store output:
    python top_title_words.py sample.txt > top_emailers.out
"""

from mrjob.job import MRJob
import re

#EMAIL_RE = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

class MRTimeline(MRJob):

    def mapper_get_years(self, _, line):
        # yield each email in the line
	#for email in EMAIL_RE.findall(line):
		yield line,1

    def reducer_count_years(self, year, counts):
        # optimization: sum the emails we've seen so far
        yield (year, sum(counts))

    # def reducer_count_years(self, years, counts):
    #     # send all (num_occurrences, emails) pairs to the same reducer.
    #     # num_occurrences is so we can easily use Python's max() function.
    #     yield None, (years,sum(counts))

 #    # discard the key; it is just None
 #    def reducer_find_top_ten(self, _, email_count_pairs):
 #        # each item of email_count_pairs is (count, email),
 #        # so yielding one results in key=counts, value=email
 #        sort_list = sorted(email_count_pairs, key=lambda x:x[1], reverse=True)
	# for d in sort_list[:10]:
	# 	yield (d)

    def steps(self):
        return [
            self.mr(mapper=self.mapper_get_years,
		    #combiner=self.combiner_count_years,
                    reducer=self.reducer_count_years)
        ]


if __name__ == '__main__':
    MRTimeline.run()
