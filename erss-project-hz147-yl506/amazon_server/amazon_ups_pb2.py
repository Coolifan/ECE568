# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: amazon_ups.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='amazon_ups.proto',
  package='',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x10\x61mazon_ups.proto\"\xa6\x01\n\x11request_get_truck\x12\x10\n\x08order_id\x18\x01 \x02(\x03\x12\x13\n\x0bups_account\x18\x02 \x01(\t\x12\x14\n\x0cwarehouse_id\x18\x03 \x02(\x05\x12\x12\n\nlocation_x\x18\x04 \x02(\x05\x12\x12\n\nlocation_y\x18\x05 \x02(\x05\x12\x15\n\rdestination_x\x18\x06 \x02(\x05\x12\x15\n\rdestination_y\x18\x07 \x02(\x05\"+\n\x15request_init_delivery\x12\x12\n\npackage_id\x18\x01 \x02(\x03\"f\n\x1arequest_change_destination\x12\x12\n\npackage_id\x18\x01 \x02(\x03\x12\x19\n\x11new_destination_x\x18\x02 \x02(\x05\x12\x19\n\x11new_destination_y\x18\x03 \x02(\x05\"\xaf\x01\n\nAUCommands\x12%\n\tget_truck\x18\x01 \x01(\x0b\x32\x12.request_get_truck\x12-\n\rinit_delivery\x18\x02 \x01(\x0b\x32\x16.request_init_delivery\x12\x37\n\x12\x63hange_destination\x18\x03 \x01(\x0b\x32\x1b.request_change_destination\x12\x12\n\ndisconnect\x18\x04 \x01(\x08\"Z\n\x16response_truck_arrived\x12\x0c\n\x04wh_x\x18\x01 \x02(\x05\x12\x0c\n\x04wh_y\x18\x02 \x02(\x05\x12\x10\n\x08truck_id\x18\x03 \x02(\x05\x12\x12\n\npackage_id\x18\x04 \x02(\x03\"0\n\x1aresponse_package_delivered\x12\x12\n\npackage_id\x18\x01 \x02(\x03\"y\n\x1cresponse_destination_changed\x12\x19\n\x11new_destination_x\x18\x01 \x02(\x05\x12\x19\n\x11new_destination_y\x18\x02 \x02(\x05\x12\x12\n\npackage_id\x18\x03 \x02(\x03\x12\x0f\n\x07success\x18\x04 \x02(\x08\"\xd6\x01\n\nUACommands\x12.\n\rtruck_arrived\x18\x01 \x01(\x0b\x32\x17.response_truck_arrived\x12\x36\n\x11package_delivered\x18\x02 \x01(\x0b\x32\x1b.response_package_delivered\x12:\n\x13\x64\x65stination_changed\x18\x03 \x01(\x0b\x32\x1d.response_destination_changed\x12\x12\n\ndisconnect\x18\x04 \x01(\x08\x12\x10\n\x08world_id\x18\x05 \x01(\x03')
)




_REQUEST_GET_TRUCK = _descriptor.Descriptor(
  name='request_get_truck',
  full_name='request_get_truck',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='order_id', full_name='request_get_truck.order_id', index=0,
      number=1, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ups_account', full_name='request_get_truck.ups_account', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='warehouse_id', full_name='request_get_truck.warehouse_id', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='location_x', full_name='request_get_truck.location_x', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='location_y', full_name='request_get_truck.location_y', index=4,
      number=5, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='destination_x', full_name='request_get_truck.destination_x', index=5,
      number=6, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='destination_y', full_name='request_get_truck.destination_y', index=6,
      number=7, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=21,
  serialized_end=187,
)


_REQUEST_INIT_DELIVERY = _descriptor.Descriptor(
  name='request_init_delivery',
  full_name='request_init_delivery',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='package_id', full_name='request_init_delivery.package_id', index=0,
      number=1, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=189,
  serialized_end=232,
)


_REQUEST_CHANGE_DESTINATION = _descriptor.Descriptor(
  name='request_change_destination',
  full_name='request_change_destination',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='package_id', full_name='request_change_destination.package_id', index=0,
      number=1, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='new_destination_x', full_name='request_change_destination.new_destination_x', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='new_destination_y', full_name='request_change_destination.new_destination_y', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=234,
  serialized_end=336,
)


_AUCOMMANDS = _descriptor.Descriptor(
  name='AUCommands',
  full_name='AUCommands',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='get_truck', full_name='AUCommands.get_truck', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='init_delivery', full_name='AUCommands.init_delivery', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='change_destination', full_name='AUCommands.change_destination', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='disconnect', full_name='AUCommands.disconnect', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=339,
  serialized_end=514,
)


_RESPONSE_TRUCK_ARRIVED = _descriptor.Descriptor(
  name='response_truck_arrived',
  full_name='response_truck_arrived',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='wh_x', full_name='response_truck_arrived.wh_x', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='wh_y', full_name='response_truck_arrived.wh_y', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='truck_id', full_name='response_truck_arrived.truck_id', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='package_id', full_name='response_truck_arrived.package_id', index=3,
      number=4, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=516,
  serialized_end=606,
)


_RESPONSE_PACKAGE_DELIVERED = _descriptor.Descriptor(
  name='response_package_delivered',
  full_name='response_package_delivered',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='package_id', full_name='response_package_delivered.package_id', index=0,
      number=1, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=608,
  serialized_end=656,
)


