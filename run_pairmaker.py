#!/usr/bin/env python

from pairmaker import PairMaker
import sys, datetime

# Usage message.
USAGE = '''
Usage: 
{program} [Date] [path]

[Date]: start date of cohort (MM/DD/YYYY formatted)
[path] (optional): path of desired output markdown file

Notes:
- Looks for students.txt in directory where script running from
- File students.txt must contain student names one per line
- If no path specified writes to "pairs.md" in current directory

'''.format(program=sys.argv[0]).strip()

STUDENTS_FILE_NAME = 'students.txt'

def argv_to_exception(argv):
    err = False
    if len(argv) < 2 or sys.argv[1] in ['-h','-?','-help']:
        print USAGE
        sys.exit()
    elif len(argv) > 3:
        print USAGE
        sys.exit()
    try:
        datetime.datetime.strptime(sys.argv[1].strip(),'%m/%d/%Y')
    except ValueError:
        raise ValueError("Start Date must be MM/DD/YYYY")

def main(argv):
    argv_to_exception(argv)
    pm = PairMaker(start_date = argv[1], students = STUDENTS_FILE_NAME)
    if len(argv) == 3:
        pm.make_md_tables(argv[2])
    else:
        pm.make_md_tables()

if __name__ == '__main__':
    main(sys.argv)
 
