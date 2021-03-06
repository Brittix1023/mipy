##-*************************
##-* This software can be used, redistributed and/or modified under
##-* the terms of the BSD 2-clause license as found in the file
##-* 'License.txt' in this distribution.
##-* This source code is (C)copyright Geoffrey French 1999-2014.
##-*************************

class Comm(object):
	def __init__(self, kernel_connection, comm_id, target_name, primary):
		self.__kernel = kernel_connection
		self.comm_id = comm_id
		self.target_name = target_name
		self.primary = primary

		self.on_message = None
		self.on_closed_remotely = None


	def send(self, data, listener=None):
		kernel = self.__kernel
		if kernel._open:
			msg, msg_id = kernel.session.send(kernel.shell, 'comm_msg', {
				'comm_id': self.comm_id,
				'data': data
			})
			if listener is not None:
				kernel._attach_listener(msg_id, listener)

	def close(self, data, listener=None):
		kernel = self.__kernel
		if kernel._open:
			msg, msg_id = kernel.session.send(kernel.shell, 'comm_close', {
				'comm_id': self.comm_id,
				'data': data
			})
			kernel._notify_comm_closed(self)
			if listener is not None:
				kernel._attach_listener(msg_id, listener)


	def _handle_message(self, data, kernel_request_listener):
		if self.on_message is not None:
			self.on_message(self, data, kernel_request_listener)

	def _handle_closed_remotely(self, data, kernel_request_listener):
		if self.on_closed_remotely is not None:
			self.on_closed_remotely(self, data, kernel_request_listener)



class CommManager (object):
	def __init__(self, default_handler=None):
		self.__target_to_handler = {}
		self.__default_handler = default_handler


	def register_comm_open_handler(self, target_name, handler):
		self.__target_to_handler[target_name] = handler

	def unregister_comm_open_handler(self, target_name):
		del self.__target_to_handler[target_name]


	def on_comm_open(self, comm, data):
		handler = self.__target_to_handler.get(comm.target_name, self.__default_handler)
		if handler is not None:
			handler(comm, data)