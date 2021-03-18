IP_CHANGE_BASE_ROUTE = '/ip-change/'


# === ALL PARAMS ============================================================ #
ROUTE_PARAM_REQUESTED_OPERATION = 'operation'
ROUTE_PARAM_FAILED_GATEWAYS     = 'failed_gateways'
ROUTE_PARAM_LAST_FAILED_GATEWAY = 'last_failed_gateway'
ROUTE_SUCCESSFUL_GATEWAY        = 'successful_gateway'
ROUTE_PARAM_PREVIOUS_GATEWAY    = 'previous_gateway'
# =========================================================================== #

# === ENUMS ================================================================= #
GET_NEW_GATEWAY_OPERATION  = 'get_new_gateway'
FINISH_IP_CHANGE_OPERATION = 'finish_ip_change'
# =========================================================================== #

# === SHORT NAMES =========================================================== #
RP_REQ_OPERATION  = ROUTE_PARAM_REQUESTED_OPERATION
RP_FAILED_GATES   = ROUTE_PARAM_FAILED_GATEWAYS
RP_LAST_FAIL_GATE = ROUTE_PARAM_LAST_FAILED_GATEWAY
RP_SUCCESS_GATE   = ROUTE_SUCCESSFUL_GATEWAY
RP_PREV_GATE      = ROUTE_PARAM_PREVIOUS_GATEWAY

OP_NEW_GATE      = GET_NEW_GATEWAY_OPERATION
OP_FIN_IP_CHANGE = FINISH_IP_CHANGE_OPERATION
# =========================================================================== #

ALL_PARAMETERS = [
    RP_REQ_OPERATION ,
    RP_FAILED_GATES  ,
    RP_LAST_FAIL_GATE,
    RP_SUCCESS_GATE  ,
    RP_PREV_GATE     ,
]

SUPPORTED_OPERATIONS = [OP_FIN_IP_CHANGE, OP_NEW_GATE]

SINGLE_IP_PARAMS = [RP_PREV_GATE, RP_SUCCESS_GATE, RP_LAST_FAIL_GATE]

# === Responces ============================================================= #
MESSAGE = 'message'
NEW_GATEWAY = 'new_gateway'
# =========================================================================== #

# === Result codes ========================================================== #
RC_OK = 200
# =========================================================================== #
