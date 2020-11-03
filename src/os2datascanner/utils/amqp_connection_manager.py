#!/usr/bin/env python
import pika

from ..engine2.utilities.backoff import run_with_backoff
from .pika_settings import AMQP_SCHEME, AMQP_HOST, AMQP_PORT, AMQP_VHOST, AMQP_USER, AMQP_PWD, AMQP_BACKOFF_PARAMS

_amqp_obj = {
    "amqp_channels": None,
    "connection": None
}


def start_amqp(queue_name):
    """
    Starts an amqp connection and queue if it is not already started
    :param queue_name: Name of the queue
    """
    _, _ = run_with_backoff(
        _create_connection,
        pika.exceptions.AMQPConnectionError,
        **AMQP_BACKOFF_PARAMS,
    )
    _create_channel(queue_name)


def _create_channel(queue_name):
    """
    Creates an amqp queue if a connection is created.
    :param queue_name: Name of the queue
    """
    if _amqp_obj['connection']:
        _amqp_obj['amqp_channel'] = _amqp_obj['connection'].channel()
        _amqp_obj['amqp_channel'].queue_declare(queue=queue_name,
                                                passive=False, durable=True,
                                                exclusive=False, auto_delete=False)


def _create_connection():
    """
    Creates a amqp connection
    """
    if not _amqp_obj['connection']:
        conn_string_tpl = '{0}://{1}:{2}@{3}:{4}/{5}?heartbeat=6000'
        conn_string = conn_string_tpl.format(AMQP_SCHEME, 
                                             AMQP_USER, 
                                             AMQP_PWD, 
                                             AMQP_HOST,
                                             AMQP_PORT,
                                             AMQP_VHOST.lstrip('/'))
        params = pika.URLParameters(conn_string)
        _amqp_obj['connection'] = pika.BlockingConnection(params)


def send_message(routing_key, body):
    """
    Sends a message to the channel using the routing_key which is the queue name.
    :param routing_key: The name of the queue.
    :param body: The message to send to the queue.
    :return: None if no channel available.
    """
    if _amqp_obj['amqp_channel']:
        _amqp_obj['amqp_channel'].basic_publish(exchange='',
                                                routing_key=routing_key,
                                                body=body)
        return _amqp_obj['amqp_channel']
    else:
        return None


def ack_message(method):
    """
    Acknowledge message recieved on the channel.
    :param channel: The channel the queue is using.
    :param method: The callback method receiving the message.
    """
    try:
        if _amqp_obj['amqp_channel']:
            _amqp_obj['amqp_channel'].basic_ack(method.delivery_tag)
    except Exception as e:
        # How to handle this...
        print('Error occured while acknowleding message: {0}'.format(e))
        print('Message rejected on queue {0}'.format(method.routing_key))


def set_callback(func, queue_name):
    """
    Set callback method on queue
    :param func: Callback function
    :param queue_name: Name of the queue
    :return: None if no channel available
    """
    if _amqp_obj['amqp_channel']:
        return _amqp_obj['amqp_channel'].basic_consume(queue_name, func)
    else:
        return None


def purge_queue(queue_name):
    """
    Purge an existing queue
    :param queue_name: Name of the queue
    """
    if _amqp_obj['amqp_channel']:
        _amqp_obj['amqp_channel'].queue_purge(queue_name)


def start_consuming():
    """
    If a channel is available a consumer is started.
    """
    if _amqp_obj['amqp_channel']:
        _amqp_obj['amqp_channel'].start_consuming()


def close_connection():
    """
    Closes the connection if connection is created
    """
    if _amqp_obj['connection']:
        _amqp_obj['connection'].close()
        _amqp_obj['connection'] = None
