#!/usr/bin/env python
import pika
import json
import socket

connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()
channel.queue_declare(queue='tcp')

def callback(ch, method, properties, body):
    req = json.loads(body)

    host = json.loads(req["monitor"]["check"]["arguments"])["host"]
    port = json.loads(req["monitor"]["check"]["arguments"])["port"]
    status = "ok"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
    except IOError:
        status = "fail"

    req["monitor"]["result"]= {}
    req["monitor"]["result"]["status"] = status
    req["monitor"]["result"]["check"] = req["monitor"]["check"]
    del req["monitor"]["check"]
    print req
    resp = json.dumps(req)
    print resp
    channel.queue_declare(queue='results')
    channel.basic_publish(exchange='',
                          routing_key='results',
                          body=resp)

channel.basic_consume(callback,
                      queue='tcp',
                      no_ack=True)
channel.start_consuming()
