from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import smtplib
from email.mime.text import MIMEText
from subprocess import *

#####
# Author: Mike Adler - May 3, 2013
#
# GOESInterviewChecker - Used to automate checking of GOES interview times.
#
# This program will log in to your GOES account with the set values below,
# and will read both your current booked interview, and the earliest
# date at your preferred enrollment center. 
# If an earlier date is found, an email message will be sent alerting you
# that an earlier date has been found.
#
# NOTE: If you have no current booking, or wish to specify a date to use
#       for comparison, please set the  compareToDate  value below. Otherwise
#       your current booking date will be found and used for comparison.
#####

class GOESInterviewChecker(unittest.TestCase):
	
	# GOES Account Info
	# Set these values
	# Note: Preferred enrollment center value is the text value in the enrollment center dropdown menu
	GOES_USERNAME = ""
	GOES_PASSWORD = ""
	GOES_BASE_URL = "https://goes-app.cbp.dhs.gov/" 

	#GOES_PREFERRED_ENROLLMENT_CENTER = "Blaine Enrollment Center - 9901 Pacific Highway, BLAINE, WA 98230, US"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Buffalo-Ft. Erie Enrollment Center - 10 CENTRAL AVENUE, FORT ERIE, ON L2A1G6, CA"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Calais Enrollment Center - 3 Customs Street, Calais, ME 04619, US"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Calgary Enrollment Center - 2000 Airport Rd N.E., Calgary, AB T2E6W5, CA"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Champlain Enrollment Center - 237 West Service Road, Champlain , NY 12919, US"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Detroit Enrollment Center - 2810 West Fort Street, Building B, Detroit, MI 48226, US"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Edmonton Enrollment Center - Edmonton International Airport-Nexus, Edmonton International Airport, Edmonton, AB T5J2T2, CA"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Fort Frances Enrollment Center - 301 Scott Street, Fort Frances, ON P9A1H1, CA"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Halifax Enrollment Center - CBSA Canada Customs , 1 Bell Boulevard Comp 1666 Halifax Intl Airport, Enfield, NS B2T1K2, CA"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Houlton Enrollment Center - 1403 Route 95, Belleville, NB E7M4Z9, CA"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Lansdowne, ON - 664 Highway 137, Hill Island, Lansdowne, ON K0E1L0, CA"
	GOES_PREFERRED_ENROLLMENT_CENTER = "Montreal Enrollment Center - 1 Pierre E Trudeau International Airport , 975 Blvd Romeo Vachon. Room T1470, Montreal, QC H2Y1H1, CA"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Niagara Falls Enrollment Center - 2250 WHIRLPOOL ST., NIAGARA FALLS, NY 14305, US"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Ottawa Enrollment Center - 1000 Airport Parkway Private, Suite 2641, Ottawa, ON K1V9B4, CA"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Ottawa Enrollment Center A - 1000 Airport Parkway Private, Ottawa, ON, CA"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Pembina Enrollment Center - 10980 Interstate 29 N, Suite 2, Pembina, ND 58271, US"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Port Huron Enrollment Center - 2321 NEXUS Enrollment Center, Pine Grove Ave., Port Huron, MI 48060, US"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Sault Ste Marie Enrollment Center - 900 International Bridge Plaza, Sault Ste. Marie, MI 49783, US"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Seattle Urban Enrollment Center - 7277 PERIMETER ROAD SOUTH RM 116, KING COUNTY INTERNATIONAL AIRPORT, BOEING FIELD, SEATTLE, WA 98108, US"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Sweetgrass Enrollment Center - 39825 FAST Enrollment Center, 39825 Interstate 15 North, Sweetgrass, MT 59484, US"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Toronto Enrollment Center - Pearson International Airport, Terminal 1, Toronto, ON L5P1A2, CA"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Vancouver Enrollment Center - 3211 Grant McConachie Way, Vancouver International Airport, Richmond, BC V7B1Y9, CA"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Vancouver Urban Enrollment Center - 333 DUNSMUIR, VANCOUVER, BC V7P3P3, CA"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Warroad Enrollment Center - 41059 Warroad Enrollment Center, State Hwy 313 N, Warroad, MN 56763, US"
	#GOES_PREFERRED_ENROLLMENT_CENTER = "Winnipeg Enrollment Center - 1970 Winnipeg NEXUS Office, Wellington Room 1074, Winnipeg, MB R3H0E3, CA"
	
	# Email Info
	# Set these values
	SENDER = None #sender email address - and login email for smtp server
	EMAIL_PASSWORD = "" #password for smtp server
	TO =  "" #email address to send the notifications
	SUBJECT = "GOES - Earlier Interview Found!" #subject of the email notification
	SMTP_SERVER = "" #smtp server address to use for email sending
	SMTP_PORT = 0 #smtp server port number

	# Notification cmd - change to something useful
	NOTIFY_CMD=None
	
	# Optionally set this value
	# Note: If set to None, comparison will use current booking date
	#       otherwise it will use this date to compare
	# **Must be in the format: "June 1, 2013 08:00" or set to  None
	compareToDate = None 
	
	# Used to store the current booking date found on GOES page
	currentBookingDate = ""
	
	#########
	# Custom functions to process GOES Website Information
	#########
	def test_g_o_e_s_interview_checker(self):
		driver = self.driver
		driver.get(self.GOES_BASE_URL + "/main/goes")
		driver.find_element_by_id("user").clear()
		driver.find_element_by_id("user").send_keys(self.GOES_USERNAME)
		driver.find_element_by_id("password").clear()
		driver.find_element_by_id("password").send_keys(self.GOES_PASSWORD)
		driver.find_element_by_id("SignIn").click()
		driver.find_element_by_link_text("Enter").click()
		driver.find_element_by_css_selector("img[alt=\"Manage Interview Appointment\"]").click()
		
		# set current booking date raw text value
		currentBookingRaw = driver.find_element_by_xpath("//div[@class='maincontainer']")
		currentBookingRawText = currentBookingRaw.text
		
		driver.find_element_by_name("reschedule").click()
		
		dropdown = driver.find_element_by_id("selectedEnrollmentCenter")
		
		# select preferred enrollment center
		for option in dropdown.find_elements_by_tag_name('option'):
			if option.text == self.GOES_PREFERRED_ENROLLMENT_CENTER:
				option.click() 
				
		driver.find_element_by_css_selector("img[alt=\"Next\"]").click()
		
		# find enrollment center earliest date value
		dateTds = driver.find_elements_by_xpath("//div[@class='maincontainer']/table/tbody/tr/td[contains(.,'Date:')]")
		# get plain text values and store them
		stringDateTds = []
		for td in dateTds:
			stringDateTds.append(td.text)
		
		# log-off of your GOES account
		driver.find_element_by_link_text("Log off").click()
		
		# after logging off now perform all the processing and logic
		# in case an error occurs with the processing, the website
		# will be sure to have already logged off
		
		# parse and set current booking date
		self.currentBookingDate = self.parseCurrentBookingDate(currentBookingRawText)
		
		#parse and check if the enrollment centers have earlier dates
		earlierDates = []
		for stringDate in stringDateTds:
			#print td.text
			if (self.isEarlierDate(stringDate)):	
				earlierDates.append(stringDate)

		# build email message
		emailMessage = '\n'.join(earlierDates)
		
		# if there's earlier dates, send the email
		if (len(earlierDates)):
			print "%d Earlier Date(s) Found!" % len(earlierDates)
			print "Sending Email Message: %s" % emailMessage
			self.sendEmail(emailMessage)
		else:
			print "NO Earlier Dates Found."
		
	def parseCurrentBookingDate(self, currentDateStr):
		dateStr = ""
		
		dateStr = currentDateStr.split("Date:")[1]
		dateStr = dateStr.split("Enrollment Center")[0]
		dateStr = dateStr.replace("Interview Time:", "")
		dateStr = dateStr.strip()
		
		currentDate = time.strptime(dateStr, "%b %d, %Y %H:%M")
		
		return currentDate
		
	def parseAvailDates(self, availDateStr):
		dateString = availDateStr.split("Date:")[1]
		dateString = dateString.split("End Time:")[0]
		dateString = dateString.replace("Start Time:", "")
		dateString = dateString.strip()
			
		return dateString
		
	def getDateForString(self, dateString):
		parsedDateString = self.parseAvailDates(dateString)
		dateStamp = time.strptime(parsedDateString, "%Y-%m-%d, %H%M,")
		
		return dateStamp
		
	def isEarlierDate(self, dateTd):
		containsEarlierDate = False
		
		# check the date against a set date
		availableDate = self.getDateForString(dateTd)
		dateToCompare = ""

		if (self.compareToDate is not None):
			dateToCompare = time.strptime(self.compareToDate, "%B %d, %Y %H:%M")
		else:
			dateToCompare = self.currentBookingDate
		
		if (availableDate < dateToCompare):
			containsEarlierDate = True
		
		return containsEarlierDate
		
	def sendEmail(self, message):
		if self.NOTIFY_CMD:
			process = Popen(self.NOTIFY_CMD, stdin=PIPE, stdout=None, stderr=None, shell=True)
			process.stdin.write(message)
			process.communicate()

		if self.SENDER:
			# Create a text/plain message
			msg = MIMEText(message)

			msg['Subject'] = self.SUBJECT
			msg['From'] = self.SENDER
			msg['To'] = self.TO

			# Send the message via provided server
			session = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)

			# Login to the smtp server
			session.ehlo()
			session.starttls()
			session.ehlo
			session.login(self.SENDER, self.EMAIL_PASSWORD)

			session.sendmail(self.SENDER, [self.TO], msg.as_string())
			session.quit()

	#######
	# Selenium Functions - DO NOT MODIFY
	######
	def setUp(self):
		self.driver = webdriver.Firefox()
		self.driver.implicitly_wait(30)
		self.verificationErrors = []
		self.accept_next_alert = True
		
	def is_element_present(self, how, what):
		try: self.driver.find_element(by=how, value=what)
		except NoSuchElementException, e: return False
		return True

	def is_alert_present(self):
		try: self.driver.switch_to_alert()
		except NoAlertPresentException, e: return False
		return True

	def close_alert_and_get_its_text(self):
		try:
			alert = self.driver.switch_to_alert()
			alert_text = alert.text
			if self.accept_next_alert:
				alert.accept()
			else:
				alert.dismiss()
			return alert_text
		finally: self.accept_next_alert = True

	def tearDown(self):
		self.driver.quit()
		self.assertEqual([], self.verificationErrors)

######
# Main - initiates the program
######
if __name__ == "__main__":
	unittest.main()
	