_RESPONSE_DESTINATION_CHANGED = _descriptor.Descriptor(
  name='response_destination_changed',
  full_name='response_destination_changed',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='new_destination_x', full_name='response_destination_changed.new_destination_x', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='new_destination_y', full_name='response_destination_changed.new_destination_y', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='package_id', full_name='response_destination_changed.package_id', index=2,
      number=3, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='success', full_name='response_destination_changed.success', index=3,
      number=4, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=658,
  serialized_end=779,
)


_UACOMMANDS = _descriptor.Descriptor(
  name='UACommands',
  full_name='UACommands',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='truck_arrived', full_name='UACommands.truck_arrived', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='package_delivered', full_name='UACommands.package_delivered', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='destination_changed', full_name='UACommands.destination_changed', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='disconnect', full_name='UACommands.disconnect', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='world_id', full_name='UACommands.world_id', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=782,
  serialized_end=996,
)

_AUCOMMANDS.fields_by_name['get_truck'].message_type = _REQUEST_GET_TRUCK
_AUCOMMANDS.fields_by_name['init_delivery'].message_type = _REQUEST_INIT_DELIVERY
_AUCOMMANDS.fields_by_name['change_destination'].message_type = _REQUEST_CHANGE_DESTINATION
_UACOMMANDS.fields_by_name['truck_arrived'].message_type = _RESPONSE_TRUCK_ARRIVED
_UACOMMANDS.fields_by_name['package_delivered'].message_type = _RESPONSE_PACKAGE_DELIVERED
_UACOMMANDS.fields_by_name['destination_changed'].message_type = _RESPONSE_DESTINATION_CHANGED
DESCRIPTOR.message_types_by_name['request_get_truck'] = _REQUEST_GET_TRUCK
DESCRIPTOR.message_types_by_name['request_init_delivery'] = _REQUEST_INIT_DELIVERY
DESCRIPTOR.message_types_by_name['request_change_destination'] = _REQUEST_CHANGE_DESTINATION
DESCRIPTOR.message_types_by_name['AUCommands'] = _AUCOMMANDS
DESCRIPTOR.message_types_by_name['response_truck_arrived'] = _RESPONSE_TRUCK_ARRIVED
DESCRIPTOR.message_types_by_name['response_package_delivered'] = _RESPONSE_PACKAGE_DELIVERED
DESCRIPTOR.message_types_by_name['response_destination_changed'] = _RESPONSE_DESTINATION_CHANGED
DESCRIPTOR.message_types_by_name['UACommands'] = _UACOMMANDS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

request_get_truck = _reflection.GeneratedProtocolMessageType('request_get_truck', (_message.Message,), dict(
  DESCRIPTOR = _REQUEST_GET_TRUCK,
  __module__ = 'amazon_ups_pb2'
  # @@protoc_insertion_point(class_scope:request_get_truck)
  ))
_sym_db.RegisterMessage(request_get_truck)

request_init_delivery = _reflection.GeneratedProtocolMessageType('request_init_delivery', (_message.Message,), dict(
  DESCRIPTOR = _REQUEST_INIT_DELIVERY,
  __module__ = 'amazon_ups_pb2'
  # @@protoc_insertion_point(class_scope:request_init_delivery)
  ))
_sym_db.RegisterMessage(request_init_delivery)

request_change_destination = _reflection.GeneratedProtocolMessageType('request_change_destination', (_message.Message,), dict(
  DESCRIPTOR = _REQUEST_CHANGE_DESTINATION,
  __module__ = 'amazon_ups_pb2'
  # @@protoc_insertion_point(class_scope:request_change_destination)
  ))
_sym_db.RegisterMessage(request_change_destination)

AUCommands = _reflection.GeneratedProtocolMessageType('AUCommands', (_message.Message,), dict(
  DESCRIPTOR = _AUCOMMANDS,
  __module__ = 'amazon_ups_pb2'
  # @@protoc_insertion_point(class_scope:AUCommands)
  ))
_sym_db.RegisterMessage(AUCommands)

response_truck_arrived = _reflection.GeneratedProtocolMessageType('response_truck_arrived', (_message.Message,), dict(
  DESCRIPTOR = _RESPONSE_TRUCK_ARRIVED,
  __module__ = 'amazon_ups_pb2'
  # @@protoc_insertion_point(class_scope:response_truck_arrived)
  ))
_sym_db.RegisterMessage(response_truck_arrived)

response_package_delivered = _reflection.GeneratedProtocolMessageType('response_package_delivered', (_message.Message,), dict(
  DESCRIPTOR = _RESPONSE_PACKAGE_DELIVERED,
  __module__ = 'amazon_ups_pb2'
  # @@protoc_insertion_point(class_scope:response_package_delivered)
  ))
_sym_db.RegisterMessage(response_package_delivered)

response_destination_changed = _reflection.GeneratedProtocolMessageType('response_destination_changed', (_message.Message,), dict(
  DESCRIPTOR = _RESPONSE_DESTINATION_CHANGED,
  __module__ = 'amazon_ups_pb2'
  # @@protoc_insertion_point(class_scope:response_destination_changed)
  ))
_sym_db.RegisterMessage(response_destination_changed)

UACommands = _reflection.GeneratedProtocolMessageType('UACommands', (_message.Message,), dict(
  DESCRIPTOR = _UACOMMANDS,
  __module__ = 'amazon_ups_pb2'
  # @@protoc_insertion_point(class_scope:UACommands)
  ))
_sym_db.RegisterMessage(UACommands)


# @@protoc_insertion_point(module_scope)
