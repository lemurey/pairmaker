from random import shuffle, choice
from math import ceil
import datetime as dt

class PairMaker(object):
    '''
    creates pairs of students until all students have paired with all other students
    '''
    def __init__(self, start_date = None, num_students = 5, debug = False):
        self.start_date = start_date
        self.debug = debug
        self._setup_from_num(num_students)
        self.all_pairs = None
        self.out_dict = None
        self.students = None


    def set_start_date(self, date):
        self.start_date = date

    def load_student_file(self, path):
        students = []
        with open(path, 'r') as f:
            for line in f:
                student = line.strip()
                students.append(student)
        self._setup_from_num(len(students))
        if self.odd_num:
            students.append(' ')
        shuffle(students)
        self.empty_index = students.index(' ')
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

    def _make_output_dict(self):
        out_dict = {}
        if not self.all_pairs:
            self._make_index_lists()
        cur_day = self.start_date
        cur_week = 0
        cur_dict = {}
        while len(self.all_pairs) > 0:
            if cur_day.weekday() > 4:
                cur_day = cur_day + dt.timedelta(1)
                continue
            elif cur_day.weekday() == 0:
                if len(cur_dict) != 0:
                    cur_week += 1
                if len(cur_dict) > 0:
                    out_dict['week {}'.format(cur_week)] = cur_dict
                cur_dict = {}
            cur_pair = self.all_pairs.pop()
            shuffle(cur_pair)
            cur_dict[cur_day.strftime("%A")] = cur_pair
            cur_day = cur_day + dt.timedelta(1)
        out_dict['week {}'.format(cur_week+1)] = cur_dict
        self.out_dict = out_dict

    def _check_next_pair(self, pair, next_pair):
        if self.empty_index in next_pair:
            extra = next_pair[0]
            if extra == self.empty_index:
                extra = next_pair[1]
            pair = (pair[0], pair[1], extra)
        return pair

    def make_md_table(self):
        if not self.out_dict:
            self._make_output_dict()
        weeks = sorted(self.out_dict.keys())
        dows = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
        days_written = 0
        week_count = 1
        write_students = False
        if self.students:
            write_students = True
            max_len = len(self.students)/2
        next_pair = []
        skip = False
        triples = []
        with open('test.md','w') as f:
            for week in weeks:
                f.write('{}\n\n'.format(week))
                all_days = []
                for day in dows:
                    if day in self.out_dict[week].keys():
                        all_days.append(day)
                # all_days = self.out_dict[week].keys()
                # f.write('|day of week|groups|\n|---|---|\n'.format('|'.join(all_days),'|'.join('---' for _ in all_days)))
                f.write('|day of week|groups|\n|---|---|\n')
                for day in all_days:
                    f.write('|{}|'.format(day))
                    pairs = []
                    ap = self.out_dict[week][day]
                    shuffle(ap)
                    for i,pair in enumerate(ap):
                        if skip:
                            skip = False
                            continue
                        if i < max_len - 1:
                            next_pair = self.out_dict[week][day][i+1]
                        pair = self._check_next_pair(pair, next_pair)
                        if i == 0 and len(pair) == 2:
                            check = self._check_next_pair(next_pair, pair)
                            if len(check) == 3:
                                pair = check
                        next_pair = pair
                        if len(pair) == 3:
                            triples.append(pair)
                            skip = True
                        if write_students:
                            pair = tuple((self.students[i] for i in pair))
                        pairs.append(pair)
                    f.write('{}|\n'.format(',<br>'.join([str(x) for x in pairs])))
                f.write('\n')
            pairs = []
            counts = {}
            for triple in triples:
                    if write_students:
                        pair = (self.students[triple[0]],self.students[triple[1]])
                    else:
                        pair = (triple[0], triple[1])
                    for entry in pair:
                        if entry in counts:
                            counts[entry] += 1
                        else:
                            counts[entry] = 1
                    pairs.append(pair)
            if self.debug:
                # f.write('tripled:\n\n')
                # f.write('{}\n'.format(', '.join(str(x) for x in pairs)))
                # f.write('\n')
                for k,v in counts.iteritems():
                    f.write('{}: {}   \n'.format(k,v))
            return len(counts), max(counts.values())


def make_fake_students(num_students = 19):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    fs = range(3,9)
    ls = range(5,12)
    with open('students.txt','w') as file:
        for i in range(num_students):
            f = choice(fs)
            l = choice(ls)
            name = ''
            for i in range(f + l):
                lett = choice(alphabet)
                if i > 0 and i != f:
                    lett = lett.lower()
                if i == f:
                    name += ' '
                name += lett
            file.write(name + '\n')
if __name__ == '__main__':
    # make_fake_students()
    pm = PairMaker(dt.datetime.strptime('08/01/2016','%m/%d/%Y'), debug = True)
    pm.load_student_file('students.txt')
    num_students = len(pm.students)
    max_val = ceil(pm.cycle_len*2/float(num_students)) + 1
    if ' ' in pm.students:
        num_students -= 1
    for _ in xrange(10000):
        t, t1 = pm.make_md_table()
        if t == num_students and t1 <= max_val:
            print 'converged, ' + str(_)
            break
    # print pm.out_dict
    # pm._make_output_dict()
    # for k,v in pm.out_dict.iteritems():
    #     print k,v

