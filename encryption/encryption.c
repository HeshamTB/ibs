/* 
 * Wrapper around mbedtls to provide AES encryption
 *
 * Needs esp32 arduino platform libraries
 *
 * Hesham T. Banafa 
 * May 9th, 2022
 *
 */
#include <string.h>
#include "encryption.h"

static int valid_time(long long time_epoch);

extern void aes_init(aes_t *ctx, char *key)
{
    mbedtls_aes_init(&ctx->aes_ctx);
    //mbedtls_aes_setkey_enc(ctx->aes_ctx, (const unsigned char*)key, strlen(key) * 8 );
    ctx->psk_key = key; // Save key ptr
}

extern void aes_encrypt(aes_t *ctx, char *plain_text, char *out_buf)
{
    if (ctx == NULL) return; // What are you doing? out_buf remains as is.
    mbedtls_aes_setkey_enc(&ctx->aes_ctx, (const unsigned char*)ctx->psk_key, strlen(ctx->psk_key) * 8 );
    mbedtls_aes_crypt_ecb(&ctx->aes_ctx, MBEDTLS_AES_ENCRYPT, (const unsigned char*)plain_text, (unsigned char*)out_buf);
}

extern void aes_decrypt(aes_t *ctx, char *cipher_text, char *out_buf) 
{
    
}

