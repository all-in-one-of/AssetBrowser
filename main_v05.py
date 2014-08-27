node = hou.pwd()
geo = node.geometry()
nodeMultiplier = 1
numOfIterations = num

class treeNode(object):
	"""TreeNode element"""
	def __init__(self, position):
		super(treeNode, self).__init__()
		self.position = position
		self.attractionCandidates = list()
		self.averagePosition = hou.Vector3(0.0, 0.0, 0.0)
		self.averagePositionNormalized = hou.Vector3(0.0, 0.0, 0.0)
		self.nextNodesPosition = hou.Vector3(0.0, 0.0, 0.0)
		self.numOfInfluencors = 0
		self.candidates = set()

	def getPosition(self):
		return (self.position[0], self.position[1], self.position[2])


	def calculateAverageDir(self):
		#Node has no influencor
		self.numOfInfluencors = len(self.attractionCandidates)
		if self.numOfInfluencors == 0:
			return -1

		else:
			#print "num of Influencors" + str(self.numOfInfluencors)
			counter = 0
			for i in self.attractionCandidates:
				counter += 1
				#Calculate the Vectors from the Currents Nodes Position
				abVector = (i[0] - self.position[0], i[1] - self.position[1], i[2] - self.position[2])
				#print "Distance Vector  " + str(abVector) + "\n"
				print "I am Node  " + str(self.position) + " Closest Point is" + str(i) + "\n"


				self.averagePosition[0] += i[0]
				self.averagePosition[1] += i[1]
				self.averagePosition[2] += i[2]

			self.averagePosition[0] = self.averagePosition[0] / self.numOfInfluencors
			self.averagePosition[1] = self.averagePosition[1] / self.numOfInfluencors
			self.averagePosition[2] = self.averagePosition[2] / self.numOfInfluencors
			#print "self av Pos" + str(self.averagePosition)
			return self.averagePosition

	def createNextNode(self):
		self.averagePositionNormalized = self.averagePosition.normalized()
		self.nextNodesPosition = hou.Vector3(self.averagePositionNormalized[0] * nodeMultiplier, self.averagePositionNormalized[1] * nodeMultiplier, self.averagePositionNormalized[2] * nodeMultiplier)
		return self.nextNodesPosition

	def resetAll(self):
		self.numOfInfluencors = 0
		self.averagePosition = hou.Vector3(0.0, 0.0, 0.0)
		self.averagePositionNormalized = hou.Vector3(0.0, 0.0, 0.0)
		self.attractionCandidates = list()
		self.nextNodesPosition = hou.Vector3(0.0, 0.0, 0.0)



def testUnit(uVector):
	uLength = math.sqrt(uVector[0]**2 + uVector[1]**2 + uVector[2]**2)



	testVector2 = ((uVector[0]/uLength)**2 + 
				   (uVector[1]/uLength)**2 + 
				   (uVector[2]/uLength)**2)

	return testVector2

treeNodes = list()
treeNodesHelper = list()

pointKeys = dict()

attractionPoints = list()
Candidates = set()

#Create Initial TreeNode
firstTreeNode = treeNode(hou.Vector3(0.0, 0.0, 0.0))
treeNodes.append(firstTreeNode)

#secondTreeNode = treeNode(hou.Vector3(-2.0, 0.0, 0.0))
#treeNodes.append(secondTreeNode)


#Populate Node Tree
#for j in treeNodes:
#	treeNodesHelper.append(j.getPosition())



#print treeNodesHelper.index((0.0, 1.0, 0.0))


#Prepare list for kd-tree
for points in geo.points():
    currentPosition = points.position()
    attractionPoints.append((currentPosition[0], currentPosition[1], currentPosition[2]))
    hashString = str(currentPosition[0]) + str(currentPosition[1]) + str(currentPosition[2])
    pointKeys[hashString] = points.number()

#Bild Tree from input
tree = KDTree.construct_from_data(attractionPoints)
counter = 0

for i in range(0,numOfIterations):
	#Populate Node Tree
	del treeNodesHelper[:]
	for j in treeNodes:
		treeNodesHelper.append(j.getPosition())

	print "##### overall debug ######"
	for i in treeNodes: 
		print i.position
	print "\n\n"
	print str(treeNodesHelper)
	print "##### overall debug END ######" + "\n"
	#Create Tree for Nodes
	NodesTree = KDTree.construct_from_data(treeNodesHelper)
	helperList = list()
	#Find Candidates
	Candidates = set()
	for i in treeNodesHelper:
		neighbours = tree.query(query_point=(i), t=3)
		for oneNeighbour in neighbours:
			Candidates.add(oneNeighbour)

	#Associate Canddiates with Nodes
	print ("==== Associcated Nodes ===== \n")
	for i in Candidates:
		nearestNode = NodesTree.query(query_point=(i), t = 1)
		currentNodeIndex = treeNodesHelper.index(nearestNode[0])
		print "Candidate: " + str((i[0], i[1], i[2])) + " ASSOC WITH*: " + str(nearestNode) +" " + str(currentNodeIndex) + "Index*:" #+ str(treeNodes[currentNodeIndex].position)
		treeNodes[currentNodeIndex].attractionCandidates.append(i)
		print "current Attr Canddiates: " + str(treeNodes[currentNodeIndex].attractionCandidates) + "\n"


	print "== nodes processing ============================ " + str(counter) +"\n"
	nodesCounter = 0
	numNodes = len(treeNodes)
	for i in treeNodes:
		if nodesCounter <= numNodes: #prevent overcounting
			nodesCounter += 1
			if i.calculateAverageDir() != -1: #maybe do it on the fly?
				print "====== next Node " + str(counter) +" ===== \n"
				print str(i.position)

				#print "function next noden" + str(i.createNextNode())
				nextNodesPosition = i.createNextNode()
				#print "Previous Tree-Nodes Position: " + str(i.getPosition())
				nextAveragePos = hou.Vector3(nextNodesPosition[0] +i.getPosition()[0] , nextNodesPosition[1] +i.getPosition()[1], nextNodesPosition[2] +i.getPosition()[2])
				nextNode = treeNode(nextAveragePos)
				treeNodes.append(nextNode)
				
				i.resetAll()
			else:
				print "this node has no candidates"

		nodesCounter += 1

	#treeNodes.extend(helperList)
	counter += 1


#Create a visual feedback (debug)
print "Nodes Total: " + str(len(treeNodes))
for i in treeNodes:
	tmp = geo.createPoint()
	tmp.setAttribValue("P", i.position)
	tmp.setAttribValue("Cd", hou.Vector3(0.0, 1.0, 0.0))


print("===== END =====")
# Add code to modify contents of geo.
# Use drop down menu to select examples.