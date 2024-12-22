import statistics as s
import sys
import random
import os

# read event file
def read_event_file(filename):
	line = []

	with open(filename, "r") as e_line:
		lines = e_line.readlines()

		for part in lines:
			line.append(part.strip())
	
	return line
	
# read stats file
def read_stats_file(filename):
	line = []

	with open(filename, "r") as s_line:
		lines = s_line.readlines()

		for part in lines:
			line.append(part.strip())
	
	return line
    

# check for inconsistencies between Events and Stats file
def check_file_inconsistency(eventData, statsData):
	noOfEventData = int(eventData[0])
	noOfStatsData = int(statsData[0])
	
	# different number of data
	if noOfEventData != noOfStatsData:
		print("Number of data is inconsistent")
		return False
		
	# loop through array of data and check the consistency between part event
	for i in range(1, noOfEventData):
		# different event
		if eventData[i].split(":")[0] != statsData[i].split(":")[0]:
			print(f"Inconsistencies found in line {i + 1}")
			return False
	
	print("No inconsistencies found")
	return True


# process Event file
def processEvents(data):
	noOfEvents = int(data[0]) # number of events on the first line
	weights = []
	
	for i in range(1, noOfEvents + 1):
		part = data[i].split(":")
		
		# capture part property
		eventName = part[0]
		eventType = part[1]	
		minimum = part[2]
		maximum = part[3]
		weight = part[4]
	
		# validations
		# neither Continuous or Discrete
		if eventType != "C" and eventType != "D":
			print("Event type must be either C or D")
			return
		
		# minimum value
		if minimum == "": # value empty
			print("Minimum values cannot be empty")
			return
	
		# weight value
		if weight.find(".") > 0: # float value found in weight variable
			print("Weight values must be an integer")
			return
	
		if weight == "": # value empty
			print("Weight values cannot be empty")
			
        # maximum value
		if maximum == "":  # Value empty
			maximum = str(random.randint(1, 999))  
	
		# in the case of Discrete events
		if eventType == "D":
			# float values found in minimum or maximum variable
			if minimum.find(".") > 0 or maximum.find(".") > 0:
				print("Float found in a Discrete Event")
				return
		
		# in the case of Continuous events
		if eventType == "C":
			minimum = "{:.2f}".format(float(minimum)) # 2 decimal places
			maximum = "{:.2f}".format(float(maximum)) # 2 decimal places
				
		# sum of weight
		weights.append(int(weight))
		
		print(f"Event:{eventName:<15} Type:{eventType:<15} Min:{minimum:<15} Max:{maximum:<15} Weight:{weight}")
	return weights

# process Stats file
def processStats(data):
	noOfEvents = int(data[0]) # number of events on the first line
	
	for i in range(1, noOfEvents + 1):
		part = data[i].split(":")
		
		# capture part property
		eventName = part[0]
		mean = part[1]
		standard_deviation = part[2]
		print(f"Event:{eventName:<16} Mean:{mean:<15} Standard Deviation:{standard_deviation}")
		
def readLogs(filename):
	print("------------------------")
	print(f"Commencing analysis for {filename}")

	data = []
	eventName = []
	
	# get event names
	with open(filename, "r") as file:
		file.readline().strip() # day number
		noOfEvents = int(file.readline().strip()) # number of events
		
		for i in range(noOfEvents):
			eventName.append(file.readline().strip().split(":")[0])
	

	with open(filename, "r") as file:	
		# total lines per day in logs #
		# first line - Day number
		# second line - number of events
		# inbetween = number of events
		# last line - \n
		# total number of lines per day = 3 + number of events
		
		file.readline().strip()
		noOfEvents = int(file.readline().strip()) # number of events logged

		count = 0 # track number of events processed
		
		# loop through the file for as many times as the number of events logged per day
		while count < noOfEvents:
			dailyData = []
			while True:
				line = file.readline().strip()
				
				if not line: # EOF rparted
					data.append(dailyData) # add daily data to list
					count += 1 # increment count
					file.seek(0) # move cursor to the top of the file
				

					
					# skip the irrelevant lines
					for i in range(2 + count):
						file.readline().strip()
					
					break # break out of the inner while loop

				# split()
				lineInfo = line.split(":")
				
				# event type
				if lineInfo[1] == "D": # discrete events - integer
					dailyData.append(int(lineInfo[2])) # add daily data
				if lineInfo[1] == "C": # continuous events - 2 d.p.
					dailyData.append(round(float(lineInfo[2]), 2))
				
				
				# skip the remaining information
				for i in range(noOfEvents + 2):
					file.readline().strip()
		print(f"<<{count} unique events processed>>")
		print("------------------------")
					
	return data, eventName

