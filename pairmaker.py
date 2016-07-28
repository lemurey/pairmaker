from random import shuffle, choice
from collections import Counter
import datetime as dt

class PairMaker(object):
    '''
    creates daily unique pairings of students until all students have paired with all other students
    '''
    def __init__(self, 
                 start_date, 
                 students = None,
                 num_students = None
                 ):
        '''
        initialize PairMaker object
        start_date: string, 'MM/DD/YYYY' formatted date of the first day of class
        students: string, path of txt file with each students name on a line
        num_students: int, number of students in the class
        
        either students or num_students is required
        '''
        err_msg = "either students or num_students must be provided"
        assert (students is not None) or (num_students is not None), err_msg
        self._set_start_date(start_date)
        if num_students:
            self._setup_from_num(num_students)
        self.dows = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
        self.counts = Counter()
        self.all_pairs = None
        self.all_named_pairs = None
        self.out_dict = None
        self.cur_trip = None
        self.triples = None
        self.problem = 0
        if students:
            self._load_student_file(students)
        else:
            self.students = None
        self._prep()

    def _set_start_date(self, date):
        date = dt.datetime.strptime(date,'%m/%d/%Y')
        self.start_date = date

    def _load_student_file(self, path):
        students = []
        with open(path, 'r') as f:
            for line in f:
                student = line.strip()
                students.append(student)
        self._setup_from_num(len(students))
        shuffle(students)
        self.empty_index = -1
        if self.odd_num:
            students = [' '] + students
            self.empty_index = 0
        self.students = students

    def _setup_from_num(self, num):
        self.odd_num = False
        if num % 2 == 1:
            self.odd_num = True
            num += 1
        self.cycle_len = num - 1
        self.indices = range(num)
        self.row_length = len(self.indices)/2

    def _make_index_lists(self):
        all_pairs = []
        for i in range(self.cycle_len):
            cur_index = self._create_rotated_index(i)
            all_pairs.append(self._index_to_index_pairs(cur_index))
        self.all_pairs = all_pairs

    def _create_rotated_index(self, shift):
        return self.indices[:1] + self._right_shift(self.indices[1:],shift)

    def _right_shift(self, l, n):
        n = n % len(l)
        return l[-n:] + l[:-n]

    def _index_to_index_pairs(self, index):
        row1 = index[:self.row_length]
        row2 = index[:-(self.row_length+1):-1]
        return zip(row1,row2)

    def _make_named_list(self):
        all_named_pairs = []
        solo = None
        for pairs in self.all_pairs:
            cur_pairs = []
            for pair in pairs:
                if self.empty_index in pair:
                    solo = pair[1]
                    continue
                if solo:
                    pair = (pair[0], pair[1], solo)
                    solo = None
                pair = tuple(sorted([self.students[i] for i in pair]))
                cur_pairs.append(pair)
            all_named_pairs.append(cur_pairs)
        self.all_named_pairs = all_named_pairs

    def _prep(self):
        self._make_index_lists()
        if self.students:
            self._make_named_list()
            self.all_pairs = self.all_named_pairs
        self._make_triples()
        if self.triples:
            self._reorder()
        else:
            shuffle(self.all_pairs)

    def _reorder(self, count = 0):
        first_triple = self.triples[0]
        output = [0]
        last_triple = None
        n = len(self.triples)
        inds = range(1,n)
        iters = 0
        while len(output) != n:
            iters += 1
            if iters > 500:
                break
            ind = choice(inds)
            check = self.triples[ind]
            if self._check_trips(check, last_triple):
                output.append(ind)
                inds.remove(ind)
                last_triple = check
            elif self._check_trips(check, first_triple) and last_triple:
                output = [ind] + output
                inds.remove(ind)
                first_triple = check
        if len(output) != n:
            return self._reorder(count+1)
        new_trips = []
        new_pairs = []
        for i in output:
            new_trips.append(self.triples[i])
            new_pairs.append(self.all_pairs[i])
        self.all_pairs = new_pairs
        self.triples = new_trips
        self.count = count

    def make_output_dict(self):
        '''
        a dictionary with keys of weeks and values of a dictionary
        with keys of days and values of the pair assignments for that day
        INPUT: None
        OUTPUT: None
        '''
        out_dict = {}
        cur_day = self.start_date
        cur_week = 0
        cur_dict = {}
        pulling = self.all_pairs[:]
        while pulling:
            if cur_day.weekday() > 4:
                cur_day = cur_day + dt.timedelta(1)
                continue
            elif cur_day.weekday() == 0 and cur_day != self.start_date:
                cur_week += 1
                out_dict['week {}'.format(cur_week)] = cur_dict
                cur_dict = {}
            cur_pair = pulling.pop()
            shuffle(cur_pair)
            cur_dict[cur_day.strftime("%A")] = (cur_day, cur_pair)
            cur_day = cur_day + dt.timedelta(1)
        out_dict['week {}'.format(cur_week+1)] = cur_dict
        self.out_dict = out_dict

    def make_md_tables(self, out_path = 'pairs.md'):
        '''
        creates a markdown file of the student pairs
        INPUT: out_path, a string, output path to write markdown tables to
        '''
        if not self.out_dict:
            self.make_output_dict()
        weeks = sorted(self.out_dict.keys())
        with open(out_path,'w') as f:
            for week in weeks:
                w_str = '{}\n\n|day of week|groups|\n|---|---|\n'.format(week)
                all_days = self._make_week(self.out_dict[week].keys())
                for day in all_days:
                    date, pairs = self.out_dict[week][day]
                    w_str += '|{} - {}|{}|\n'.format(day, date.strftime('%m-%d'), ',<br>'.join(str(x) for x in pairs))
                f.write(w_str)
            f.write('\n')

    def _check_trips(self, trip1, trip2):
        if trip2 is None:
            trip2 = self.triples[0]
        for entry in trip1:
            if entry in trip2:
                return False
        return True

    def _make_triples(self):
        triples = []
        for pairs in self.all_pairs:
            for pair in pairs:
                if len(pair) == 3:
                    triples.append(pair)
        self.triples = triples

    def _make_week(self,lst):
        output = []
        for day in self.dows:
            if day in lst:
                output.append(day)
        return output

