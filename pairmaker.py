from random import shuffle
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
        self.out_dict = None
        if students:
            self._load_student_file(students)
        else:
            self.students = None


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
        if self.odd_num:
            students.append(' ')
        shuffle(students)
        if self.odd_num:
            self.empty_index = students.index(' ')
        else:
            self.empty_index = -1
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
            elif cur_day.weekday() == 0 and cur_day != self.start_date:
                cur_week += 1
                out_dict['week {}'.format(cur_week)] = cur_dict
                cur_dict = {}
            cur_pair = self.all_pairs.pop()
            shuffle(cur_pair)
            cur_dict[cur_day.strftime("%A")] = cur_pair
            cur_day = cur_day + dt.timedelta(1)
        out_dict['week {}'.format(cur_week+1)] = cur_dict
        self.out_dict = out_dict

    def make_md_tables(self, out_path = 'pairs.md'):
        '''
        creates a markdown file of the student pairs
        out_path: string, output path to write markdown tables to
        '''
        if not self.out_dict:
            self._make_output_dict()
        weeks = sorted(self.out_dict.keys())
        if self.students:
            write_students = True
        else:
            write_students = False
        triples = []
        with open(out_path,'w') as f:
            for week in weeks:
                w_str = '{}\n\n|day of week|groups|\n|---|---|\n'.format(week)
                all_days = self._make_week(self.out_dict[week].keys())
                solo = None
                for day in all_days:
                    ap = self.out_dict[week][day]
                    shuffle(ap)
                    pairs = []
                    for pair in ap:
                        if self.empty_index in pair:
                            ind = 1 - pair.index(self.empty_index)
                            solo = (pair[ind],)
                        else:
                            pairs.append(pair)
                    if solo:
                        pairs = self._add_single(pairs,solo)
                    if write_students:
                        pairs = [tuple(self.students[i] for i in pair) for pair in pairs]
                    w_str += '|{}|{}|\n'.format(day, ',<br>'.join(str(x) for x in pairs))
                f.write(w_str)
            f.write('\n')

    def _add_single(self, pairs, solo):
        output = set()
        to_add = True
        add = False
        vals = Counter()
        for pair in pairs:
            val = self.counts[pair[0]] + self.counts[pair[1]]
            vals[pair] = val
            output.add(pair)
        update = vals.most_common()[-1][0]
        output.remove(update)
        self.counts[update[0]] += 1
        self.counts[update[1]] += 1
        new_entry = (update[0], update[1], solo[0])
        output.add(new_entry)
        return list(output)

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


if __name__ == '__main__':
    make_fake_students(26)
    pm = PairMaker(start_date = '08/01/2016',students = 'students.txt')
    pm.make_md_tables()

