from numpy.lib.type_check import imag
from commonfunctions import show_images
import cv2 as cv
import numpy as np
import imutils
from matplotlib import pyplot as plt
from utils import ptile
from skimage.filters import threshold_local
import utils
import functools
import easyocr
import argparse
import json

#cv.imshow = lambda comment, image: None
#cv.waitKey = lambda key: None

file = open('outputs','w')
reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory

def get_y_dim(stripped_image):
    j = stripped_image.shape[1] // 2
    flips = [0]
    diff, lower, upper = -1, -1, -1
    prv_clr = stripped_image[0][j]
    for i in range(stripped_image.shape[0]):
        if prv_clr != stripped_image[i][j]:
            prv_clr = stripped_image[i][j]
            flips.append(i)
            if flips[-1] - flips[-2] > diff:
                diff  = flips[-1] - flips[-2]
                upper = flips[-2]
                lower = flips[-1]

    return (upper, lower)


def biggestContour(contours, maxArea):
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv.contourArea(i)
        # to avoid small contours (noise)
        if area > maxArea:
            peri = cv.arcLength(i, True)
            approx = cv.approxPolyDP(i, 0.02 * peri, True)
            # check if this rectangle
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest, max_area


def drawRectangle(img, biggest, thickness):
    cv.line(img, (biggest[0][0][0], biggest[0][0][1]),
            (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
    cv.line(img, (biggest[0][0][0], biggest[0][0][1]),
            (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv.line(img, (biggest[3][0][0], biggest[3][0][1]),
            (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv.line(img, (biggest[3][0][0], biggest[3][0][1]),
            (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)

    return img


def reorder(myPoints):

    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)
    add = myPoints.sum(1)

    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] = myPoints[np.argmax(add)]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] = myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]

    return myPointsNew

def sort_contours(cnts, method="top-to-bottom"):
	# initialize the reverse flag and sort index
	reverse = False
	i = 0
	# handle if we need to sort in reverse
	if method == "right-to-left" or method == "bottom-to-top":
		reverse = True
	# handle if we are sorting against the y-coordinate rather than
	# the x-coordinate of the bounding box
	if method == "top-to-bottom" or method == "bottom-to-top":
		i = 1
	# construct the list of bounding boxes and sort them from top to
	# bottom
	boundingBoxes = [cv.boundingRect(c) for c in cnts]
	(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
		key=lambda b:b[1][i], reverse=reverse))
	# return the list of sorted contours and bounding boxes
	return (cnts, boundingBoxes)


def getId (idImageBinary,idImage):
    id = ''
    cnts,hei = cv.findContours(idImageBinary, cv.RETR_EXTERNAL,	cv.CHAIN_APPROX_SIMPLE)
    cnts = sort_contours(cnts, method="left-to-right")[0]
    ## name , id
    letters = []
    print('cnts : ',len(cnts))
    for c in cnts:
        (x, y, w, h) = cv.boundingRect(c)
        asceptRatio = w / float(h)
        #cv.rectangle(idImage,(x,y),(x+w,y+h),(0,255,0),1)
        character = idImage[y:y+h,x:x+w]
        #entities.append(rect) 
        blank = character
        w,h = w+max(h,w),h+max(h,w)
        blank = np.pad(blank,((h,h), (w,w), (0,0)),constant_values=np.max(character))
        ratio = 10
        print(h,w)
        #cv.imshow("blank",cv.resize(blank,(ratio*w,ratio*h)) )
        #cv.waitKey(0)
      
        result = reader.readtext(cv.resize(blank,(ratio*w,ratio*h)),detail=0)
        print(result)
        if  result :
            if result[0].isnumeric():
                id += result[0]
    return id

def getName (nameBinary,name):
    #cv.imshow("nameBinary",nameBinary )
    #cv.waitKey(0)    
    result = reader.readtext(name,detail=0)
    return result[0]

def getAnswers (question):
    chosenAnswer = max(question)

def removeNumberLine(image,imageTh):
    SE = np.ones((100,5))
    # dilation
    numberDilation = cv.dilate(th4, SE, iterations=1)

    cnts,hei = cv.findContours(numberDilation, cv.RETR_EXTERNAL,
	cv.CHAIN_APPROX_SIMPLE)

    cnts = sort_contours(cnts, method="left-to-right")[0]
    sripts = []
    for c in cnts:
        (x, y, w, h) = cv.boundingRect(c)
        if h >= image.shape[0] // 2: 
            sripts.append(c)
            #rect = cv.rectangle(image11,(x,y),(x+w,y+h),(0,255,0),1)
            #cv.imshow('rects',rect)
            #cv.waitKey(0)
    (x, y, w, h) =  cv.boundingRect(sripts[0])
    cv.imshow('8araboly',imageTh[:,x+w:])
    cv.waitKey(0)
    return imageTh[:,x+w:],image[:,x+w:]
 ######################### start program #######################


def checkAnswers(row):
    max_ = max(row)
    
output = {}

images = ["imgs/9.jpeg","imgs/10.jpeg","imgs/11.jpg","imgs/12.jpeg","imgs/13.jpeg","imgs/14.jpeg","imgs/15.jpeg"]
## take image
image = cv.imread(images[-2])
orignalImage = image.copy()
orignalImage[orignalImage.shape[0]-1,:]=0
orignalImage[0,:]=0
orignalImage[:,orignalImage.shape[1]-1]=0
orignalImage[:,0]=0

## no need for resize
# orignalImage = cv.resize(image,(800,800)) #resizing because opencv does not work well with bigger images

# get width and height
heigh = orignalImage.shape[0]
width = orignalImage.shape[1]

# convert image into grey scale
grayImage = cv.cvtColor(orignalImage, cv.COLOR_BGR2GRAY)

# get histogram
dst = cv.calcHist(grayImage, [0], None, [256], [0, 256])
plt.hist(grayImage.ravel(), 256, [0, 256])
plt.title('Histogram for gray scale image')
plt.show()

# make gaussian blur
blur = cv.GaussianBlur(grayImage, (5, 5), 0)
ret3, th3 = cv.threshold(blur, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
print(ret3)
cv.imshow('thresh', th3)
cv.waitKey(0)

"""
# structure element
SE =np.ones((5,5),np.uint8)
# opening
openingImage = cv.morphologyEx(blur, cv.MORPH_OPEN, SE)
# followed by closing with same SE
closingImage = cv.morphologyEx(blur, cv.MORPH_CLOSE, SE)
"""

# m7tagen n7dd el threshold @zizo
med_val = np.median(blur)
lower = int(max(0, 0.7*med_val))
upper = int(min(255, 1.3*med_val))
edged = cv.Canny(blur, lower, upper)
cv.imshow("Outline", edged)
cv.waitKey(0)

## msh 3arf lsa btboz leh??
# structure element
# SE = np.ones((5,5))
# Dilation = cv.dilate(edged,SE,iterations = 2)
# erosion = cv.erode(edged,SE,iterations = 1)


"""
save all found contours in contours
"""
contours, hirerarchy = cv.findContours(
    edged.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
## the paper is the biggest contour in image
biggest, maxArea = biggestContour(contours, width*heigh//5)

# biggest are 4 points of our biggest contour
print(biggest)
if biggest.size != 0:
    # reorder these 4 points
    
    biggest = reorder(biggest)
    cv.drawContours(image, biggest, -1, (0, 255, 0), 20)
    imgBigContour = drawRectangle(image, biggest, 2)
    cv.imshow("Big Contours", cv.resize(image, (600, 800)))
    cv.waitKey(0)


    # reorder sort points according to our annotations
    # extract exampaper from  image (warpPerspective)
    pts1 = np.float32(biggest)
    pts2 = np.float32([[0, 0], [width, 0], [0, heigh], [width, heigh]])
    paperView = cv.getPerspectiveTransform(pts1, pts2)
    wrap = cv.warpPerspective(orignalImage, paperView, (width, heigh))
    cv.imshow("final", cv.resize(wrap, (600, 800)))
    cv.waitKey(0)
    cv.destroyAllWindows()
else:
    cnts = sorted(contours, key=cv.contourArea, reverse=True)[:1]
    (x, y, w, h) = cv.boundingRect(cnts[0])
    print('area : ',w*h)
    test = cv.rectangle(orignalImage,(x,y),(x+w,y+h),(0,255,0),1)
    cv.imshow('a',test)
    cv.waitKey(0)
# if their is no biggest contour (contour with large size)
#   then the image is already the exam paper so take the greyImage
if biggest != []:
    examPaper = wrap
    examPaper = cv.cvtColor(examPaper, cv.COLOR_BGR2GRAY)
else:
    examPaper = grayImage


## histogram of the examPaper itself
cv.imshow("bubble group", cv.resize(examPaper, (600, 800)))
cv.waitKey(0)
cv.destroyAllWindows()
plt.hist(examPaper.ravel(), 256, [0, 256])
plt.title('Histogram for gray scale image')
plt.show()


"""
####   hsv thresholding   (tare2a 7lwa mmkn nst5dmha)
imgHsv = cv.cvtColor(examPaper, cv.COLOR_BGR2HSV)

# Define lower/upper color
lower = np.array([0, 0, 180])
upper = np.array([180, 20, 255])

# Check the region of the image actually with a color in the range defined below
# inRange returns a matrix in black and white
bw = cv.inRange(imgHsv, lower, upper)
print(bw)
"""


#TODO: 3ayzen nzbt el thresholding
ret, thresh1 = cv.threshold(examPaper, 100, 255, cv.THRESH_BINARY_INV)
#th = utils.ptile(examPaper, 100-85)
#thresh1 = np.where(examPaper > th, 255, 0)
# show_images([thresh1])
cv.imshow("threshold", thresh1)
cv.waitKey(0)
cv.destroyAllWindows()




# contours, hirerarchy = cv.findContours(
#     dilation.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

#TODO: for 2nd model  (bta3 mostafa gendy nzwd showyt hyperParameter)
# SE = np.ones((25, 25))
# # dilation
# thresh1 = cv.dilate(thresh1, SE, iterations=1)
# cv.imshow("dilation", thresh1)
# cv.waitKey(0)

## sripts dilation 
SE = np.ones((5, width))
sriptedImage = cv.dilate(thresh1, SE, iterations=1)
cv.imshow("stripted", sriptedImage)
cv.waitKey(0)
cv.destroyAllWindows()

## get the sripts and (biggest sripts is the bubbles group)
upper, lower = get_y_dim(sriptedImage)
headerBinary = thresh1[:upper,:]
header = orignalImage[:upper,:]
thresh1 = thresh1[upper:lower, :]
striptedImage = orignalImage[upper:lower, :]
cv.imshow("stripted", thresh1)
cv.waitKey(0)

cv.imshow("idImage", header)
cv.waitKey(0)
cv.destroyAllWindows()

######################  get id ##################################
cnts,hei = cv.findContours(headerBinary, cv.RETR_EXTERNAL,
	cv.CHAIN_APPROX_SIMPLE)

cnts = sorted(cnts, key=cv.contourArea, reverse=True)[:2]
cnts = sort_contours(cnts, method="left-to-right")[0]

## assume that name is allows at the left of the id
print(cnts)
## name , id
entities = []
for c in cnts:
    (x, y, w, h) = cv.boundingRect(c)
    asceptRatio = w / float(h)
    cv.rectangle(header,(x,y),(x+w,y+h),(0,255,0),1)
    #rectBinary = headerBinary[y:y+h,x:x+w]
    f=5
    rectBinary = headerBinary[min(y+f,headerBinary.shape[0]):min(y+h-f,headerBinary.shape[0]),max(x+f,0):max(x+w-f,0)]
    # rect =  header[y:y+h,x:x+w]
    rect =  header[min(y+f,headerBinary.shape[0]):min(y+h-f,headerBinary.shape[0]),max(x+f,0):max(x+w-f,0)]
    entities.append((rectBinary,rect)) 
    cv.imshow("Bigs", rect)
    cv.waitKey(0)
    cv.destroyAllWindows()

nameBinary = entities[0][0]
name = entities[0][1]
idBinary = entities[1][0]
id = entities[1][1]

id = getId(idBinary,id)
name = getName(nameBinary,name)

print('student name : ',name)
print('student id = ',id)
output['name'] = name
output['id'] = id

#print(idBinary.shape)


########################################################






## dilate the bubbles to make each group as contour
SE = np.ones((20, 20))
# dilation
dilation = cv.dilate(thresh1, SE, iterations=1)
cv.imshow("dilation", dilation)
cv.waitKey(0)
cv.destroyAllWindows()

## get contours of each bubbles group
contours, hirerarchy = cv.findContours(
    dilation.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

# sort contours by area
contours = sorted(contours, key=cv.contourArea, reverse=True)

BubblesGroup = []

for con in contours:
    # approximate the contour
    peri = cv.arcLength(con, True)
    if cv.contourArea(con) < (striptedImage.shape[0]*striptedImage.shape[1]) // 10:
        break
    approx = cv.approxPolyDP(con, 0.02 * peri, True)
    # if our approximated contour has four points, then we
    # can assume that we have found our screen
    if len(approx) == 4:
        BubblesGroup.append(approx)

BubblesGroup = sort_contours(BubblesGroup, method="left-to-right")[0]
print(len(BubblesGroup))
wraps = []
iteration = 1
for subBubbles in BubblesGroup:

    subBubbles = reorder(subBubbles)
    #cv.drawContours(striptedImage, subBubbles, -1, (0, 255, 0), 20)
    #imgBigContour = drawRectangle(striptedImage, subBubbles, 2)
    #cv.imshow("Big Contours", cv.resize(striptedImage, (600, 800)))
    #cv.imshow()
    #cv.waitKey(0)
    pts1 = np.float32(subBubbles)
    pts2 = np.float32([[0, 0], [width, 0], [0, heigh], [width, heigh]])
    paperView = cv.getPerspectiveTransform(pts1, pts2)
    wrap = cv.warpPerspective(striptedImage, paperView, (width, heigh))
    wraps.append(wrap)
    cv.imshow("final", wrap)
    cv.waitKey(0)
    cv.destroyAllWindows()

    # تصحيييييح
    wrapGrey =cv.cvtColor( wrap , cv.COLOR_BGR2GRAY)
    ret4, th4 = cv.threshold(wrapGrey, 0, 255, cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
    # find contours in the thresholded image, then initialize
    # the list of contours that correspond to questions
    cv.imshow("number line th4", th4)
    cv.waitKey(0)
    ##########################################
    
    #cv.imshow("number line dilation", numberDilation)
    #cv.waitKey(0)
    imageTh,wrap = removeNumberLine(wrap,th4)
    wrapGrey =cv.cvtColor( wrap , cv.COLOR_BGR2GRAY)
    #cv.imshow("number line dilation1", numberDilation)
    #cv.waitKey(0)
    ##########################################

    ## get the bubbles
    cnts = cv.findContours(imageTh.copy(), cv.RETR_EXTERNAL,
        cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    print(len(cnts))
    questionCnts = []
    # loop over the contours
    # cv.imshow("Big",wrapGrey)
    # cv.waitKey(0)
    
    for bubble in cnts:
        # compute the bounding box of the contour, then use the
        # bounding box to derive the aspect ratio
        (x, y, w, h) = cv.boundingRect(bubble)
        asceptRatio = w / float(h)
        # in order to label the contour as a question, region
        # should be sufficiently wide, sufficiently tall, and
        # have an aspect ratio approximately equal to 1
        print(w, h, asceptRatio)
        ## only get the small bubbles 
        if w >= 10 and w<=50 and h >= 10 and h <= 50  :
                # cv.drawContours(wrap[0], [c], -1, (0, 255, 0), 20)
                # imgBigContour = drawRectangle(wrap[0], c, 2)
                # cv.imshow("Big Contours",wrap[0])
                # cv.waitKey(0)
                #image = cv.rectangle(wraps[0],(x +w//2,y+h//2),(w,h),(0,255,0),2)
                questionCnts.append(bubble)
                # draw bubbles contour
                image = cv.drawContours(wrap, bubble, -1, (0, 255, 0), 3)
                #cv.imshow("Get bubbles",image)
                #cv.waitKey(0)

    #print(questionCnts)
    cv.imshow("Get bubbles",image)
    cv.waitKey(0)



    ## sort contours from tom to bottom
    questionCnts = sort_contours(questionCnts, method="top-to-bottom")[0]

    correctAnwers = 0
    chooses = ['A','B','C','D','E']

    thresh = cv.threshold(wrapGrey, 0, 255,
        cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]
    # each question has 5 possible answers, to loop over the
    # question in batches of 5
    
    for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):

        # bubbled answer
            # sort each row form left to right 
            cnts = sort_contours(questionCnts[i:i + 5],method="left-to-right")[0]
            bubbled = None
            # loop over the sorted contours
            row = []
            for (j, bubble) in enumerate(cnts):
                        #print(' : ' , bubble)
                    
                # construct a mask that reveals only the current
                # "bubble" for the question
                        mask = np.zeros(thresh.shape, dtype="uint8")
                        cv.drawContours(mask, [bubble], -1, 255, -1)
                        # apply the mask to the thresholded image, then
                        # count the number of non-zero pixels in the
                        # bubble area
                        mask = cv.bitwise_and(thresh, thresh, mask=mask)
                        (x, y, w, h) = cv.boundingRect(bubble)
                        print('x: ',x,'y : ',y,'w :',w,'h :',h)
                        #rect = cv.rectangle(mask,(x,y),(x+w,y+h),255,2)
                        cv.imshow("Get bubbles",mask)
                        cv.waitKey(0)
                        ## factor
                        f = 5
                        rect = mask[max(y-f,0):min(y+h+f,mask.shape[0]),max(x-f,0):min(x+w+f,mask.shape[1])]
                        cv.imshow("Get rect",rect)
                        cv.waitKey(0)
                        number_of_white_pix = np.sum(rect == 255)
                        percentage = (number_of_white_pix /(rect.shape[0]*rect.shape[1])) * 100
                        row.append(percentage)

                        # total = cv.countNonZero(mask)
                        # #print(total)
                        # if bubbled is None or total > bubbled[0]:
                        #     bubbled = (total, j)
                        #     print(bubbled)

            print('row = ',row)
            ##TODO: test bs
            answers=[] 
            
            checkAnswers(row)

            for (k, r) in enumerate(row):
                if r > 30.0:
                    answers.append(k)

            # only one chosen answer
            if len(answers) == 1:
                #result += '{} : {} , '.format(iteration,chooses[answers[0]])
                output['q'+str(iteration)] = chooses[answers[0]]
            else:
                #result += '{} : {} , '.format(iteration,'no answer')
                output['q'+str(iteration)] = 'no answer'
            
            iteration += 1
        
file.write(json.dumps(output))




    # for con in contours:
    #     # approximate the contour
    #     peri = cv.arcLength(con, True)
    #     if cv.contourArea(con) < (striptedImage.shape[0]*striptedImage.shape[1]) // 10:
    #         break
    #     approx = cv.approxPolyDP(con, 0.02 * peri, True)
    #     # if our approximated contour has four points, then we
    #     # can assume that we have found our screen
    #     if len(approx) == 4:
    #         BubblesGroup.append(approx)


file.close()

