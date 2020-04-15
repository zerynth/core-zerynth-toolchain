.. _zdm-cmd-events:

******
Events
******

In the ZDM events are used in devices to notify the occurrence of certain conditions.


List of device commands:

* :ref:`Get events <zdm-cmd-events-get>`

    
.. _zdm-cmd-workspace-events-get:

Get events
----------

To get all the events of a workspace use the command: ::

    zdm events uid

where :samp:`uid` is the uid of the workspace.

You can also filter result adding the options:
* :option:`--device-id`
* :option:`--start`
* :option:`--end`

    
