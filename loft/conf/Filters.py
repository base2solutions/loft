"""
FILTERING README:
Filters are defined by 'filter_name':'regex string' key, value pairs. Filters will be applied in logical order according
to the ##_name designator at the beginning of the key. For the purpose of system performance, the most broad filters
should be at the top of the list. Note that each key MUST be unique.

The filtering configuration must implement both a stateInspector and a outgoingFilter as described below.

STATE INSPECTOR: The stateInspector defines conditions that must be met inside the configured TTL window to
prompt a 'green system status'.

OUTGOING FILTER: The outgoingFilter defines forwarding decisions for messages coming through. If a match is made, the log will be
forwarded to the defined output.
"""

stateInspector = {
    '1_condition_1': '.*condition 1.*',
    '2_condition_2': '.*condition 2.*',
    '3_condition_3': '.*condition 3.*'
}

stateStatusMsgMet = "State inspector conditions met"
stateStatusMsgNotMet = "State inspector conditions NOT met"


#At a minimum should contain a match for the state status messages
outgoingFilter = {
    '01_allow_met': '.*State inspector conditions met.*',
    '02_allow_not_met': '.*State inspector conditions NOT met.*'
}


