import copy

atrPARENT = geo.findPointAttrib("Cd")

nodeMultiplier = 0.3
numOfIterations = num
KILLDISTANCE = 1
def lengthVector(vVector):
    vVector = math.sqrt(vVector[0]**2 + vVector[1]**2 + vVector[2]**2)  
    return vVector

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
            counter = 0
            for i in self.attractionCandidates:
                counter += 1
                #Calculate the Vectors from the Currents Nodes Position
                abVector = (i.position()[0] - self.position[0], i.position()[1] - self.position[1], i.position()[2] - self.position[2])
                #print "Distance Vector  " + str(abVector) + "\n"
                #print "I am Node  " + str(self.position) + " Closest Point is" + str(i) + "\n"
                #print "postition node: " + str(self.position) + " position point " + str(i.position())
                #print "Length of Vector: " +  str(lengthVector(abVector))
                if lengthVector(abVector) < KILLDISTANCE:
                    attractionPointsKill.append(i)
                    #print "deleted"


                self.averagePosition[0] += abVector[0] #i[0]
                self.averagePosition[1] += abVector[1] #i[1]
                self.averagePosition[2] += abVector[2] #i[2]

            self.averagePosition[0] = self.averagePosition[0] / self.numOfInfluencors
            self.averagePosition[1] = self.averagePosition[1] / self.numOfInfluencors
            self.averagePosition[2] = self.averagePosition[2] / self.numOfInfluencors
            ##print "self av Pos" + str(self.averagePosition)
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
attractionPointsKill = list()

pointKeys = dict()

attractionPoints = list()
attractionPointsHelper = list()
Candidates = set()



###################################
## INITIALIZIATION OF INPUT DATA ##
###################################

anotherPointsList = list()
for points in geo.points():
    currentPosition = points.position()
    #attractionPoints.append((currentPosition[0], currentPosition[1], currentPosition[2]))
    hashString = str(currentPosition[0]) + str(currentPosition[1]) + str(currentPosition[2])
    #pointKeys[hashString] = points.number()

    #Check new incoming data what it is by defining color
    isNode  = points.attribValue("Cd")[1]
    
    #If Point is green, then it is a Node
    if isNode == 1.0:
        tempNode = treeNode(hou.Vector3(currentPosition[0], currentPosition[1], currentPosition[2]))
        treeNodes.append(tempNode)
    #else it is just an Attraction Point
    else:
        attractionPointsHelper.append((currentPosition[0], currentPosition[1], currentPosition[2]))
        attractionPoints.append(points)
    #print "is it a Node? : " + str(isNode)


counter = 0



#Bild Tree from input
trashAttractionPointHelper = copy.deepcopy(attractionPointsHelper)
AttractionPointsTree = KDTree.construct_from_data(trashAttractionPointHelper)
for j in treeNodes:
    treeNodesHelper.append((j.getPosition()[0],j.getPosition()[1],j.getPosition()[2]) )


trashTreeHelper = copy.deepcopy(treeNodesHelper)
NodesTree = KDTree.construct_from_data(trashTreeHelper) #CONSTRUCT FROM DATA juggles the order!

helperList = list()

#Find Candidates
Candidates = set()
for i in treeNodesHelper:
    neighbours = AttractionPointsTree.query(query_point=(i), t=3)
    for oneNeighbour in neighbours:
        Candidates.add(oneNeighbour)

#Associate Canddiates with Nodes
#print ("==== Associcated Nodes ===== \n")
for i in Candidates:
    nearestNode = NodesTree.query(query_point=(i), t = 1)
    attractionHelperIndex = attractionPointsHelper.index(i)
    currentNodeIndex = treeNodesHelper.index(nearestNode[0])
    #print "Candidate: " + str((i[0], i[1], i[2])) + " ASSOC WITH*: " + str(nearestNode[0]) +"\n " +  "\nIndex*:" +str(currentNodeIndex) + " "+ str(treeNodes[currentNodeIndex].position)
    treeNodes[currentNodeIndex].attractionCandidates.append(attractionPoints[attractionHelperIndex])



#print "== nodes processing ============================ " + str(counter) +"\n"
nodesCounter = 0
numNodes = len(treeNodes)
#print "length of nodes: " + str(numNodes)
for i in treeNodes:
    if nodesCounter <= numNodes: #prevent overcounting
        #nodesCounter += 1
        if i.calculateAverageDir() != -1: #maybe do it on the fly?
            #print "====== next Node " + str(i.getPosition()) +" ===== \n"
            nextNodesPosition = i.createNextNode()
            nextAveragePos = hou.Vector3(nextNodesPosition[0] +i.getPosition()[0] , nextNodesPosition[1] +i.getPosition()[1], nextNodesPosition[2] +i.getPosition()[2])
            nextNode = treeNode(nextAveragePos)
            treeNodes.append(nextNode)
            
            i.resetAll()
        #else:
        #   print "this node has no candidates " + str(i.getPosition())

    nodesCounter += 1

#treeNodes.extend(helperList)
counter += 1

#Kill Attraction Points to close to Nodes
geo.deletePoints(attractionPointsKill)


#Create Nodes 
for i in treeNodes:
    tmp = geo.createPoint()
    tmp.setAttribValue("P", i.position)
    tmp.setAttribValue("Cd", hou.Vector3(0.0, 1.0, 0.0))

#Special Thanks to Niko Wuttke