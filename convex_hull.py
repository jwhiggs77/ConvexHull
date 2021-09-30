
import math
from heapq import merge

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25


def partition(array, low, high):
	i = (low - 1)  # index of smaller element
	pivot = array[high].x()  # pivot

	for j in range(low, high):

		# If current element is smaller than or
		# equal to pivot
		if array[j].x() <= pivot:
			# increment index of smaller element
			i = i + 1
			array[i], array[j] = array[j], array[i]

	array[i + 1], array[high] = array[high], array[i + 1]
	return (i + 1)


def quickSort(array, low, high):
	if len(array) == 1:
		return array
	if low < high:
		# pi is partitioning index, arr[p] is now
		# at right place
		pi = partition(array, low, high)

		# Separately sort elements before
		# partition and after partition
		quickSort(array, low, pi - 1)
		quickSort(array, pi + 1, high)


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)

# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		# TODO: SORT THE POINTS BY INCREASING X-VALUE
		quickSort(points, 0, len(points) - 1)
		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		# polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]

		convexHull = self.find_convex_hull(points)
		polygon = [QLineF(convexHull[i],convexHull[(i+1)]) for i in range(len(convexHull) - 1)]
		polygon.append(QLineF(convexHull[len(convexHull) - 1],convexHull[0]))
		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		# self.showHull(key, GREEN)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	#divide and conquer
	def find_convex_hull(self, points) :
		mid_point = math.floor(len(points) / 2)
		if len(points) < 3 :
			# if len(points) == 2: return [points[1], points[0]]
			return points
		else:
			hullLeft = points[:mid_point]
			hullRight = points[mid_point:]
			hullLeft = self.find_convex_hull(hullLeft)
			hullRight = self.find_convex_hull(hullRight)
			return self.merge(hullLeft, hullRight)

	#finds upper and lower tangents and merges the hulls
	def merge(self, left, right) :
		if len(left) == 1 and len(right) == 1 : return right + left

		leftMostIndexOfRight = 0
		rightMost = left[0]
		rightMostIndexOfLeft = 0
		for i in left :
			if i.x() > rightMost.x() :
				rightMost = i
				rightMostIndexOfLeft += 1

		upperLeft = None
		upperRight = None
		lowerLeft = None
		lowerRight = None

		#find upper bound
		leftIndex = rightMostIndexOfLeft
		rightIndex = leftMostIndexOfRight
		# FIND UPPER TANGENT INDEXES
		# Keep track of the previous lines slope, starting with the left/right-most points of either hull
		slope = self.find_slope(left[leftIndex], right[rightIndex])
		updated = True
		while updated :
			updated = False
			if slope > self.find_slope(left[(leftIndex - 1) % len(left)], right[rightIndex]):
				leftIndex = (leftIndex - 1)  % len(left)
				slope = self.find_slope(left[leftIndex], right[rightIndex])
				updated = True

			if slope < self.find_slope(left[leftIndex], right[(rightIndex + 1) % len(right)]):
				rightIndex = (rightIndex + 1)  % len(right)
				slope = self.find_slope(left[leftIndex], right[rightIndex])
				updated = True
		upperLeft = leftIndex
		upperRight = rightIndex

		#FIND LOWER TANGENT INDEXES
		leftIndex = rightMostIndexOfLeft
		rightIndex = leftMostIndexOfRight
		slope = self.find_slope(left[leftIndex], right[rightIndex])
		updated = True
		while updated :
			updated = False
			if slope < self.find_slope(left[(leftIndex + 1)  % len(left)], right[rightIndex]):
				leftIndex = (leftIndex + 1)  % len(left)
				slope = self.find_slope(left[leftIndex], right[rightIndex])
				updated = True

			if slope > self.find_slope(left[leftIndex], right[(rightIndex - 1) % len(right)]):
				rightIndex = (rightIndex - 1) % len(right)
				slope = self.find_slope(left[leftIndex], right[rightIndex])
				updated = True
		lowerLeft = leftIndex
		lowerRight = rightIndex

		mergedHull = self.merge_helper(upperLeft, upperRight, lowerRight, lowerLeft, left, right)
		keyPoints = [left[0], left[upperLeft], right[upperRight], right[lowerRight], left[lowerLeft]]
		return mergedHull
		#return array of new points sorted clockwise

	#does the actual merging of the two hulls into one
	def merge_helper(self, upperLeft, upperRight, lowerRight, lowerLeft, left, right):
		mergedHull = [left[0]]
		pointIndex = 0
		while pointIndex != upperLeft and pointIndex < len(left):
			if pointIndex > 0: mergedHull.append(left[pointIndex])
			pointIndex = pointIndex + 1
		if left[0] != left[upperLeft]: mergedHull.append(left[upperLeft])

		mergedHull.append(right[upperRight])
		pointIndex = upperRight
		while pointIndex != lowerRight and pointIndex < len(right):
			if pointIndex != upperRight: mergedHull.append(right[pointIndex])
			pointIndex = pointIndex + 1
		if upperRight != lowerRight: mergedHull.append(right[lowerRight])

		if lowerLeft != 0:
			mergedHull.append(left[lowerLeft])
			pointIndex = lowerLeft + 1
			while pointIndex < len(left):
				slopeTo0 = self.find_slope(left[0], left[lowerLeft])
				slope = self.find_slope(left[pointIndex], left[lowerLeft])
				if slope > slopeTo0:
					mergedHull.append(left[pointIndex])
				pointIndex = pointIndex + 1

		return mergedHull

	def find_slope(self, left, right) :
		return (left.y() - right.y()) / (left.x() - right.x())

