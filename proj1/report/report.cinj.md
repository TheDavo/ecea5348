---
title: ECEA5348 Project 1
author: Davit Khudaverdyan
date: 12 March 2024
---

# Table of Contents
1. [Introduction](#introduction)
    1. [Implementation and Assumptions](#implementation-and-assumptions)
2. [Code](#code)
    2. [Server Code](#server-code)
    2. [Client Code](#client-code)
3. [Images](#images)
    3. [Server Images](#server-images)
    3. [Client Images](#client-images)


# Introduction

ECEA5348's first project is to get an understanding of using cloud tools
such as AWS to send messages to "Things." A lot of this project involves
the initial setup of an AWS, setting up a Thing, and sending it messages 
using the MQTT protocol through the Python libraries `paho` and 
reading the SQS messsages from `boto3`.

The data generated is from a pseudo temperature and humidity sensor. That 
data is sent from our "local device" to the AWS cloud where it is retained
in AWS for the default four days.

## Implementation and Assumptions

This being the first time working with AWS there was a lot of learning to 
get the system setup. Luckily, the AWS tutorials had great step-by-step
guides to getting a setup running on Windows.

The first step to making sure the setup would work was to install the 
`awdiotsdk` and the examples files from AWS and execute them and see them
working after the initial Thing setup.

From there, it was following directions on setting up the SQS and learning
howt to use `paho` and `boto3` to get started. Using `paho` had some challenges
at first due to the older guide. The MQTT standard is now on version five, 
therefore the older library would not work with a simple copy-paste.

It took a lot of searching and reading the documents to get `paho` to work,
even though the change was super simple. Thankfully, `paho`'s example
on GitHub and [Steve's Guide](http://www.steves-internet-guide.com/python-mqtt-client-changes/)
helped understand the differences from the class's links to what the latest
libraries required to get started.

Once the Python code ran fine, and everything was working on the AWS Console,
it was time to right the client code that would then consume the messages
from the SQS queue.

Once assumption here was that once the message was read, it was to be deleted
from the SQS queue, in other words, the data is consumed and assumed to be
properly used by the end user or application.

To ensure that the code is safe and nothing is exposed, the `dotenv` library 
is installed and used to hide locations of the private keys, access keys,
and endpoints of the AWS setup.

# Code

The code is split into two components, `server.py` and `client.py`. The code in
`server.py` establishes the connection to the AWS Thing through the endpoint
and publishes the humidity, temperature, and datetime data through the
"sensor/data" topic. 

The `on_message` function parses incoming data to tell the server to stop
sending data to and to gracefully exit the application. This is done through
the AWS Console through the MQTT Testing page. The `handle_command` helper
function slims down the code a bit and handles the `stop`, `pause`, and
`resume` commands that can be submitted through the "control/commands" topic.

The `client.py` script loops through the queued messages and continues to
run until all the messages are consumed.

## Server Code

cinj{../server.py}

## Client Code

cinj{../client.py}

# Images
## Server Images

Server on startup, showing success message on connect and sending messages
immediately after startup:

![Server on startup](./images/server_startup.png "Server on startup")

Server closing:

![Server closing](./images/stop_command.png "Server closing on stop command")

Server with pause/resume/stop commands from "control/commands" topic:

![Server control/commands messages](./images/server_pause_resume_stop.png "Server responding to control/commands messages")

## Client images

The image below shows the client receiving messages from the SQS client,
printing the messages, and then deleting them from the queue.

![Client consuming messages](./images/client_sqs_receive.png "Client consuming SQS messages")

When there are no more messages, the client will report that too:

![Client showing no available messages](./images/client_no_more_messages.png "Client showing no available messages")
