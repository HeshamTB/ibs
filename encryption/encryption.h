/* 
 * Wrapper around mbedtls to provide AES encryption
 *
 * Needs esp32 arduino platform libraries
 *
 * Hesham T. Banafa 
 * May 9th, 2022
 *
 */

#include "mbedtls/aes.h"

typedef struct aes_t 
{
    const char *psk_key;
    mbedtls_aes_context aes_ctx;
} aes_t;

static int valid_time(long long time_epoch);

extern void aes_init(aes_t *ctx, char *key);
extern void aes_encrypt(aes_t *ctx, char *plain_text, char *out_buf);
extern void aes_decrypt(aes_t *ctx, char *cipher_text, char *out_buf);

