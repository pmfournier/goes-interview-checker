# GOES NEXUS Interview Checker
 
## Introduction

This script can be used to automate checking of GOES NEXUS interview times. If an interview time is found, an email notification will be sent to alert you.
In order to run this, you must first have [Selenium](http://docs.seleniumhq.org/download/) python library installed.
Once installed, simply set the required GOES login and email information in the Python file, and run the Python script.

## Broken selenium

There is an issue with some versions of Selenium/Ubuntu where firefox will not be able to start. In this case, try installing the latest version using
	# pip install -U selenium

## Headless machine

In order to use on a headless machine, use xvfb:
	$ xvfb-run python GOESInterviewChecker.py
