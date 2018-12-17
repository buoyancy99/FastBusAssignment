from priorityqueue import MinHeapPriorityQueue, MaxHeapPriorityQueue
import random

class A():

    def __init__(self, A, rank):
        #a list use to rank obj in pq
        self.rank = rank
        self.obj = A

class MaxPQ():
	def __init__(self):
		self.pq = MaxHeapPriorityQueue(key = lambda x: x.rank)

	def insert(self, item, rank):

		self.pq.append(A(item, rank))

	def pop(self):
		return self.pq.pop()

	def remove(self, item):
		for j in range(len(self.pq._pq)):
				if self.pq._pq[j]._item.obj == item:
					self.pq.remove(self.pq._pq[j])
					break

	def change(self, item, dif):
		for j in range(len(self.pq._pq)):
			if self.pq._pq[j]._item.obj == item:
				new_val = [0, 0]
				new_val[0] = dif[0] + self.pq._pq[j]._value[0]
				new_val[1] = dif[1] + self.pq._pq[j]._value[1]
				self.pq.update(self.pq._pq[j], new_val, A(item, new_val))
				break

	def length(self):
		return len(self.pq._pq)

"""
def test():
	items = [str(random.randint(1, 100)) for _ in range(100)]
	ranks = [(random.randint(1, 100), random.randint(1, 100)) for _ in range(100)]
	case = General()
	for i in range(len(items)):
		case.insert(items[i], ranks[i])
	verify_max(case.pq)

def verify_max(pq):
     n = len(pq._pq)
     for i in range(n):
         left, right = 2*i + 1, 2*i + 2
         if left < n:
             assert pq._pq[i] >= pq._pq[left]
         if right < n:
             assert pq._pq[i] >= pq._pq[right]

def test_duplicate():
	case = General()
	case.insert("first", [10, 9])
	case.insert("first", [10, 9])
	assert case.pq.size == 1

def test_update():
	case = General()
	case.insert("first", [10, 9])
	case.insert("first", [8, 7])
	assert case.pq._pq[0]._value[0] == 8
	assert case.pq._pq[0]._value[1] == 7

def test_remove():
	case = General()
	case.insert("1", [10, 9])
	case.insert("2", [8, 7])
	case.insert("3", [6, 5])
	case.insert("4", [4, 3])
	case.remove("3")
	assert case.pq.size == 3
	case.insert("4", [200, 19])
	print(case.pq.pop().obj)
	print(case.pq.pop().obj)
	print(case.pq.pop().obj)
	#assert verify_max(case.pq)
def test_change():
	case = General()
	case.insert("1", [10, 9])
	case.insert("2", [8, 7])
	case.insert("3", [6, 5])
	case.insert("4", [4, 3])
	case.change("1", [11, 13])
	print(case.pq._pq[0]._value[0])
	assert case.pq._pq[0]._value[1] == 22



test()
test_remove()
test_update()
test_duplicate()
test_change()
"""