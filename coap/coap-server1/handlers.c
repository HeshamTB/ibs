#include "handlers.h"
#include <coap3/resource.h>

void hnd_get_hello(coap_resource_t *resource,
    coap_session_t *session,
    const coap_pdu_t *request,
    const coap_string_t *query_string,
    coap_pdu_t *response)
{
    coap_show_pdu(LOG_WARNING, request);
    coap_pdu_set_code(response, COAP_RESPONSE_CODE_CONTENT);
    coap_add_data(response, 5, (const uint8_t *)"world");
    coap_show_pdu(LOG_WARNING, response);
    return;
}