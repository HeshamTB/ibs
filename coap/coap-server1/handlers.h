
#include <coap3/coap.h>
#include <coap3/coap_forward_decls.h>
#include <coap3/resource.h>
#include <coap3/str.h>

void hnd_get_hello(
    coap_resource_t *resource,
    coap_session_t *session,
    const coap_pdu_t *resquest,
    const coap_string_t *query_string,
    coap_pdu_t* response);
