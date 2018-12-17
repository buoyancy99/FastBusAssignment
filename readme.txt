This is Boyuan's project code for CS170 Fall 2018 @ UC Berkeley
Rank: 3rd on EC and 18th on Normal Input
Our philosophy is to give a super fast algorithm(<5 min) for the project with decent performance!
Project description can be found as CS_170_FA18_Project_Spec.pdf

Group Members: Cathy Li and Jerry Wang

First download my packed data from 
https://drive.google.com/drive/folders/1-pfoQ7XkezIS9skOTqPnS2pvVqoeLBA1?usp=sharing

To run small, medium and large using all cores
	python3 multi.py
By now it should be ~46%. However, you might want to run
	python3 randomopt.py
to make small better aroung ~4%, this is randomized but almost gaurantees 


To run EC all_large using all cores
	python3 multiEC.py

==============================================
we used sml.pkl and all_large.pkl to store convered graphs into a single file to save IO time
to regenerate them, just delete it and run the corresponding code

sml.pkl is used to accelerate data loading
==============================================
Approximate time:
If you didn't sml.pkl file, you should expect several minutes on multi.py 
We ran it on my PC's Xeon E5-2673 v3 QS 12C/24T 2.4GHz-3.1GHz CPU and got following result:

IO ~ 2 min
Computing (running solve on all) ~ 103 seconds
By now you will see ~46% score
However randomopt.py is not included in above because it can be run for whatever iterations and almost always have improvement

If you use a laptop it might be slower because it has much less core count
PS: my Xeon E5 is purchased at only $150 from China! Cheaper than i7 or Ryzen but very good for multithreading
==============================================

File list:
eval_all.py    help you evaluate overall score on small, medium and large
maxpq.py       our max priority queue class
multi.py       main program to compute small, medium and large
multiEC.py     main program to compute all_large
output_scorer.py   single evaluator in skeleton code
priorityqueue.py   PQ class from internet
randomopt.py   random algorithm to improve small
score_funtion.py   quick evaluation of result without IO