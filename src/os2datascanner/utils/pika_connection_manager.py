#!/usr/bin/env python
import pika

from .pika_settings import AMQP_HOST

class PikaConnectionManager(object):

    _pika_obj = {
        "amqp_channels": None,
        "connection": None
    }


    def start_amqp(self, queue_name):
        """
        Starts an amqp connection and queue if it is not already started
        :param queue_name: Name of the queue
        """
        self._create_connection()
        self._create_channel(queue_name)


    def _create_channel(self, queue_name):
        """
        Creates an amqp queue if a connection is created.
        :param queue_name: Name of the queue
        """
        if self._pika_obj['connection']:
            self._pika_obj['amqp_channel'] = self._pika_obj['connection'].channel()
            self._pika_obj['amqp_channel'].queue_declare(queue=queue_name,
                                                         passive=False, durable=True,
                                                         exclusive=False, auto_delete=False)


    def _create_connection(self):
        """
        Creates a amqp connection
        """
        if not self._pika_obj['connection']:
            conn_params = pika.ConnectionParameters(AMQP_HOST,
                                                    heartbeat=6000)
            self._pika_obj['connection'] = pika.BlockingConnection(conn_params)


    def send_message(self, routing_key, body):
        """
        Sends a message to the channel using the routing_key which is the queue name.
        :param routing_key: The name of the queue.
        :param body: The message to send to the queue.
        :return: None if no channel available.
        """
        if self._pika_obj['amqp_channel']:
            self._pika_obj['amqp_channel'].basic_publish(exchange='',
                                                         routing_key=routing_key,
                                                         body=body)
            return self._pika_obj['amqp_channel']
        else:
            return None


    def ack_message(self, method):
        """
        Acknowledge message recieved on the channel.
        :param channel: The channel the queue is using.
        :param method: The callback method receiving the message.
        """
        try:
            if self._pika_obj['amqp_channel']:
                self._pika_obj['amqp_channel'].basic_ack(method.delivery_tag)
        except Exception as e:
            # How to handle this...
            print('Error occured while acknowleding message: {0}'.format(e))
            print('Message rejected on queue {0}'.format(method.routing_key))


    def set_callback(self, func, queue_name):
        """
        Set callback method on queue
        :param func: Callback function
        :param queue_name: Name of the queue
        :return: None if no channel available
        """
        if self._pika_obj['amqp_channel']:
            return self._pika_obj['amqp_channel'].basic_consume(queue_name, func)
        else:
            return None


    def purge_queue(self, queue_name):
        """
        Purge an existing queue
        :param queue_name: Name of the queue
        """
        if self._pika_obj['amqp_channel']:
            self._pika_obj['amqp_channel'].queue_purge(queue_name)


    def start_consuming(self):
        """
        If a channel is available a consumer is started.
        """
        if self._pika_obj['amqp_channel']:
            self._pika_obj['amqp_channel'].start_consuming()


    def close_connection(self):
        """
        Closes the connection if connection is created
        """
        if self._pika_obj['connection']:
            self._pika_obj['connection'].close()
            self._pika_obj['connection'] = None
            self._pika_obj['connection'] = None