def generateData(mean, standardDeviation, days, minimum, maximum, eventType):
    while True:
        n = s.NormalDist(mean,standardDeviation)
        samples = n.samples(days)
        
        # Keep values within min/max bounds
        for index in range(len(samples)):
            if eventType == "D":  # Discrete event
                samples[index] = round(samples[index])  # Round value to integer
            elif eventType == "C":  # Continuous event
                samples[index] = round(samples[index], 2)  # Round value to 2 decimal places
                
            # Check for out-of-bounds values
            if samples[index] < minimum or samples[index] > maximum:
                continue

        # Use a consistent tolerance for mean and standard deviation checks
        tolerance = 0.05  # 5% tolerance

        # Check if the generated data matches the desired mean and standard deviation
        if (mean * (1 - tolerance) <= s.mean(samples) <= mean * (1 + tolerance) and
            standardDeviation * (1 - tolerance) <= s.stdev(samples) <= standardDeviation * (1 + tolerance)):
            return samples  # Return the generated sample data



# generate data set for part event
def generateDataSet(days, eventData, statsData):

	# get the number of events
	noOfEvents = int(eventData[0])
	
	# track the set of data to be used to simulate activity for the baseline
	activityData = []
	
	for i in range(days):
		for j in range(1, noOfEvents + 1):
			# split event data
			eData = eventData[j].split(":")
			eventName = eData[0] # name of event		
			eventType = eData[1] # type of event
			minimum = int(eData[2]) # min of event
			if eData[3] == "":
				maximum = random.randint(1,sys.maxsize)  # Generate random max value
			else:
				maximum = int(eData[3])  # max of event
		
			# split stats data
			sData = statsData[j].split(":")
			mean = float(sData[1]) # mean
			standardDeviation = float(sData[2]) # standard deviation
			
			# generate set of data as close to mean and stdev
			dataSet = generateData(mean, standardDeviation, days, minimum, maximum, eventType)
			activityData.append(dataSet) # add
			
		
	print(f"<<Data set generation for {days} days completed!>>")
	return activityData



# write statistics to file
def outputData(data, eventName, filename):
	# get mean
	mean = calculateMean(data)
	
	# get variance
	variance = calculateVariance(data, mean)
	
	# get standard deviation
	stddev = calculateStddev(variance)
			
	# write to file
	with open(filename, "a") as file:
		file.write(str(len(eventName)))
		for i in range(len(eventName)): # number of events
			file.write(f"\n{eventName[i]}:{str(mean[i])}:{str(stddev[i])}")
			
	return mean, stddev

def simulateActivity(filename, days, eventData, dataSet):
	print(f"Simulating activity with the data set generated")

	noOfEvents = int(eventData[0])
	
	file = open(filename, "a")

	for i in range(days):
		file.write(f"Day {i + 1}\n")
		file.write(f"{noOfEvents}\n")
		
		for j in range(noOfEvents):
			# deconstruct eventData
			data = eventData[j + 1].split(":")
			eventName = data[0]
			eventType = data[1]
			
			file.write(f"{eventName}:{eventType}:{dataSet[j][i]}:\n")
		
		file.write("\n")
		
	file.close()
	

	print(f"<<{days} days of data has been written to {filename}!>>")
	
		
# calculate mean
def calculateMean(data):
	mean = []
	
	# process data obtained from the logs file - MEAN
	for index, value in enumerate(data): # number of events
		sum = 0
		for i, v in enumerate(value): # number of days
			sum += v
			
			if i + 1 == len(value): # rparted the last day
				# calculate mean - maintain at 2dp if exceeded
				mean.append(round(sum / (i + 1), 2))

	return mean

# calculate variance
def calculateVariance(data, mean):
	variance = []

	# process data obtained from the logs file - VARIANCE
	for index, value in enumerate(data): # number of events
		sum = 0
		for i, v in enumerate(value): # number of days
			sum += (v - mean[index]) ** 2
			
			if i + 1 == len(value): # rparted the last day
				# calculate variance - maintain at 2dp if exceeded
				variance.append(round(sum / (i + 1), 2))

	return variance
	
# calculate standard deviation
def calculateStddev(variance):
	stddev = []
	
	# calculate the standard deviation based on the variance
	for index, value in enumerate(variance):
		stddev.append(round(value ** 0.5, 2)) # square root variance
	
	return stddev

	
# get threshold
def getThreshold(weights):
	sum = 0
	for i in range(len(weights)):
		sum += weights[i]
		
	return 2 * sum
	
# read new log file
def readNewLogs(filename):
	print(f"Commencing analysis for {filename}\n")

	dailyData = [] # track all the data for part day
	
	# get event names
	with open(filename, "r") as file:
		while True:
			line = file.readline().strip() # day number
			
			if not line: # EOF rparted
				break
				
			daily = [] # track daily data

			noOfEvents = int(file.readline().strip()) # number of events
		
			for i in range(noOfEvents): # go through part event for a day
				daily.append(file.readline().strip().split(":")[2])
			
			dailyData.append(daily) # add to 2d list to track daily data
			file.readline().strip() # new line
					
	return dailyData
	
# for part event:
# 	[total - mean(from Baseline.txt)] / stddev(from Baseline.txt) * weight(from Events.txt)
def anomalyCounter(filename, weight, mean, stddev):
	print("Currently calculating daily totals")
    
	# read new logs file and capture its data
	data = readNewLogs(filename)
	
	# track the daily totals
	dailyCounter = []
	
	for index, value in enumerate(data): # loop through the number of days
		counter = 0 # track counter for daily events
		for i, v in enumerate(value): # loop through the number of events
			counter += float(round(((abs((float(v) - mean[i])) / stddev[i]) * weight[i]), 2))
		
		dailyCounter.append(counter)
	
	print("Daily totals calculated!\n")
	return dailyCounter


