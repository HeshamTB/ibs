/* minimal CoAP server
 *
 * Copyright (C) 2018-2021 Olaf Bergmann <bergmann@tzi.org>
 * Edited by Hesham T. Banafa Mar 8, 2022 for ibs
 */

#include <gsl/gsl_matrix_uint.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <sys/socket.h>

#include <gsl/gsl_matrix.h>
#include <coap3/coap.h>
#include "common.h"
#include "handlers.h"

int main(void) {
  coap_context_t  *ctx = NULL;
  coap_address_t dst;
  coap_resource_t *resource = NULL;
  coap_endpoint_t *endpoint = NULL;
  int result = EXIT_FAILURE;;
  coap_str_const_t *ruri = coap_make_str_const("hello");
  coap_startup();

  /* resolve destination address where server should be sent */
  
  if (resolve_address("localhost", "5683", &dst) < 0) {
    coap_log(LOG_CRIT, "failed to resolve address\n");
    goto finish;
  }

  /* create CoAP context and a client session */
  ctx = coap_new_context(NULL);

  if (!ctx || !(endpoint = coap_new_endpoint(ctx, &dst, COAP_PROTO_UDP))) {
    coap_log(LOG_EMERG, "cannot initialize context\n");
    goto finish;
  }

  resource = coap_resource_init(ruri, 0);
  // coap_register_handler(resource, COAP_REQUEST_GET,
  //                       [](auto, auto,
  //                          const coap_pdu_t *request,
  //                          auto,
  //                          coap_pdu_t *response) {
  //                         coap_show_pdu(LOG_WARNING, request);
  //                         coap_pdu_set_code(response, COAP_RESPONSE_CODE_CONTENT);
  //                         coap_add_data(response, 5,
  //                                       (const uint8_t *)"world");
  //                         coap_show_pdu(LOG_WARNING, response);
  //                       });
  
  /* From what I understand, we need to implement the coap_method_handler_t
      a supply a fucntion ptr to a function that takes args defined in
      coap_method_handler_t typedef.
      Holy crap this different. 
      This kind of typedef is similar to a java abstract class or interface..
      (somefunkystudd.txt)
      Mar 8, 2022 - H.B. */
  
  //coap_method_handler_t  hnd = &hnd_get_hello;
  coap_register_handler(resource, COAP_REQUEST_GET, &hnd_get_hello);
  coap_add_resource(ctx, resource);

  while (true) { coap_io_process(ctx, COAP_IO_WAIT); }

  result = EXIT_SUCCESS;
 finish:

  coap_free_context(ctx);
  coap_cleanup();

  return result;
}