#!/usr/bin/env python
import unittest
from ...utils.pika_connection_manager import PikaConnectionManager


class PikaConnectionManagerTest(unittest.TestCase):

    pika_manager = None
    queue_name = 'test'
    message = 'hejsa'

    def consume_message(self, channel, method, properties, body):
        ack_message(channel, method)

    def setUp(self):
        self.pika_manager = PikaConnectionManager()
        self.pika_manager.start_amqp(self.queue_name)
        self.pika_manager.purge_queue(self.queue_name)

    def tearDown(self):
        self.pika_manager.purge_queue(self.queue_name)
        self.pika_manager.close_connection()
        self.pika_manager = None

    def test_set_callback(self):
        consumer_tag = self.pika_manager.set_callback(self.consume_message, self.queue_name)
        self.assertNotEqual(consumer_tag, None)

    def test_send_message(self):
        channel = self.pika_manager.send_message(self.queue_name, self.message)
        method_frame, header_frame, body = channel.basic_get(self.queue_name)

        self.assertEqual(body.decode("utf-8"), self.message)
        self.assertEqual(method_frame.message_count, 0)

    def test_ack_message(self):
        channel = self.pika_manager.send_message(self.queue_name, self.message)
        method_frame, header_frame, body = channel.basic_get(self.queue_name)
        self.pika_manager.ack_message(method_frame)
        self.assertEqual(channel.is_open, True)
        self.assertEqual(method_frame.delivery_tag, 1)

    def test_multiple_queues(self):
        name0 = self.queue_name
        name1 = 'test1'
        name2 = 'test2'
        name3 = 'test3'
        # name0 is already started in setUp()
        self.pika_manager.start_amqp(name1)
        self.pika_manager.start_amqp(name2)
        self.pika_manager.start_amqp(name3)

        message0 = self.message
        message1 = 'hejsa1'
        message2 = 'hejsa2'
        message3 = 'hejsa3'

        self._send_message(message0, name0, 1)

        self._send_message(message1, name1, 2)

        self._send_message(message2, name2, 3)

        self._send_message(message3, name3, 4)

    def _send_message(self, message, queue_name, expected_delivery_tag):
        channel = self.pika_manager.send_message(queue_name, message)
        method_frame, header_frame, body = channel.basic_get(queue_name)

        self.assertEqual(body.decode("utf-8"), message)
        self.assertEqual(method_frame.message_count, 0)

        self.pika_manager.ack_message(method_frame)

        self.assertEqual(channel.is_open, True)
        self.assertEqual(method_frame.delivery_tag, expected_delivery_tag)

        self.pika_manager.purge_queue(self.queue_name)