# check for anomaly
def flagging(data, threshold):
	print("Currently checking for anomalies\n")

	flagged = []
	
	for i in range(len(data)):
		alert = False
		if data[i] > threshold:
			flagged.append(i + 1) # day number
			alert = True
		
		print(f"Day {i + 1} anomaly count = {round(data[i], 2)} {'<<ALERT>>' if alert == True else ''}")

	print("\n")
			
	# alert
	if len(flagged) != 0:
		print("ALERT! Anomalies detected!")
		print("--------------------------")
		for index, value in enumerate(flagged):
			print(f"Day {value} has been flagged!")
		print("\n")
	else:
		print("No anomalies detected\n")
	
			
	return flagged


	

def displayGeneratedData(eventData, dataSet):
    print("\nGenerated Data:")
    noOfEvents = int(eventData[0])
    
    # Display the generated data for part event
    for i in range(noOfEvents):
        eventName = eventData[i + 1].split(":")[0]
        print(f"{eventName}: {dataSet[i]}")

    print("\nDaily Totals:")
    # Calculate and display daily totals
    for day in range(len(dataSet[0])):
        daily_total = sum(dataSet[event][day] for event in range(noOfEvents))
        print(f"Day {day + 1}: {daily_total}")

def displayGeneratedData(eventData, dataSet):
    print("\nGenerated Data:")
    noOfEvents = int(eventData[0])
    
    # Display the generated data for part event
    for i in range(noOfEvents):
        eventName = eventData[i + 1].split(":")[0]
        print(f"{eventName}: {dataSet[i]}")

    print("\nDaily Totals:")
    # Calculate and display daily totals
    for day in range(len(dataSet[0])):
        daily_total = sum(dataSet[event][day] for event in range(noOfEvents))
        print(f"Day {day + 1}: {daily_total:.2f}")
		
def generateNewLogFileName(baseName="logs", extension=".txt"):
    logCount = 1
    while os.path.exists(f"{baseName}{logCount}{extension}"):
        logCount += 1
    return f"{baseName}{logCount}{extension}", logCount



def main():
    if len(sys.argv) != 4:
        print("Usage: python3 IDS.py <event_file_name> <stats_file_name> <days>")
        sys.exit(1)
    
    eventFile = sys.argv[1]  # Event file name from command line arguments
    statsFile = sys.argv[2]  # Stats file name from command line arguments
    days = int(sys.argv[3])  # Number of days from command line arguments
    
    # Read event and stats data
    eventData = read_event_file(eventFile)
    statsData = read_stats_file(statsFile)
    newLogsFile, logCount = generateNewLogFileName()
    print("--------------------------------------------------------------------")
    print(f"Checking for inconsistencies between {eventFile} and {statsFile}...")
    print("--------------------------------------------------------------------")
    
    # Check for consistency between event and stats data
    if not check_file_inconsistency(eventData, statsData):
        print("Inconsistencies found. Exiting program.")
        sys.exit(1)  # Stop program if inconsistencies are found
    
    print("------------------------")
    print(f"<<{eventFile}>>")
    weights = processEvents(eventData)
	

    print("\n")
    print(f"<<{statsFile}>>")
    processStats(statsData)


    print("------------------------")
    # generate data set for part event for part day
    dataSet = generateDataSet(days, eventData, statsData)
    displayGeneratedData(eventData, dataSet)  # Call the display function

    print("------------------------")
    # simulate activity and write to logs file
    simulateActivity(newLogsFile, days, eventData, dataSet)


    # get data from logs file
    data, eventName = readLogs(newLogsFile)
	

    # write result of analysis to text file - BASELINE
    mean, stddev = outputData(data, eventName, "Baseline_Statistics.txt")


    logCount = 1
    while True:
        
        # get new stats file and number of days
        newStatsFile = input("\nEnter the new Stats.txt file (or 'q' to quit): ").strip()
        if newStatsFile.lower() == "q":
            print("Exiting the system. Goodbye!")
            break  
        
        newDays = int(input("Enter the number of days for the new stats file: ").strip())
        # read new stats file
		
        print("------------------------")
        newStatsData = read_stats_file(newStatsFile)

        # generate data set for part event for part day
        newDataSet = generateDataSet(newDays, eventData, newStatsData)

        # new logs file
        newLogsFile = f"logs{logCount+1}.txt"
        logCount += 1
        print("------------------------")
        # simulate activity and write to new logs file
        simulateActivity(newLogsFile, newDays, eventData, newDataSet)
        print("------------------------")
        # get threshold
        threshold = getThreshold(weights)
        
        # anomaly counter
        dailyAnomalyCounter = anomalyCounter(newLogsFile, weights, mean, stddev)
        
        # check for anomaly
        print(f"\nThreshold: {threshold}")
        flagging(dailyAnomalyCounter, threshold)
	
if __name__ == "__main__":
	main()