##################################################################################################
##################################################################################################

# class time_trial():
# 	def compute_hull(self, points):
# 		assert( type(points) == list and type(points[0]) == QPointF )
#
# 		t1 = time.time()
# 		quickSort(points, 0, len(points) - 1)
# 		t2 = time.time()
#
# 		t3 = time.time()
# 		# this is a dummy polygon of the first 3 unsorted points
# 		# polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
#
# 		convexHull = self.find_convex_hull(self, points)
# 		polygon = [QLineF(convexHull[i],convexHull[(i+1)]) for i in range(len(convexHull) - 1)]
# 		polygon.append(QLineF(convexHull[len(convexHull) - 1],convexHull[0]))
# 		t4 = time.time()
#
# 		return t1, t2, t3, t4
#
# 	#divide and conquer
# 	def find_convex_hull(self, points) :
# 		mid_point = math.floor(len(points) / 2)
# 		if len(points) < 3 :
# 			# if len(points) == 2: return [points[1], points[0]]
# 			return points
# 		else:
# 			hullLeft = points[:mid_point]
# 			hullRight = points[mid_point:]
# 			hullLeft = self.find_convex_hull(self, hullLeft)
# 			hullRight = self.find_convex_hull(self, hullRight)
# 			return self.merge(self, hullLeft, hullRight)
#
# 	def merge(self, left, right) :
# 		if len(left) == 1 and len(right) == 1 : return right + left
#
# 		leftMostIndexOfRight = 0
# 		rightMost = left[0]
# 		rightMostIndexOfLeft = 0
# 		for i in left :
# 			if i.x() > rightMost.x() :
# 				rightMost = i
# 				rightMostIndexOfLeft += 1
#
# 		upperLeft = None
# 		upperRight = None
# 		lowerLeft = None
# 		lowerRight = None
#
# 		#find upper bound
# 		leftIndex = rightMostIndexOfLeft
# 		rightIndex = leftMostIndexOfRight
# 		# FIND UPPER TANGENT INDEXES
# 		# Keep track of the previous lines slope, starting with the left/right-most points of either hull
# 		slope = self.find_slope(self, left[leftIndex], right[rightIndex])
# 		updated = True
# 		while updated :
# 			updated = False
# 			if slope > self.find_slope(self, left[(leftIndex - 1) % len(left)], right[rightIndex]):
# 				leftIndex = (leftIndex - 1)  % len(left)
# 				slope = self.find_slope(self, left[leftIndex], right[rightIndex])
# 				updated = True
#
# 			if slope < self.find_slope(self, left[leftIndex], right[(rightIndex + 1) % len(right)]):
# 				rightIndex = (rightIndex + 1)  % len(right)
# 				slope = self.find_slope(self, left[leftIndex], right[rightIndex])
# 				updated = True
# 		upperLeft = leftIndex
# 		upperRight = rightIndex
#
# 		#FIND LOWER TANGENT INDEXES
# 		leftIndex = rightMostIndexOfLeft
# 		rightIndex = leftMostIndexOfRight
# 		slope = self.find_slope(self, left[leftIndex], right[rightIndex])
# 		updated = True
# 		while updated :
# 			updated = False
# 			if slope < self.find_slope(self, left[(leftIndex + 1)  % len(left)], right[rightIndex]):
# 				leftIndex = (leftIndex + 1)  % len(left)
# 				slope = self.find_slope(self, left[leftIndex], right[rightIndex])
# 				updated = True
#
# 			if slope > self.find_slope(self, left[leftIndex], right[(rightIndex - 1) % len(right)]):
# 				rightIndex = (rightIndex - 1) % len(right)
# 				slope = self.find_slope(self, left[leftIndex], right[rightIndex])
# 				updated = True
# 		lowerLeft = leftIndex
# 		lowerRight = rightIndex
#
# 		mergedHull = self.merge_helper(self, upperLeft, upperRight, lowerRight, lowerLeft, left, right)
# 		keyPoints = [left[0], left[upperLeft], right[upperRight], right[lowerRight], left[lowerLeft]]
# 		return mergedHull
# 		#return array of new points sorted clockwise
#
# 	def merge_helper(self, upperLeft, upperRight, lowerRight, lowerLeft, left, right):
# 		mergedHull = [left[0]]
# 		pointIndex = 0
# 		while pointIndex != upperLeft and pointIndex < len(left):
# 			if pointIndex > 0: mergedHull.append(left[pointIndex])
# 			pointIndex = pointIndex + 1
# 		if left[0] != left[upperLeft]: mergedHull.append(left[upperLeft])
#
# 		mergedHull.append(right[upperRight])
# 		pointIndex = upperRight
# 		while pointIndex != lowerRight and pointIndex < len(right):
# 			if pointIndex != upperRight: mergedHull.append(right[pointIndex])
# 			pointIndex = pointIndex + 1
# 		if upperRight != lowerRight: mergedHull.append(right[lowerRight])
#
# 		if lowerLeft != 0:
# 			mergedHull.append(left[lowerLeft])
# 			pointIndex = lowerLeft + 1
# 			while pointIndex < len(left):
# 				slopeTo0 = self.find_slope(self, left[0], left[lowerLeft])
# 				slope = self.find_slope(self, left[pointIndex], left[lowerLeft])
# 				if slope > slopeTo0:
# 					mergedHull.append(left[pointIndex])
# 				pointIndex = pointIndex + 1
#
#
# 		# mergedHull = [left[upperRight]]
# 		# pointIndex = upperRight
# 		# while pointIndex != lowerRight and pointIndex < len(right):
# 		# 	if pointIndex != upperRight: mergedHull.append(right[pointIndex])
# 		# 	pointIndex = pointIndex + 1
# 		#
# 		# mergedHull.append(right[lowerRight])
# 		# mergedHull.append(left[lowerLeft])
# 		#
# 		# pointIndex = lowerLeft
# 		# while pointIndex != upperLeft and pointIndex < len(left):
# 		# 	if pointIndex!= lowerLeft: mergedHull.append(left[pointIndex])
# 		# 	pointIndex = pointIndex + 1
# 		# mergedHull.append(left[upperLeft])
#
#
# 		return mergedHull
#
# 	def find_slope(self, left, right) :
# 		return (left.y() - right.y()) / (left.x() - right.x())
#
#
# import pandas as pd
# import random
#
# random.seed(10)
#
# iteration = 0
# for i in [10, 100, 10000, 100000, 500000, 1000000]:
# 	for j in range(5):
# 		points = [QPointF(random.uniform(-1, 1), random.uniform(-1, 1)) for k in range(i)]
# 		trial = time_trial
# 		time1, time2, time3, time4 = trial.compute_hull(trial, points)
# 		dataframe = pd.DataFrame({'num_points': i, 'algorithm_time': (time4 - time1)}, index = [iteration])
# 		with open('/Users/joshuahiggins/Desktop/Desktop - Joshua’s MacBook Air/CS 312/proj2/convex_analysis.csv', 'a') as f:
# 			dataframe.to_csv(f, header=False)
# 		iteration+= 1