def make_fake_students(num_students = 19):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    with open('students.txt','w') as file:
        for i in range(num_students):
            file.write(alphabet[i] + '\n')


def main(n):
    
    iters = 500
    counts = []
    make_fake_students(n)
    for _ in range(iters):
        pm = PairMaker(start_date = '08/01/2016',students = 'students.txt')
        pm.make_md_tables()
        if pm.count > 0:
            counts.append(pm.count)
    print sorted(counts, reverse=True)
    print len(counts)
    # for _ in range(iters):
        
    #     c = Counter()
    #     c1 = Counter()
    #     prev = None
    #     for pairs in pm.all_pairs:
    #         for pair in pairs:
    #             c1[pair] += 1
    #     for t in pm.triples:
    #         if not prev:
    #             prev = t
    #             continue
    #         for entry in t:
    #             if entry in prev:
    #                 c[entry] += 1
    #         prev = t
    #     if len(c) > 0:
    #         count += 1
    #     if pm.count > 0:
    #         problems += 1
    #     if c1.most_common(1)[0][1] > 1:
    #         multiples += 1
    #     if len(c1) != 300:
    #         weird += 1
    # print 'number of invalid lists: {}'.format(count)
    # print 'number of non-convergent solutions: {}'.format(problems)
    # print 'number of pair multiples: {}'.format(multiples)
    # print 'number of werid pair lists: {}'.format(weird)
        # for k,v in c.iteritems():
        #     print '{}:{}'.format(k,v)
    
    # for t in new:
    #     print t




if __name__ == '__main__':
    n = 25
    main(n)
