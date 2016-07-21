# Pairmaker

## Intro

Generates pairs for pair programming, that are guaranteed to not
repeat.
Modified from original created by asimjalis, available [here](https://github.com/asimjalis/pairmaker)

## How To Install And Use

Make a local copy.

    git clone https://github.com/asimjalis/pairmaker
    cd pairmaker

Edit the `students.txt` file and put one student name per line. Here
are some example students.

    Alexander
    Ben
    Cassandra
    Dana

For today's pairs run:

    ./pairmaker.py today
## Algorithm

Uses *round-robin tournament algorithm* as described at
<https://en.wikipedia.org/wiki/Round-robin_tournament>.

## Usage
```
    ./pairmaker.py [Date] [OPTIONS]
    
    [Date]: start date of cohort (MM/DD/YYYY formatted)  
    [path] (optional): path of desired output markdown file  
```
## Examples

    ./pairmaker.py 08/01/2016                        Pairs with start date 08/01/2016 written to pairs.md  
    ./pairmaker.py 08/01/2016 pairs_cohort_16.md     Pairs with start date 08/01/2016 written to pairs_cohort_16.md  
    ./pairmaker.py -help                              Usage message  

## Notes

- Looks for `students.txt` in directory where script running from
- File `students.txt` must contain student names one per line
- If no path specified writes to "pairs.md" in current directory


