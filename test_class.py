from random import shuffle
import datetime as dt

class PairMaker(object):
    '''
    creates pairs of students until all students have paired with all other students
    '''
    def __init__(self, start_date = None, num_students = 5):
        self.start_date = start_date
        self._setup_from_num(num_students)
        self.all_pairs = None
        self.out_dict = None

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
        print len(self.all_pairs)
        cur_day = self.start_date
        while len(self.all_pairs) > 0:
            if cur_day.weekday() > 4:
                cur_day = cur_day + dt.timedelta(1)
                continue
            cur_pair = self.all_pairs.pop()
            shuffle(cur_pair)
            out_dict[cur_day] = cur_pair
            cur_day = cur_day + dt.timedelta(1)
        self.out_dict = out_dict

    def make_md_table(self):
        if not self.out_dict:
            self._make_output_dict()
        dates = sorted(self.out_dict.keys())
        days_written = 0
        week_count = 1
        with open('test.md','w') as f:
            for date in dates:
                if days_written % 5 == 0:
                    f.write('Week {}:\n'.format(week_count))
                    f.write('```')
                    week_count += 1
                f.write('{}\n'.format(date.strftime('%m/%d/%Y')))
                for i,pair in enumerate(self.out_dict[date]):
                    f.write('|{}|{}|\n'.format(i,pair))
                days_written += 1
                




if __name__ == '__main__':
    
    pm = PairMaker(dt.datetime.now())
    pm.make_md_table()
    # pm._make_output_dict()
    # for k,v in pm.out_dict.iteritems():
    #     print k.strftime('%m/%d/%Y'),v

