import time
import json
import math
import numpy as np

'''
	Visitor JSON file:
	{
		"inside":["currentDateIndex", visitorAmount],
    
		"dateIndex0":[24IntegerWithItsVisitorAmount],
		"dateIndex1":[24IntegerWithItsVisitorAmount],
		    ...
		"dateIndexN":[24IntegerWithItsVisitorAmount]
	}
'''

class Visitor:
	def __init__(self,url,a=0,b=0,direction=True,vertical=False,x=0):
		#Get the visitor data url
		self.dataUrl = url
		#Set time list variable
		self.hourList = ["00-01","01-02","02-03","03-04","04-05","05-06","06-07","07-08","08-09","09-10","10-11","11-12",
        				"12-13","13-14","14-15","15-16","16-17","17-18","18-19","19-20","20-21","21-22","22-23","23-24"]
		#Linear function variable
		self.a = a
		self.b = b
		self.direction = direction
  
		self.vertical = vertical
		self.x = x
		#Create a time index
		self.currentHourIndex = int(time.time()/(60*60))
		self.currentDayIndex = int(self.currentHourIndex/24)
		#Loading data
		try: #If the visitor data exist
			with open(self.dataUrl,'r') as file:
				#Retreave all data
				self.record = json.load(file)
			#Get the amount of visitor inside of the day
			if self.record['inside'][0] == self.currentDayIndex:
				self.inside = self.record['inside'][1]
			else:
				self.inside = 0
			#Count the number of visitor entered today
			self.today = 0
			for i in range(24):
				try:
					self.today = self.today + self.record[str(self.currentDayIndex)][i]
				except:
					continue
		except :
			self.record = {
    			'inside':[self.currentDayIndex,0],
            	str(self.currentDayIndex):[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
          	}
			self.inside = 0
			self.today = 0
			with open(self.dataUrl,'w') as file:
				file.write(json.dumps(self.record))
		#Store the prediction value
		self.old_pred = None


	def enter(self):
		#Get actual time data
		self.updateTime()
		#Increament the new data
		self.inside = self.inside + 1
		self.today = self.today + 1
		self.record['inside'] = [self.currentDayIndex,self.inside]
		try:
			self.record[str(self.currentDayIndex)][str(self.currentHourIndex-(self.currentDayIndex*24))] = self.record[str(self.currentDayIndex)][str(self.currentHourIndex-(self.currentDayIndex*24))] + 1
		except:
			self.record[str(self.currentDayIndex)] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			self.record[str(self.currentDayIndex)][str(self.currentHourIndex-(self.currentDayIndex*24))] = self.record[str(self.currentDayIndex)][str(self.currentHourIndex-(self.currentDayIndex*24))] + 1
		#Save data
		with open(self.dataUrl,'w') as file:
			file.write(json.dumps(self.record))

	def exit(self):
		#Get actual time data
		self.updateTime()
		#Decreament the new data
		self.inside = self.inside - 1
		self.record['inside'] = [self.currentDayIndex,self.inside]
		#Save data
		with open(self.dataUrl,'w') as file:
			file.write(json.dumps(self.record))
	
	def fline(self, x):
		return (self.a*x)+self.b
	def gline(self, y):
		return (y-self.b)/self.a

	def check(self, prediction):
		'''
		pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]
			boxes = [[[x1,y1,x2,y2],[x1,y1,x2,y2],...,[x1,y1,x2,y2]]]
		   scores = [[p1,p2,p3,...,pn]]
		  classes = [[c1,c2,c3,...,cn]]
    
		f = self.a * x + self.b
  
		We confirm that a person entered when :
		- is vertical : (Direction : Left to Right)
			x1 < self.x
			x2 > self.x
		- self.a < 0 : (Direction : Bottom-Left to Top-Right) 
  			x1 < gline(y1) and y1 < fline(x1)
			x2 > gline(y2) and y2 > fline(x2)
		- self.a = 0 : (Direction : Bottom to Top)
			y1 < fline(x1)
			y2 > fline(x2)
		- self.a > 0 : (Direction : Top-Left to Bottom-Right)
			x1 < gline(y1) and y1 > fline(x1)
			x2 > gline(y2) and y2 < fline(x2)
  		'''

		if(self.old_pred == None):
			return (0,0)
		else:
			bbox_coordinate = []
   
			for i in range(50):
				if (prediction[1][0][i] < 0.45 and prediction[2][0][i] == 2):
					continue
				bbox_coordinate.append([(prediction[0][0][0][i][0]+prediction[0][0][0][i][2])/2])
				#bbox_coordinate.append([(prediction[0][0][0][i][0]+prediction[0][0][0][i][2])/2,(prediction[0][0][0][i][1]+prediction[0][0][0][i][3])/2])
				
				entering = False
				exiting = False
    
				for j in range(len(self.old_pred)):
					if math.abs(bbox_coordinate[i][0]-self.old_pred[j][0]) < 0.02:
						if (self.old_pred[j][0] < self.x and bbox_coordinate >= self.x):
							entering = True
						elif (self.old_pred[j][0] > self.x and bbox_coordinate <= self.x):
							exiting = True

						'''
					if math.abs(bbox_coordinate[i][0]-self.old_pred[j][0])+math.abs(bbox_coordinate[i][1]-self.old_pred[j][1]) < 0.02 :
     					if self.vertical:
							if self.direction == False:
								if (self.old_pred[j][0] < self.x and 
									bbox_coordinate >= self.x):
									entering = True
						elif self.a < 0:
							if self.direction == False:
								if (self.old_pred[j][0] < self.gline(self.old_pred[j][1]) and
									self.old_pred[j][1] < self.fline(self.old_pred[j][0]) and
									bbox_coordinate[i][0] > self.gline(bbox_coordinate[i][1]) and
									bbox_coordinate[i][1] > self.fline(bbox_coordinate[i][0])
									):
									entering = True
									exiting = True
						elif self.a == 0:
							if self.direction == False:
								if (self.old_pred[j][1] < self.fline(self.old_pred[j][0]) and
									bbox_coordinate[i][1] > self.fline(bbox_coordinate[i][0])):
									entering = True
						elif self.a > 0:
							if (self.old_pred[j][0] < self.gline(self.old_pred[j][1]) and 
           						self.old_pred[j][1] > self.fline(self.old_pred[j][0]) and
                 				bbox_coordinate[i][0] > self.gline(bbox_coordinate[i][1]) and
                     			bbox_coordinate[i][1] < self.fline(bbox_coordinate[i][0])):
								if self.direction == False:
									entering = True
								else:
									exiting = True
						'''
					
					if entering:
						self.enter()
					if exiting:
						self.exit()
      
		self.old_pred = bbox_coordinate
		return (self.today, self.inside)
			

	def updateTime(self):
		self.currentHourIndex = int(time.time()/(60*60))
		self.currentDayIndex = int(self.currentHourIndex/24)