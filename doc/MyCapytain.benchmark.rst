Benchmarks
==========

In the recent attempt to boost our system, we had a look on the performance of MyCapytain with different parser. Even if as 1.0.1 \
xmlparser() is the recommended tool, we highly recommend to switch to lxml.objectify.parse() parser for performance. In the following benchmark \
run with timeit.sh on the main repo (You need PerseusDL/canonical-latinLit somewhere ), the first line is run with lxml.etree, the second \
with objectify and the third with a pickled object.

**Testing on Seneca, Single Simple Passage**

- 100 loops, best of 3: 4.45 msec per loop
- 100 loops, best of 3: 4.15 msec per loop
- 100 loops, best of 3: 3.75 msec per loop

**Testing range**

- 100 loops, best of 3: 7.63 msec per loop
- 100 loops, best of 3: 7.72 msec per loop
- 100 loops, best of 3: 6.66 msec per loop

**Testing with a deeper architecture**

- 100 loops, best of 3: 18.2 msec per loop
- 100 loops, best of 3: 14.3 msec per loop
- 100 loops, best of 3: 9.31 msec per loop

**Testing with a deeper architecture at the end**

- 100 loops, best of 3: 18.2 msec per loop
- 100 loops, best of 3: 14.2 msec per loop
- 100 loops, best of 3: 9.34 msec per loop

**Testing with a deeper architecture with range**

- 100 loops, best of 3: 19.3 msec per loop
- 100 loops, best of 3: 14.3 msec per loop
- 100 loops, best of 3: 9.9 msec per loop

**Testing with complicated XPATH**

- 100 loops, best of 3: 751 usec per loop
- 100 loops, best of 3: 770 usec per loop
- 100 loops, best of 3: 617 usec per loop
