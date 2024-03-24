---
title: ECEA5348 Project 2
author: Davit Khudaverdyan
date: 24 March 2024
---

# Table of Contents
1. [Introduction](#introduction)
    1. [Implementation and Assumptions](#implementation-and-assumptions)
2. [Code](#code)
    2. [Lambda MySQL RDS Function](#lambda-mysql-rds-function)
    2. [Lambda API Gateway Handler](#lambda-api-gateway-handler)
    2. [Python REST API Caller](#python-rest-api-caller)
3. [Images](#images)
    3. [Server Images](#server-images)
    3. [API Client Images](#rest-api-client-images)



# Introduction

ECEA5348's second project is to take the insfrastructure built in the first
project and add Lambda code to take the project further. In this project the
goal is to use the AWS infrastructure to send the sensor data to a database
and build an API to get the new data.

# Implementation and Assumptions

This project had a lot of rough edges to it at the beginning. Lots of little
parts are added together to get the project working, ranging from the IoT Core
to the IAM role manager. Altogether, these were the systems that had to be
used to get this project finished:

1. IoT Core
1. AWS Lambda
1. SQS (although this was not used after the first project)
1. MySQL RDS
1. IAM Role Manager
1. Secrets Manager
1. VPC Endpoints
1. API Gateway

This time around, compared to the first project, the challenge was not
in programming, but learning how AWS worked. Some challenges at the beginning
with getting systems connected lead to an `Admin` role that allowed all access
to the tools to reduce the headache of learning all these systems.

Once the project started working, it started to make sense (especially thinking
about scaling) why these tools are in place and that the initial hurdle is
very much worth it when working on larger scale projects.

The most difficult part of this project was getting the Lambda functions to
properly communicate with the other services. Following the tutorials, the 
Lambda functions needed to be routed through Virtual Private Connections and
appropriate security policies to have access to other services. At first, the
Lambda functions could not connect to the Secrets Manager as the VPCs that
were being used did not have that service attached to them. These headaches
caused the most trouble, as the code used was from the tutorials but those
other steps were easier to miss or to not include in a tutorial.

Once the Secret Manager and RDS connection issues were fixed the rest became
easy as the lessons learned from the first two were easy to carry to the 
API Gateway specification of the project.

# Code

Two Lambda functions and a simple command line Python API caller were written
as part of the project specifications to upload and receive data.

## Lambda MySQL RDS Function

The first Lambda function takes the data from the sensor and adds it to the
database made with MySQL. Because the data format is easy, the addition process
is not lengthy and not a lot of error checking is performed. At this point the
data is assumed to be correct.

cinj{../lambda_data_into_db.py}

## Lambda API Gateway Handler

The API calls require access to the database, therefore the Secrets Manager
boilerplate code is reused to open the connection. The user, when callin the 
API, is able to query with two parameters, `count` and `id`. Additional queries
can be developed where the main challenge is to add to the `WHERE` clause 
creation and building the query correctly.

cinj{../lambda_api_handler.py}

## Python REST API Caller

Using Python and an external module, `requests`, a small Command Line tool is
made that can call the deployed API and retrieve data from the MySQL database.

The `argparse` library makes CLI tool development simple, and adding the query
parameters (`count`, `id`) as options was easy to do and added a nice layer
of interactivity when calling the API.

cinj{../api_caller.py}


# Images 
## Server Images

Server on startup, showing success message on connect and sending messages
immediately after startup:

![Server on startup](./images/server_startup.png "Server on startup")

Server closing:

![Server closing](./images/stop_command.png "Server closing on stop command")

Server with pause/resume/stop commands from "control/commands" topic:

![Server control/commands messages](./images/server_pause_resume_stop.png "Server responding to control/commands messages")

## REST API Client Images

Since the client is using `argparse` the user can use the `-h` option to show
the available commands.

![API Caller Help](./images/api_caller_help.png "API Caller help option")

Using the `count` parameter, the user can request a number of records to fetch.

![API Caller Count Use](./images/api_caller_count.png  "Fetch a number of records")
