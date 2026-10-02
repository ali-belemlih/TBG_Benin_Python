#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "asn_application.h"
#include "asn_system.h"
#include "asn_internal.h"
#include "CallDataRecord.h"
#include <MSOriginating.h>
#include <MSTerminatingSMSinMSC.h>
#include <CallForwarding.h>
#include <RoamingCallForwarding.h>
#include <MSTerminating.h>
#include <MSTerminatingSMSinSMS-GMSC.h>
#include <MSOriginatingSMSinMSC.h>
#include <MSOriginatingSMSinSMS-IWMSC.h>
#include <SSProcedure.h>
#include <TransitINOutgoingCall.h>
#include <INIncomingCall.h>
#include <INOutgoingCall.h>
#include <ISDNOriginating.h>
#include <ISDNCallForwarding.h>
#include <ISDNSSProcedure.h>
#include <SCFChargingOutput.h>
#include <LocationServices.h>
asn_dec_rval_t decode_record(const void *buffer, size_t size);
void decode_tbcd(const uint8_t *data, size_t length, char *output);
void decode_octet_string(const uint8_t *data, size_t length, char *output);
void processCallDataRecord(const CallDataRecord_t *record);
void process_umts_gsm_record(const UMTSGSMPLMNCallDataRecord_t *record);
void process_composite_record(const CompositeCallDataRecord_t *composite_record);
void process_ms_mSTerminatingSMSinMSC(const MSTerminatingSMSinMSC_t *record);
void process_ms_mSOriginating(const MSOriginating_t *record);
void process_callForwarding(const CallForwarding_t *);
void process_mSTerminating(const MSTerminating_t *);
void process_locationServices(const LocationServices_t *);
void process_msOriginatingSMSinMSC(const MSOriginatingSMSinMSC_t *);
void process_msOriginatingSMSinSMSIWMSC(const MSOriginatingSMSinSMS_IWMSC_t *);
void process_msTerminatingSMSinSMSGMSC(const MSTerminatingSMSinSMS_GMSC_t *);
void process_ssProcedure(const SSProcedure_t *);
void process_roamingCallForwarding(const RoamingCallForwarding_t *);
void process_transit(const Transit_t *);
void process_isdnOriginating(const ISDNOriginating_t *);
void process_transitINOutgoingCall(const TransitINOutgoingCall_t *);
void process_inIncomingCall(const INIncomingCall_t *);
void process_inOutgoingCall(const INOutgoingCall_t *);
void process_isdnCallForwarding(const ISDNCallForwarding_t *);
void process_scfChargingOutput(const SCFChargingOutput_t *);
void process_isdnSSProcedure(const ISDNSSProcedure_t *);
char* buffer_to_hex(const uint8_t* buf, size_t size);
const char* getCallPositionString(int value);
const char* getFirstradiochannelused(int value);
const char* getSpeechcoderversion(int value);
const char* getChargedparty(int value);
const char* getDisconnectingParty(int value);
const char* getOutputType(int value);
const char* getRadiochannelproperty(int value);
const char* getTariffSwitchInd(int value);
const char* getMessageTypeindicator(int value);
const char* getAirInterfaceUserRate(int value);
const char* getfixedNetworkUserRate(int value);
const char* getINmarkingofMS(int value);
const char* getCallAttemptState(int value);
unsigned long Integer(const unsigned char* octets, size_t size);



uint64_t hexBufferToDecimal(const uint8_t* buf, size_t size);
char* BCD(const uint8_t* buffer, size_t size);

#define OUTPUT_BUFFER_SIZE 256
#define GSM_CHAR_COUNT 128
int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <input_file>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *filename = argv[1];

    // Open input file
    FILE *file = fopen(filename, "rb");
    if (file == NULL) {
        return EXIT_FAILURE;
    }

    // Read input file into buffer
    if (fseek(file, 0, SEEK_END) != 0) {
        fclose(file);
        return EXIT_FAILURE;
    }

    long filesize = ftell(file);
    if (filesize == -1) {
        fclose(file);
        return EXIT_FAILURE;
    }

    if (fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        return EXIT_FAILURE;
    }

    void *buffer = malloc(filesize);
    if (buffer == NULL) {
        fclose(file);
        return EXIT_FAILURE;
    }

    size_t read_size = fread(buffer, 1, filesize, file);
    if (read_size != (size_t)filesize) {
        free(buffer);
        fclose(file);
        return EXIT_FAILURE;
    }

    fclose(file);
    uint8_t *current_ptr = buffer;
    size_t remaining_size = filesize;
    int rec_num = 0;

while (remaining_size > 0) {
        CallDataRecord_t *decoded_record = NULL;
        asn_dec_rval_t rval = ber_decode(NULL, &asn_DEF_CallDataRecord, 
                                         (void **)&decoded_record, current_ptr, remaining_size);
        if (rval.code == RC_OK) {
            // printf("\n\nCallDataRecord [%d]\n\n", rec_num);
        processCallDataRecord(decoded_record);
        current_ptr += rval.consumed;
        remaining_size -= rval.consumed;
        ASN_STRUCT_FREE(asn_DEF_CallDataRecord, decoded_record);
        rec_num++;
    } else if (rval.code == RC_WMORE) {
        // fprintf(stderr, "Need more data to decode the record.\n");
        break;
    }
    else{
        current_ptr++;
        remaining_size--;
    }
    // } else {
    //     fprintf(stderr, "Decoding failed at record %d with error code %d.\n", rec_num, rval.code);
    //     if (*current_ptr == 0) {
    //         current_ptr++;
    //         remaining_size--;
    //     } else {
    //         free(buffer);
    //         return EXIT_FAILURE;
    //     }
    // }
    }
    printf("records processed:%d", rec_num); 
    return EXIT_SUCCESS;
}

void decode_tbcd(const uint8_t *data, size_t length, char *output) {
if (length < 1) {
        snprintf(output, 256, "Error: Input data is too short");
        return;
    }

    // Extract TON and NPI from the first byte
    uint8_t first_byte = data[0];
    uint8_t ton = first_byte >> 4;      // High nibble for TON
    uint8_t npi = first_byte & 0x0F;   // Low nibble for NPI

    // Maximum length for decoded digits to ensure no overflow in the output buffer
    size_t max_digits_length = 256 - 32; // Reserve space for "TON=.., NPI=.., Digits=" and null terminator
    char decoded_digits[max_digits_length];
    size_t i, j = 0;

    // Decode the remaining bytes
    for (i = 1; i < length && j < max_digits_length - 1; i++) { // Ensure space for null-termination
        decoded_digits[j++] = '0' + (data[i] & 0x0F);  // Low nibble
        if ((data[i] >> 4) != 0x0F && j < max_digits_length - 1) { // High nibble, avoid padding
            decoded_digits[j++] = '0' + ((data[i] >> 4) & 0x0F);
        }
    }
    decoded_digits[j] = '\0'; // Null-terminate the string

    // Format the final output, ensuring no overflow
    snprintf(output, 256, "TON=%d, NPI=%d, Digits=%s", ton, npi, decoded_digits);

}
char* decode_LocationInformation(const unsigned char* contents, size_t size) {
    // Check if the size is sufficient for decoding
    if (size < 7) {
        return "";
    }

    static char result[64]; // Result buffer

    // Decode MCC (Mobile Country Code)
    int dig1 = contents[0] & 0x0F;
    int dig2 = contents[0] >> 4;
    int dig3 = contents[1] & 0x0F;
    char mcc[4];
    snprintf(mcc, sizeof(mcc), "%X%X%X", dig1, dig2, dig3);

    // Decode MNC (Mobile Network Code)
    dig1 = contents[2] & 0x0F;
    dig2 = contents[2] >> 4;
    dig3 = contents[1] >> 4;
    char mnc[4];
    snprintf(mnc, sizeof(mnc), "%X%X", dig1, dig2);
    if (dig3 != 0x0F) { // Include the third digit if it's not padding
        char temp[2];
        snprintf(temp, sizeof(temp), "%X", dig3);
        strncat(mnc, temp, sizeof(mnc) - strlen(mnc) - 1);
    }

    // Decode LAC (Location Area Code)
    int lac = contents[3] * 256 + contents[4];

    // Decode SAC (Service Area Code)
    int sac = contents[5] * 256 + contents[6];

    // Format the result
    snprintf(result, sizeof(result), "MCC=%s, MNC=%s, LAC=%d, SAC=%d", mcc, mnc, lac, sac);

    return result;
}
char* buffer_to_hex(const uint8_t* buf, size_t size) {
    if (!buf || size == 0) {
        return strdup("(empty)"); // Return a placeholder for empty or null buffers.
    }

    // Allocate enough space for the hexadecimal string (2 chars per byte + null terminator).
    size_t hex_len = size * 2 + 1;
    char* hex_string = (char*)malloc(hex_len);
    if (!hex_string) {
        return NULL;
    }

    // Convert each byte to its hexadecimal representation.
    for (size_t i = 0; i < size; i++) {
        sprintf(hex_string + (i * 2), "%02X", buf[i]);
    }

    hex_string[hex_len - 1] = '\0'; // Null-terminate the string.
    return hex_string;
}

void process_umts_gsm_record(const UMTSGSMPLMNCallDataRecord_t *record) {
    if (!record) return;
    // printf("Processing CallDataRecord\n");
    switch (record->callDataRecord.present) {
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_mSTerminatingSMSinMSC:
            process_ms_mSTerminatingSMSinMSC(&record->callDataRecord.choice.mSTerminatingSMSinMSC);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_mSOriginating:
            process_ms_mSOriginating(&record->callDataRecord.choice.mSOriginating);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_callForwarding:
            process_callForwarding(&record->callDataRecord.choice.callForwarding);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_roamingCallForwarding:
            process_roamingCallForwarding(&record->callDataRecord.choice.roamingCallForwarding);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_mSTerminating:
            process_mSTerminating(&record->callDataRecord.choice.mSTerminating);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_mSTerminatingSMSinSMS_GMSC:
            process_msTerminatingSMSinSMSGMSC(&record->callDataRecord.choice.mSTerminatingSMSinSMS_GMSC);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_mSOriginatingSMSinMSC:
            process_msOriginatingSMSinMSC(&record->callDataRecord.choice.mSOriginatingSMSinMSC);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_mSOriginatingSMSinSMS_IWMSC:
            process_msOriginatingSMSinSMSIWMSC(&record->callDataRecord.choice.mSOriginatingSMSinSMS_IWMSC);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_sSProcedure:
            process_ssProcedure(&record->callDataRecord.choice.sSProcedure);
            return;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_transit:
            process_transit(&record->callDataRecord.choice.transit);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_iNIncomingCall:
            process_inIncomingCall(&record->callDataRecord.choice.iNIncomingCall);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_iNOutgoingCall:
            process_inOutgoingCall(&record->callDataRecord.choice.iNOutgoingCall);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_iSDNOriginating:
            process_isdnOriginating(&record->callDataRecord.choice.iSDNOriginating);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_iSDNCallForwarding:
            process_isdnCallForwarding(&record->callDataRecord.choice.iSDNCallForwarding);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_iSDNSSProcedure:
            process_isdnSSProcedure(&record->callDataRecord.choice.iSDNSSProcedure);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_sCFChargingOutput:
            process_scfChargingOutput(&record->callDataRecord.choice.sCFChargingOutput);
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_locationServices: 
            process_locationServices(&record->callDataRecord.choice.locationServices);
            break; 
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_NOTHING:
            break;
        case UMTSGSMPLMNCallDataRecord__callDataRecord_PR_transitINOutgoingCall:
            process_transitINOutgoingCall(&record->callDataRecord.choice.transitINOutgoingCall);
            break;
    }
}
void processCallDataRecord(const CallDataRecord_t *record){
    if (!record) return;
    switch (record->present) {
        case CallDataRecord_PR_uMTSGSMPLMNCallDataRecord:
            process_umts_gsm_record(&record->choice.uMTSGSMPLMNCallDataRecord);
            break;
        case CallDataRecord_PR_compositeCallDataRecord:
            for (int i = 0; i < record->choice.compositeCallDataRecord.list.count; i++) {
                UMTSGSMPLMNCallDataRecord_t *callData = record->choice.compositeCallDataRecord.list.array[i];
                if (callData->callDataRecord.present) {
                    process_umts_gsm_record(callData);
                    break;
                }
            }
            break;
    }
}

char* BCD(const uint8_t* buffer, size_t size) {
    if (size < 3) {
        return strdup("Invalid input"); 
    }
    char* output = (char*)malloc(20 * sizeof(char)); // Enough for "HH:MM:SS.ms"
    if (!output) {
        return strdup("Memory error");
    }

    // Extract hours, minutes, and seconds
    int hh = buffer[0];  // Hour
    int mm = buffer[1];  // Minute
    int ss = buffer[2];  // Second

    // Format the time
    if (size == 4) { // With milliseconds
        int ms = buffer[3]; // Milliseconds
        snprintf(output, 20, "%02d:%02d:%02d.%d", hh, mm, ss, ms);
    } else { // Without milliseconds
        snprintf(output, 20, "%02d:%02d:%02d", hh, mm, ss);
    }

    return output; // Return the formatted string
}

uint64_t hexBufferToDecimal(const uint8_t* buf, size_t size) {
    uint64_t decimalValue = 0;

    // Process each byte in the buffer
    for (size_t i = 0; i < size; i++) {
        decimalValue = (decimalValue << 8) | buf[i]; // Shift left and add current byte
    }

    return decimalValue;
}

char GSMCHAR[GSM_CHAR_COUNT];

void decode_gsm(const uint8_t *data, size_t length, char *output) {
    size_t i, nbits = 0;
    uint8_t remain = 0;
    size_t j = 0;
    size_t max_decoded_length = OUTPUT_BUFFER_SIZE - 32; // Leave space for formatting

    for (i = 0; i < length; i++) {
        uint8_t out = ((data[i] << nbits) + remain) & 0x7F;
        if (j < max_decoded_length - 1) output[j++] = GSMCHAR[out];
        nbits = (nbits + 1) % 7;
        remain = data[i] >> (8 - nbits);

        if (nbits == 0 && j < max_decoded_length - 1) {
            out = data[i] >> 1;
            output[j++] = GSMCHAR[out];
        }

        if (j >= max_decoded_length - 1) break; // Prevent overflow
    }
    output[j] = '\0'; // Null-terminate
}


void decode_address_string_extended(const uint8_t *data, size_t length, char *output) {
    if (length < 2) {
        snprintf(output, OUTPUT_BUFFER_SIZE, "Error: Input data is too short");
        return;
    }

    uint8_t first_byte = data[0];
    uint8_t ton = first_byte >> 4;
    uint8_t npi = first_byte & 0x0F;

    char decoded[OUTPUT_BUFFER_SIZE - 32] = {0}; // Limit decoded size
    if (ton == 14) {
        decode_gsm(data + 1, length - 1, decoded);
    } else {
        decode_tbcd(data, length, decoded);
    }

    // Safeguard against truncation
    if (strlen(decoded) > OUTPUT_BUFFER_SIZE - 32) {
        decoded[OUTPUT_BUFFER_SIZE - 33] = '\0';
    }

    snprintf(output, OUTPUT_BUFFER_SIZE, "TON=%d, NPI=%d, Digits=%s", ton, npi, decoded);

}

char* decode_LocationInformationExtension(const unsigned char* contents, size_t size) {
    // Check if the size is sufficient for decoding
    if (size == 0) {
        return "Error: Input size too small for decoding.";
    }

    static char result[64]; // Result buffer

    // Make a copy of the input and mask the first octet
    unsigned char octets[size];
    for (size_t i = 0; i < size; ++i) {
        octets[i] = contents[i];
    }
    octets[0] &= 0x0F; // Mask the first octet to keep only the lower nibble

    // Convert the octets into an integer
    unsigned long cellId = Integer(octets, size);

    // Format the result
    snprintf(result, sizeof(result), "E-UTRAN Cell Id=%lu", cellId);

    return result;
}





void process_ms_mSTerminatingSMSinMSC(const MSTerminatingSMSinMSC_t *record) {
    if(record == NULL) {
        return;
    }

    // Buffers for decoded data
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
printf("msterminatingsmsinmsc;");
if (record->tAC) {
    uint64_t hex_result = hexBufferToDecimal(record->tAC->buf,record->tAC->size);
    printf("%ld;", hex_result);
}
if (record->callIdentificationNumber) {
    uint64_t decimalValue = hexBufferToDecimal(record->callIdentificationNumber->buf,record->callIdentificationNumber->size);
    printf("%lu;", decimalValue);
}
if (record->recordSequenceNumber) {
    uint64_t decimalValue = hexBufferToDecimal(record->recordSequenceNumber->buf,record->recordSequenceNumber->size);
    printf("%lu;", decimalValue);
}
if (record->calledPartyNumber) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->calledPartyNumber->buf, record->calledPartyNumber->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}
if (record->calledSubscriberIMSI) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->calledSubscriberIMSI->buf, record->calledSubscriberIMSI->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}
if (record->calledSubscriberIMEI) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->calledSubscriberIMEI->buf, record->calledSubscriberIMEI->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}
if (record->dateForStartOfCharge) {
    char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf,record->dateForStartOfCharge->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->timeForStartOfCharge) {
    char* hex_result = BCD(record->timeForStartOfCharge->buf,record->timeForStartOfCharge->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->originForCharging) {
    char* hex_result = buffer_to_hex(record->originForCharging->buf,record->originForCharging->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->chargedParty) {
    if (record->chargedParty != NULL) {
        printf("%s;", getChargedparty(*record->chargedParty));
        } else {
            printf(";");
    }
}
if (record->exchangeIdentity) {
    printf("%s;", record->exchangeIdentity->buf);
}
if (record->mSCIdentification) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->mSCIdentification->buf, record->mSCIdentification->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}
if(record->outgoingRoute){
    printf("%s;",record->outgoingRoute->buf);
}
if (record->firstCalledLocationInformation) {
    char* hex_result = decode_LocationInformation(record->firstCalledLocationInformation->buf,record->firstCalledLocationInformation->size);
    printf("%s;", hex_result);
}
if (record->teleServiceCode) {
    char* hex_result = buffer_to_hex(record->teleServiceCode->buf,record->teleServiceCode->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->serviceCentreAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->serviceCentreAddress->buf, record->serviceCentreAddress->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}
if (record->iCIOrdered) {
    printf("%ls;", record->iCIOrdered);
}
if (record->outputForSubscriber) {
    printf("%ln;", record->outputForSubscriber);
}
if (record->miscellaneousInformation) {
    char* hex_result = buffer_to_hex(record->miscellaneousInformation->buf,record->miscellaneousInformation->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->regionalServiceUsed) {
    printf("%ln;", record->regionalServiceUsed);
}
if (record->regionDependentChargingOrigin) {
    char* hex_result = buffer_to_hex(record->regionDependentChargingOrigin->buf,record->regionDependentChargingOrigin->size);
    printf("%s; ", hex_result);
    free(hex_result);
}
if (record->channelAllocationPriorityLevel) {
    printf("%s;", record->channelAllocationPriorityLevel->buf);
}
if (record->incompleteCallDataIndicator) {
    printf("%ls; ", record->incompleteCallDataIndicator);
}
if (record->restartDuringOutputIndicator) {
    printf("%ls;", record->restartDuringOutputIndicator);
}
if (record->frequencyBandSupported) {
    char* hex_result = buffer_to_hex(record->frequencyBandSupported->buf,record->frequencyBandSupported->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->forloppDuringOutputIndicator) {
    printf("%ls;", record->forloppDuringOutputIndicator);
}
if (record->numberOfShortMessages){
    uint64_t decimalValue = hexBufferToDecimal(record->numberOfShortMessages->buf,record->numberOfShortMessages->size);
    printf("%lu;", decimalValue);
}
if (record->lastCalledLocationInformation){
    char* hex_result = decode_LocationInformation(record->lastCalledLocationInformation->buf,record->lastCalledLocationInformation->size);
    printf("%s;", hex_result);
}
if (record->positionAccuracy) {
    char* hex_result = buffer_to_hex(record->positionAccuracy->buf,record->positionAccuracy->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->userTerminalPosition) {
    char* hex_result = buffer_to_hex(record->userTerminalPosition->buf,record->userTerminalPosition->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->switchIdentity) {
    char* hex_result = buffer_to_hex(record->switchIdentity->buf,record->switchIdentity->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->originatingAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_address_string_extended(record->originatingAddress->buf, record->originatingAddress->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}
if (record->messageTypeIndicator) {
    if (record->messageTypeIndicator != NULL) {
        printf("%s;", getMessageTypeindicator(*record->messageTypeIndicator));
        } else {
            printf(";");
    }
}
if (record->rNCidOfFirstRNC) {
    char* hex_result = buffer_to_hex(record->rNCidOfFirstRNC->buf,record->rNCidOfFirstRNC->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->bCSMTDPData1) {
    char* hex_result = buffer_to_hex(record->bCSMTDPData1->serviceKey.buf,record->bCSMTDPData1->serviceKey.size);
    printf("%s;", hex_result);
    char* hex_result2 = buffer_to_hex(record->bCSMTDPData1->gsmSCFAddress.buf,record->bCSMTDPData1->gsmSCFAddress.size);
    printf("%s;", hex_result2);
    free(hex_result);
}
if (record->defaultSMSHandling) {
    printf("%ln;", record->defaultSMSHandling);
}
if (record->freeFormatData) {
    char* hex_result = buffer_to_hex(record->freeFormatData->buf,record->freeFormatData->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->sMSResult) {
    char* hex_result = buffer_to_hex(record->sMSResult->buf,record->sMSResult->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->sMSReferenceNumber) {
    char* hex_result = buffer_to_hex(record->sMSReferenceNumber->buf,record->sMSReferenceNumber->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->mSCAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->mSCAddress->buf, record->mSCAddress->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}
if (record->cAMELOriginatingAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_address_string_extended(record->mSCAddress->buf, record->mSCAddress->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}
if (record->calledSubscriberIMEISV) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->calledSubscriberIMEISV->buf, record->calledSubscriberIMEISV->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}
if (record->rTCIndicator) {
    printf(" %ls;", record->rTCIndicator);
}
if (record->rTCSessionID) {
    char* hex_result = buffer_to_hex(record->rTCSessionID->buf,record->rTCSessionID->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->rTCDefaultServiceHandling) {
    printf("%ln;", record->rTCDefaultServiceHandling);
}
if (record->rTCFailureIndicator) {
    char* hex_result = buffer_to_hex(record->rTCFailureIndicator->buf,record->rTCFailureIndicator->size);
    printf(" %s;", hex_result);
    free(hex_result);
}
if (record->rTCNotInvokedReason) {
    printf("%ln;", record->rTCNotInvokedReason);
}
if (record->bladeID) {
    char* hex_result = buffer_to_hex(record->bladeID->buf,record->bladeID->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->buddyBladeIndicator) {
    printf("%ls;", record->buddyBladeIndicator);
}
if (record->trafficIsolationIndicator) {
    printf("%ls;", record->trafficIsolationIndicator);
}
if (record->firstCalledLocationInformationExtension) {
    char* hex_result = decode_LocationInformationExtension(record->firstCalledLocationInformationExtension->buf,record->firstCalledLocationInformationExtension->size);
    printf("%s;", hex_result);
}
if (record->lastCalledLocationInformationExtension) {
    char* hex_result = decode_LocationInformationExtension(record->lastCalledLocationInformationExtension->buf,record->lastCalledLocationInformationExtension->size);
    printf("%s;", hex_result);
}
if (record->subscriptionType) {
    printf(" %s;", record->subscriptionType->buf);
}
if (record->outputType) {
    if (record->outputType != NULL) {
        printf(" %s;", getOutputType(*record->outputType));
        } else {
            printf(";");
    }
}
if (record->ccbsCallIndicator) {
    char* hex_result = buffer_to_hex(record->ccbsCallIndicator->buf,record->ccbsCallIndicator->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->subscriptionType){
    char* hex_result = buffer_to_hex(record->subscriptionType->buf,record->subscriptionType->size);
    printf("%s;", hex_result);
    free(hex_result);
}
    // Print the updated record using xer_fprint
    // xer_fprint(stdout, &asn_DEF_MSTerminatingSMSinMSC, record);
}


void process_callForwarding(const CallForwarding_t *record){
    if (record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];

    printf(";");
    // tAC
    if (record->tAC) {
        uint64_t hex_result = hexBufferToDecimal(record->tAC->buf,record->tAC->size);
        printf("%ld;", hex_result);
    }

    // callIdentificationNumber
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("%ld;", hex_result);
    }

    // recordSequenceNumber
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("%ld;", hex_result);
    }

    // typeOfCallingSubscriber
    if (record->typeOfCallingSubscriber) {
        uint64_t hex_result = hexBufferToDecimal(record->typeOfCallingSubscriber->buf, record->typeOfCallingSubscriber->size);
        printf("%ld;", hex_result);
    }

    // callingPartyNumber
    if (record->callingPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingPartyNumber->buf, record->callingPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }

    // calledPartyNumber
    if (record->calledPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->calledPartyNumber->buf, record->calledPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }

    // originalCalledNumber
    if (record->originalCalledNumber) {
        printf("%s;", record->originalCalledNumber->buf);
    }

    // redirectingNumber
    if (record->redirectingNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->redirectingNumber->buf, record->redirectingNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }

    // redirectionCounter
    if (record->redirectionCounter) {
        uint64_t hex_result = hexBufferToDecimal(record->redirectionCounter->buf, record->redirectionCounter->size);
        printf("%ld;", hex_result);
    }

    // redirectingSPN
    if (record->redirectingSPN) {
        printf("%s;", record->redirectingSPN->buf);
    }

    // redirectingIMSI
    if (record->redirectingIMSI) {
        printf("%s;", record->redirectingIMSI->buf);
    }

    // mobileStationRoamingNumber
    if (record->mobileStationRoamingNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mobileStationRoamingNumber->buf, record->mobileStationRoamingNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }

    // disconnectingParty
    if (record->disconnectingParty) {
        if (record->disconnectingParty != NULL) {
        printf("%s;", getDisconnectingParty(*record->disconnectingParty));
        } else {
            printf(";");
        }
    }

    // dateForStartOfCharge
    if (record->dateForStartOfCharge) {
        char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf, record->dateForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    // timeForStartOfCharge
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf, record->timeForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    // timeForStopOfCharge
    if (record->timeForStopOfCharge) {
        char* hex_result = BCD(record->timeForStopOfCharge->buf, record->timeForStopOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    // chargeableDuration
    if (record->chargeableDuration) {
        char* hex_result = BCD(record->chargeableDuration->buf, record->chargeableDuration->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    // interruptionTime
    if (record->interruptionTime) {
        char* hex_result = BCD(record->interruptionTime->buf, record->interruptionTime->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    // timeFromRegisterSeizureToStartOfCharging
    if (record->timeFromRegisterSeizureToStartOfCharging) {
        char* hex_result = BCD(record->timeFromRegisterSeizureToStartOfCharging->buf, record->timeFromRegisterSeizureToStartOfCharging->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    // chargedParty
    if (record->chargedParty) {
         if (record->chargedParty != NULL) {
        printf("%s;", getChargedparty(*record->chargedParty));
        } else {
            printf(";");
        }
    }

    // originForCharging
    if (record->originForCharging) {
        char* hex_result = buffer_to_hex(record->originForCharging->buf, record->originForCharging->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    // tariffClass
    if (record->tariffClass) {
        uint64_t hex_result = hexBufferToDecimal(record->tariffClass->buf, record->tariffClass->size);
        printf("%ld;", hex_result);
    }

    // tariffSwitchInd
    if (record->tariffSwitchInd) {
        if (record->tariffSwitchInd != NULL) {
        printf("%s;", getTariffSwitchInd(*record->tariffSwitchInd));
        } else {
            printf(";");
        }
    }

    // exchangeIdentity
    if (record->exchangeIdentity) {
        printf("%s;", record->exchangeIdentity->buf);
    }

    // mSCIdentification
    if (record->mSCIdentification) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCIdentification->buf, record->mSCIdentification->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }

    // outgoingRoute
    if (record->outgoingRoute) {
        printf("%s;", record->outgoingRoute->buf);
    }

    // incomingRoute
    if (record->incomingRoute) {
        printf("%s;", record->incomingRoute->buf);
    }

    // miscellaneousInformation
    if (record->miscellaneousInformation) {
        printf("%s;", record->miscellaneousInformation->buf);
    }

    // originatingLocationNumber
    if (record->originatingLocationNumber) {
        printf("%s;", record->originatingLocationNumber->buf);
    }

    // callPosition
    if (record->callPosition) {
        if (record->callPosition != NULL) {
        printf("%s;", getCallPositionString(*record->callPosition));
        } else {
            printf(";");
        }
    }

    // eosInfo
    if (record->eosInfo) {
        printf("%s;", record->eosInfo->buf);
    }

    // internalCauseAndLoc
    if (record->internalCauseAndLoc) {
        printf("%s;", record->internalCauseAndLoc->buf);
    }

    // restartDuringCall
    if (record->restartDuringCall) {
        printf("%ls;", record->restartDuringCall);
    }

    // restartDuringOutputIndicator
    if (record->restartDuringOutputIndicator) {
        printf("%ls;", record->restartDuringOutputIndicator);
    }

    // numberOfMeterPulses
    if (record->numberOfMeterPulses) {
        printf("%s;", record->numberOfMeterPulses->buf);
    }

    // c7ChargingMessage
    if (record->c7ChargingMessage) {
        printf("%s;", record->c7ChargingMessage->buf);
    }

    // c7FirstCHTMessage
    if (record->c7FirstCHTMessage) {
        printf("%s;", record->c7FirstCHTMessage->buf);
    }

    // c7SecondCHTMessage
    if (record->c7SecondCHTMessage) {
        printf("%s;", record->c7SecondCHTMessage->buf);
    }

    // iCIOrdered
    if (record->iCIOrdered) {
        printf("%ls;", record->iCIOrdered);
    }

    // outputForSubscriber
    if (record->outputForSubscriber) {
        printf("%ln;", record->outputForSubscriber);
    }

    // iNMarkingOfMS
    if (record->iNMarkingOfMS) {
        if (record->iNMarkingOfMS != NULL) {
        printf("%s;", getINmarkingofMS(*record->iNMarkingOfMS));
        } else {
            printf(";");
        }
    }

    // lastPartialOutput
    if (record->lastPartialOutput) {
        printf("%ls;", record->lastPartialOutput);
    }

    // partialOutputRecNum
    if (record->partialOutputRecNum) {
        printf("%s;", record->partialOutputRecNum->buf);
    }

    // relatedCallNumber
    if (record->relatedCallNumber) {
        char* hex_result = buffer_to_hex(record->relatedCallNumber->buf, record->relatedCallNumber->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    // cUGInterlockCode
    if (record->cUGInterlockCode) {
        printf("%s;", record->cUGInterlockCode->buf);
    }

    // cUGIndex
    if (record->cUGIndex) {
        printf("%s;", record->cUGIndex->buf);
    }

    // cUGOutgoingAccessUsed
    if (record->cUGOutgoingAccessUsed) {
        printf("%ls;", record->cUGOutgoingAccessUsed);
    }

    // cUGOutgoingAccessIndicator
    if (record->cUGOutgoingAccessIndicator) {
        printf("%ls;", record->cUGOutgoingAccessIndicator);
    }
g
    // regionalServiceUsed
    if (record->regionalServiceUsed) {
        printf("%ln;", record->regionalServiceUsed);
    }

    // regionDependentChargingOrigin
    if (record->regionDependentChargingOrigin) {
        printf("%s;", record->regionDependentChargingOrigin->buf);
    }

    // presentationAndScreeningIndicator
    if (record->presentationAndScreeningIndicator) {
        uint64_t hex_result = hexBufferToDecimal(record->presentationAndScreeningIndicator->buf, record->presentationAndScreeningIndicator->size);
        printf("%ld;", hex_result);
    }

    // faultCode
    if (record->faultCode) {
        printf("%s;", record->faultCode->buf);
    }

    // subscriptionType
    if (record->subscriptionType) {
        printf("%s;", record->subscriptionType->buf);
    }

    // incompleteCallDataIndicator
    if (record->incompleteCallDataIndicator) {
        printf("%ls;", record->incompleteCallDataIndicator);
    }

    // incompleteCompositeCDRIndicator
    if (record->incompleteCompositeCDRIndicator) {
        printf("%ls;", record->incompleteCompositeCDRIndicator);
    }

    // switchIdentity
    if (record->switchIdentity) {
        char* hex_result = buffer_to_hex(record->switchIdentity->buf, record->switchIdentity->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    // networkCallReference
    if (record->networkCallReference) {
        printf("%s;", record->networkCallReference->buf);
    }

    // disconnectionDueToSystemRecovery
    if (record->disconnectionDueToSystemRecovery) {
        printf("%ls;", record->disconnectionDueToSystemRecovery);
    }

    // forloppDuringOutputIndicator
    if (record->forloppDuringOutputIndicator) {
        printf("%ls;", record->forloppDuringOutputIndicator);
    }

    // forloppReleaseDuringCall
    if (record->forloppReleaseDuringCall) {
        printf("%ls;", record->forloppReleaseDuringCall);
    }

    // translatedNumber
    if (record->translatedNumber) {
        printf("%s;", record->translatedNumber->buf);
    }

    // cAMELInitiatedCallForwarding
    if (record->cAMELInitiatedCallForwarding) {
        printf("%ls;", record->cAMELInitiatedCallForwarding);
    }

    // bCSMTDPData1
    if (record->bCSMTDPData1) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData1->serviceKey.buf,record->bCSMTDPData1->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData1->gsmSCFAddress.buf,record->bCSMTDPData1->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData2
    if (record->bCSMTDPData2) {
                char* hex_result = buffer_to_hex(record->bCSMTDPData2->serviceKey.buf,record->bCSMTDPData2->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData2->gsmSCFAddress.buf,record->bCSMTDPData2->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData3
    if (record->bCSMTDPData3) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData3->serviceKey.buf,record->bCSMTDPData3->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData3->gsmSCFAddress.buf,record->bCSMTDPData3->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData4
    if (record->bCSMTDPData4) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData4->serviceKey.buf,record->bCSMTDPData4->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData4->gsmSCFAddress.buf,record->bCSMTDPData4->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData5
    if (record->bCSMTDPData5) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData5->serviceKey.buf,record->bCSMTDPData5->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData5->gsmSCFAddress.buf,record->bCSMTDPData5->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData6
    if (record->bCSMTDPData6) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData6->serviceKey.buf,record->bCSMTDPData6->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData6->gsmSCFAddress.buf,record->bCSMTDPData6->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData7
    if (record->bCSMTDPData7) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData7->serviceKey.buf,record->bCSMTDPData7->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData7->gsmSCFAddress.buf,record->bCSMTDPData7->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData8
    if (record->bCSMTDPData8) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData8->serviceKey.buf,record->bCSMTDPData8->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData8->gsmSCFAddress.buf,record->bCSMTDPData8->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }
    // bCSMTDPData9
    if (record->bCSMTDPData9) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData9->serviceKey.buf,record->bCSMTDPData9->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData9->gsmSCFAddress.buf,record->bCSMTDPData9->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData10
    if (record->bCSMTDPData10) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData10->serviceKey.buf,record->bCSMTDPData10->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData10->gsmSCFAddress.buf,record->bCSMTDPData10->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // gSMCallReferenceNumber
    if (record->gSMCallReferenceNumber) {
    char* hex_result = buffer_to_hex(record->gSMCallReferenceNumber->buf, record->gSMCallReferenceNumber->size);
    printf("%s;", hex_result);
    free(hex_result);
    }

    // mSCAddress
    if (record->mSCAddress) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCAddress->buf, record->mSCAddress->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }

    // aCMChargingIndicator
    if (record->aCMChargingIndicator) {
        printf("%s;", record->aCMChargingIndicator->buf);
    }

    // aNMChargingIndicator
    if (record->aNMChargingIndicator) {
        printf("%s;", record->aNMChargingIndicator->buf);
    }

    // carrierInformationBackward
    if (record->carrierInformationBackward) {
        printf("%s;", record->carrierInformationBackward->buf);
    }

    // chargeInformation
    if (record->chargeInformation) {
        printf("%s;", record->chargeInformation->buf);
    }

    // disconnectionDate
    if (record->disconnectionDate) {
        printf("%s;", record->disconnectionDate->buf);
    }

    // disconnectionTime
    if (record->disconnectionTime) {
        char* hex_result = BCD(record->disconnectionTime->buf, record->disconnectionTime->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
// exitPOICA
    if (record->exitPOICA) {
        printf("%s;", record->exitPOICA->buf);
    }

    // originatingCarrier
    if (record->originatingCarrier) {
        printf("%s;", record->originatingCarrier->buf);
    }

    // originatingChargeArea
    if (record->originatingChargeArea) {
        printf("%s;", record->originatingChargeArea->buf);
    }

    // terminatingAccessISDN
    if (record->terminatingAccessISDN) {
        printf("%ls;", record->terminatingAccessISDN);
    }

    // terminatingCarrier
    if (record->terminatingCarrier) {
        printf("%s;", record->terminatingCarrier->buf);
    }

    // terminatingChargeArea
    if (record->terminatingChargeArea) {
        printf("%s;", record->terminatingChargeArea->buf);
    }

    // terminatingMobileUserClass1
    if (record->terminatingMobileUserClass1) {
        printf("%s;", record->terminatingMobileUserClass1->buf);
    }

    // terminatingMobileUserClass2
    if (record->terminatingMobileUserClass2) {
        printf("%s;", record->terminatingMobileUserClass2->buf);
    }

    // terminatingUserClass
    if (record->terminatingUserClass) {
        printf("%s;", record->terminatingUserClass->buf);
    }

    // originatingAccessISDN
    if (record->originatingAccessISDN) {
        printf("%ls;", record->originatingAccessISDN);
    }

    // contractorNumber
    if (record->contractorNumber) {
        printf("%s;", record->contractorNumber->buf);
    }

    // calledPartyMNPInfo
    if (record->calledPartyMNPInfo) {
        printf("%s;", record->calledPartyMNPInfo->buf);
    }

    // carrierIdentificationCode
    if (record->carrierIdentificationCode) {
        printf("%s;", record->carrierIdentificationCode->buf);
    }

    // carrierInformation
    if (record->carrierInformation) {
        printf("%s;", record->carrierInformation->buf);
    }

    // carrierSelectionSubstitutionInformation
    if (record->carrierSelectionSubstitutionInformation) {
        printf("%s;", record->carrierSelectionSubstitutionInformation->buf);
    }

    // chargeNumber
    if (record->chargeNumber) {
        printf("%s;", record->chargeNumber->buf);
    }

    // interExchangeCarrierIndicator
    if (record->interExchangeCarrierIndicator) {
        printf("%ls;", record->interExchangeCarrierIndicator);
    }

    // originatingLineInformation
    if (record->originatingLineInformation) {
        printf("%s;", record->originatingLineInformation->buf);
    }

    // optimalRoutingType
    if (record->optimalRoutingType) {
        printf("%ln;", record->optimalRoutingType);
    }

    // optimalRoutingInvocationFailed
    if (record->optimalRoutingInvocationFailed) {
        printf("%ls;", record->optimalRoutingInvocationFailed);
    }

    // userToUserInformation
    if (record->userToUserInformation) {
        printf("%s;", record->userToUserInformation->buf);
    }

    // outputType
    if (record->outputType) {
        if (record->outputType != NULL) {
        printf("%s;", getOutputType(*record->outputType));
        } else {
            printf(";");
    }
    }

    // multimediaInformation
    if (record->multimediaInformation) {
        printf("%ln;", record->multimediaInformation->userRate);
    }

    // globalCallReference
    if (record->globalCallReference) {
        printf("%s;", record->globalCallReference->buf);
    }

    // rTCIndicator
    if (record->rTCIndicator) {
        printf("%ls;", record->rTCIndicator);
    }

    // rTCSessionID
    if (record->rTCSessionID) {
        printf("%s;", record->rTCSessionID->buf);
    }

    // rTCDefaultServiceHandling
    if (record->rTCDefaultServiceHandling) {
        printf("%ln;", record->rTCDefaultServiceHandling);
    }

    // rTCFailureIndicator
    if (record->rTCFailureIndicator) {
        printf("%s;", record->rTCFailureIndicator->buf);
    }

    // rTCNotInvokedReason
    if (record->rTCNotInvokedReason) {
        printf("%ln;", record->rTCNotInvokedReason);
    }

    // calledDirectoryNumber
    if (record->calledDirectoryNumber) {
        printf("%s;", record->calledDirectoryNumber->buf);
    }

    // outgoingPChargingVector
    if (record->outgoingPChargingVector) {
        printf("%s;", record->outgoingPChargingVector->buf);
    }

    // bladeID
    if (record->bladeID) {
        char* hex_result = buffer_to_hex(record->bladeID->buf, record->bladeID->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    // buddyBladeIndicator
    if (record->buddyBladeIndicator) {
        printf("%ls;", record->buddyBladeIndicator);
    }

    // trafficIsolationIndicator
    if (record->trafficIsolationIndicator) {
        printf("%ls;", record->trafficIsolationIndicator);
    }

    // ccbsCallIndicator
    if (record->ccbsCallIndicator) {
        printf("%s;", record->ccbsCallIndicator->buf);
    }

    // firstCallingLocationInformation
    if (record->firstCallingLocationInformation) {
        char* hex_result = decode_LocationInformation(record->firstCallingLocationInformation->buf, record->firstCallingLocationInformation->size);
        printf("%s;", hex_result);
    }

    // teleServiceCode
    if (record->teleServiceCode) {
        char* hex_result = buffer_to_hex(record->teleServiceCode->buf, record->teleServiceCode->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    // bearerServiceCode
    if (record->bearerServiceCode) {
        printf("%s;", record->bearerServiceCode->buf);
    }
}

void process_ms_mSOriginating(const MSOriginating_t *record){
    if(record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];

    printf(";");

if (record->tAC) {
        uint64_t hex_result = hexBufferToDecimal(record->tAC->buf,record->tAC->size);
        printf("%ld;", hex_result);
    }
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->typeOfCallingSubscriber) {
        uint64_t hex_result = hexBufferToDecimal(record->typeOfCallingSubscriber->buf, record->typeOfCallingSubscriber->size);
        printf("%ld;", hex_result);
    }
    if (record->callingPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingPartyNumber->buf, record->callingPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->callingSubscriberIMSI) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingSubscriberIMSI->buf, record->callingSubscriberIMSI->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->callingSubscriberIMEI) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingSubscriberIMEI->buf, record->callingSubscriberIMEI->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->calledPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->calledPartyNumber->buf, record->calledPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->disconnectingParty) {
        // char* hex_result = buffer_to_hex(record->disconnectingParty->buf, record->disconnectingParty->size);
        // printf("%s;", hex_result);
        if (record->disconnectingParty != NULL) {
        printf("%s;", getDisconnectingParty(*record->disconnectingParty));
        } else {
            printf(";");
        }
    }
    if (record->dateForStartOfCharge) {
        char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf, record->dateForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf, record->timeForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeForStopOfCharge) {
        char* hex_result = BCD(record->timeForStopOfCharge->buf, record->timeForStopOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->chargeableDuration) {
        char* hex_result = BCD(record->chargeableDuration->buf, record->chargeableDuration->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->interruptionTime) {
        char* hex_result = BCD(record->interruptionTime->buf, record->interruptionTime->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeFromRegisterSeizureToStartOfCharging) {
        char* hex_result = BCD(record->timeFromRegisterSeizureToStartOfCharging->buf, record->timeFromRegisterSeizureToStartOfCharging->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->chargedParty) {
        // char* hex_result = buffer_to_hex(record->chargedParty->buf, record->chargedParty->size);
        // printf("%s;", hex_result);
        if (record->chargedParty != NULL) {
        printf("%s;", getChargedparty(*record->chargedParty));
        } else {
            printf(";");
        }
    }
    if (record->originForCharging) {
        char* hex_result = buffer_to_hex(record->originForCharging->buf, record->originForCharging->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->chargingCase) {
        uint64_t hex_result = hexBufferToDecimal(record->chargingCase->buf, record->chargingCase->size);
        printf("%ld;", hex_result);
    }
    if (record->tariffClass) {
        uint64_t hex_result = hexBufferToDecimal(record->tariffClass->buf, record->tariffClass->size);
        printf("%ld;", hex_result);
    }
    if (record->tariffSwitchInd) {
        // char* hex_result = buffer_to_hex(record->tariffSwitchInd->buf, record->tariffSwitchInd->size);
        // printf("%s;", hex_result);
        if (record->tariffSwitchInd != NULL) {
        printf("%s;", getTariffSwitchInd(*record->tariffSwitchInd));
        } else {
            printf(";");
        }
    }
    if (record->exchangeIdentity) {
        printf("%s;", record->exchangeIdentity->buf);
    }
    if (record->mSCIdentification) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCIdentification->buf, record->mSCIdentification->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->outgoingRoute) {
        printf("%s;", record->outgoingRoute->buf);
    }
    if (record->incomingRoute) {
        printf("%s;", record->incomingRoute->buf);
    }
    if (record->miscellaneousInformation) {
    printf("%s;", record->miscellaneousInformation->buf);
    }
    if (record->originatingLocationNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->originatingLocationNumber->buf, record->originatingLocationNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->timeForTCSeizureCalling) {
        char* hex_result = BCD(record->timeForTCSeizureCalling->buf, record->timeForTCSeizureCalling->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->firstCallingLocationInformation) {
        char* hex_result = decode_LocationInformation(record->firstCallingLocationInformation->buf, record->firstCallingLocationInformation->size);
        printf("%s;", hex_result);
    }
    if (record->lastCallingLocationInformation) {
        char* hex_result = decode_LocationInformation(record->lastCallingLocationInformation->buf, record->lastCallingLocationInformation->size);
        printf("%s;", hex_result);
    }
    if (record->teleServiceCode) {
        char* hex_result = buffer_to_hex(record->teleServiceCode->buf, record->teleServiceCode->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->bearerServiceCode) {
        printf("%s;", record->bearerServiceCode->buf);
    }
    if (record->transparencyIndicator) {
        printf("%ln;", record->transparencyIndicator);
    }
    if (record->firstRadioChannelUsed) {
        if (record->firstRadioChannelUsed != NULL) {
        printf("%s;", getFirstradiochannelused(*record->firstRadioChannelUsed));
        } else {
            printf(";");
        }
    }
    if (record->callPosition) {
        if (record->callPosition != NULL) {
        printf("%s;", getCallPositionString(*record->callPosition));
        } else {
            printf(";");
        }  
 }
    if (record->eosInfo) {
        char* hex_result = buffer_to_hex(record->eosInfo->buf, record->eosInfo->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->internalCauseAndLoc) {
        char* hex_result = buffer_to_hex(record->internalCauseAndLoc->buf, record->internalCauseAndLoc->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->restartDuringCall) {
        printf("%ls;", record->restartDuringCall);
    }
    if (record->restartDuringOutputIndicator) {
        printf("%ls;", record->restartDuringOutputIndicator);
    }
    if (record->numberOfMeterPulses) {
        printf("%s;", record->numberOfMeterPulses->buf);
    }
    if (record->c7ChargingMessage) {
        printf("%s;", record->c7ChargingMessage->buf);
    }
    if (record->c7FirstCHTMessage) {
        printf("%s;", record->c7FirstCHTMessage->buf);
    }
    if (record->c7SecondCHTMessage) {
        printf("%s;", record->c7SecondCHTMessage->buf);
    }
    if (record->calledPartyMNPInfo) {
        printf("%s;", record->calledPartyMNPInfo->buf);
    }
    if (record->carrierIdentificationCode) {
        printf("%s;", record->carrierIdentificationCode->buf);
    }
    if (record->dTMFUsed) {
        printf("%ls;", record->dTMFUsed);
    }
    if (record->iCIOrdered) {
        printf("%ls;", record->iCIOrdered);
    }
    if (record->outputForSubscriber) {
        printf("%ln;", record->outputForSubscriber);
    }
    if (record->iNMarkingOfMS) {
        // char* hex_result = buffer_to_hex(record->iNMarkingOfMS->buf, record->iNMarkingOfMS->size);
        // printf("%s;", hex_result);
        if (record->iNMarkingOfMS != NULL) {
        printf("%s;", getINmarkingofMS(*record->iNMarkingOfMS));
        } else {
            printf(";");
        }
    }
    if (record->lastPartialOutput) {
    printf("%ls;", record->lastPartialOutput);
}
if (record->partialOutputRecNum) {
    printf("%s;", record->partialOutputRecNum->buf);
}
if (record->cUGInterlockCode) {
    printf("%s;", record->cUGInterlockCode->buf);
}
if (record->cUGIndex) {
    printf("%s;", record->cUGIndex->buf);
}
if (record->cUGOutgoingAccessUsed) {
    printf("%ls;", record->cUGOutgoingAccessUsed);
}
if (record->cUGOutgoingAccessIndicator) {
    printf("%ls;", record->cUGOutgoingAccessIndicator);
}
if (record->regionalServiceUsed) {
    printf("%ln;", record->regionalServiceUsed);
}
if (record->regionDependentChargingOrigin) {
    printf("%s;", record->regionDependentChargingOrigin->buf);
}
if (record->sSCode) {
    printf("%s;", record->sSCode->buf);
}
if (record->channelAllocationPriorityLevel) {
    printf("%s;", record->channelAllocationPriorityLevel->buf);
}
if (record->radioChannelProperty) {
    if (record->radioChannelProperty != NULL) {
        printf("%s;", getRadiochannelproperty(*record->radioChannelProperty));
        } else {
            printf(";");
        }
}
if (record->faultCode) {
    char* hex_result = buffer_to_hex(record->faultCode->buf, record->faultCode->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->intermediateRate) {
    printf("%ln;", record->intermediateRate);
}
if (record->firstAssignedSpeechCoderVersion) {
    if (record->firstAssignedSpeechCoderVersion != NULL) {
        printf("%s;", getSpeechcoderversion(*record->firstAssignedSpeechCoderVersion));
        } else {
            printf(";");
        }
    }
if (record->speechCoderPreferenceList) {
    char* hex_result = buffer_to_hex(record->speechCoderPreferenceList->buf, record->speechCoderPreferenceList->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->subscriptionType) {
    char* hex_result = buffer_to_hex(record->subscriptionType->buf, record->subscriptionType->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->incompleteCallDataIndicator) {
    printf("%ls;", record->incompleteCallDataIndicator);
}
if (record->incompleteCompositeCDRIndicator) {
    printf("%ls;", record->incompleteCompositeCDRIndicator);
}
if (record->switchIdentity) {
    char* hex_result = buffer_to_hex(record->switchIdentity->buf, record->switchIdentity->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->networkCallReference) {
    char* hex_result = buffer_to_hex(record->networkCallReference->buf, record->networkCallReference->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->frequencyBandSupported) {
    char* hex_result = buffer_to_hex(record->frequencyBandSupported->buf, record->frequencyBandSupported->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->disconnectionDueToSystemRecovery) {
    printf("%ls;", record->disconnectionDueToSystemRecovery);
}
if (record->forloppDuringOutputIndicator) {
    printf("%ls;", record->forloppDuringOutputIndicator);
}
if (record->forloppReleaseDuringCall) {
    printf("%ls;", record->forloppReleaseDuringCall);
}
if (record->accountCode) {
    printf("%s;", record->accountCode->buf);
}
if (record->translatedNumber) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->translatedNumber->buf, record->translatedNumber->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}
if (record->gSMCallReferenceNumber) {
    char* hex_result = buffer_to_hex(record->gSMCallReferenceNumber->buf, record->gSMCallReferenceNumber->size);
    printf("%s;", hex_result);
    free(hex_result);
}
if (record->mSCAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->mSCAddress->buf, record->mSCAddress->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}
if (record->eMLPPPriorityLevel) {
    printf("%s;", record->eMLPPPriorityLevel->buf);
}

if (record->positionAccuracy) {
    printf("%s;", record->positionAccuracy->buf);
}

if (record->userTerminalPosition) {
    printf("%s;", record->userTerminalPosition->buf);
}

if (record->acceptableChannelCodings) {
    printf("%s;", record->acceptableChannelCodings->buf);
}

if (record->incomingAssignedRoute) {
    printf(" %s;",record->incomingAssignedRoute->buf);
}

if (record->channelCodingUsed) {
    printf("%s;", record->channelCodingUsed->buf);
}

if (record->rANAPCauseCode) {
    printf("%s;", record->rANAPCauseCode->buf);
}

if (record->gsmSCFAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->gsmSCFAddress->buf, record->gsmSCFAddress->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}

if (record->fNURRequested) {
    if (record->fNURRequested != NULL) {
        printf("%s;", getfixedNetworkUserRate(*record->fNURRequested));
        } else {
            printf(";");
    }
}

if (record->aIURRequested) {
    if (record->aIURRequested != NULL) {
        printf("%s;", getAirInterfaceUserRate(*record->aIURRequested));
        } else {
            printf(";");
    }
}

if (record->numberOfChannelsRequested) {
    printf("%ln;", record->numberOfChannelsRequested);
}

if (record->bSSMAPCauseCode) {
    printf("%s;", record->bSSMAPCauseCode->buf);
}

if (record->multimediaCall) {
    printf("%ls;", record->multimediaCall);
}

if (record->guaranteedBitRate) {
    printf("%s;", record->guaranteedBitRate->buf);
}

if (record->trafficClass) {
    uint64_t hex_result = hexBufferToDecimal(record->trafficClass->buf, record->trafficClass->size);
    printf("%ld;", hex_result);
}

if (record->outputType) {
    // char* hex_result = buffer_to_hex(record->outputType->buf, record->outputType->size);
    // printf("%s;", hex_result);
    if (record->outputType != NULL) {
        printf("%s;", getOutputType(*record->outputType));
        } else {
            printf(";");
    }
}

if (record->rNCidOfFirstRNC) {
    char* hex_result = buffer_to_hex(record->rNCidOfFirstRNC->buf,record->rNCidOfFirstRNC->size);
    printf("%s;", hex_result);
    free(hex_result);
}

if (record->maxBitRateDownlink) {
    printf("%s;", record->maxBitRateDownlink->buf);
}

if (record->maxBitRateUplink) {
    printf("%s;", record->maxBitRateUplink->buf);
}

if (record->transferDelay) {
    printf("%s;", record->transferDelay->buf);
}

if (record->deliveryOfErroneousSDU1) {
    printf("%ln;", record->deliveryOfErroneousSDU1);
}

if (record->deliveryOfErroneousSDU2) {
    printf("%ln;", record->deliveryOfErroneousSDU2);
}

if (record->deliveryOfErroneousSDU3) {
    printf("%ln;", record->deliveryOfErroneousSDU3);
}

if (record->residualBitErrorRatio1) {
    printf("%s;", record->residualBitErrorRatio1->buf);
}

if (record->residualBitErrorRatio2) {
    printf("%s;", record->residualBitErrorRatio2->buf);
}

if (record->residualBitErrorRatio3) {
    printf("%s;", record->residualBitErrorRatio3->buf);
}

if (record->sDUErrorRatio1) {
    printf("%s;", record->sDUErrorRatio1->buf);
}

if (record->sDUErrorRatio2) {
    printf("%s;", record->sDUErrorRatio2->buf);
}

if (record->sDUErrorRatio3) {
    printf("%s;", record->sDUErrorRatio3->buf);
}

if (record->aCMChargingIndicator) {
    printf("%s;", record->aCMChargingIndicator->buf);
}

if (record->aNMChargingIndicator) {
    printf("%s;", record->aNMChargingIndicator->buf);
}

if (record->carrierInformationBackward) {
    printf("%s;", record->carrierInformationBackward->buf);
}

if (record->chargeInformation) {
    printf("%s;", record->chargeInformation->buf);
}

if (record->disconnectionDate) {
    printf("%s;", record->disconnectionDate->buf);
}

if (record->disconnectionTime) {
    char* hex_result = BCD(record->disconnectionTime->buf, record->disconnectionTime->size);
        printf("%s;", hex_result);
        free(hex_result);
}

if (record->originatingCarrier) {
    printf("%s;", record->originatingCarrier->buf);
}

if (record->originatingChargeArea) {
    printf("%s;", record->originatingChargeArea->buf);
}

if (record->tDSCounter) {
    printf("%s;", record->tDSCounter->buf);
}

if (record->terminatingAccessISDN) {
    printf("%ls;", record->terminatingAccessISDN);
}

if (record->terminatingCarrier) {
    printf("%s;", record->terminatingCarrier->buf);
}

if (record->terminatingChargeArea) {
    printf("%s;", record->terminatingChargeArea->buf);
}

if (record->terminatingMobileUserClass1) {
    printf("%s;", record->terminatingMobileUserClass1->buf);
}

if (record->terminatingMobileUserClass2) {
    printf("%s;", record->terminatingMobileUserClass2->buf);
}

if (record->terminatingUserClass) {
    printf("%s;", record->terminatingUserClass->buf);
}

if (record->contractorNumber) {
    printf("%s;", record->contractorNumber->buf);
}

if (record->carrierInformation) {
    printf("%s;", record->carrierInformation->buf);
}

if (record->carrierSelectionSubstitutionInformation) {
    printf("%s;", record->carrierSelectionSubstitutionInformation->buf);
}

if (record->chargeNumber) {
    printf("%s;", record->chargeNumber->buf);
}

if (record->interExchangeCarrierIndicator) {
    printf("%ls;", record->interExchangeCarrierIndicator);
}

if (record->originatingLineInformation) {
    printf("%s;", record->originatingLineInformation->buf);
}

if (record->selectedCodec) {
    printf("%ln;", record->selectedCodec);
}

if (record->wPSCallIndicator) {
    printf("%ls;", record->wPSCallIndicator);
}

if (record->userToUserInformation) {
    printf("%s;", record->userToUserInformation->buf);
}

if (record->callingSubscriberIMEISV) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->callingSubscriberIMEISV->buf, record->callingSubscriberIMEISV->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
}

if (record->globalCallReference) {
    printf("%s;", record->globalCallReference->buf);
}

if (record->roamingPriorityLevel) {
    printf("%s;", record->roamingPriorityLevel->buf);
}

if (record->rTCIndicator) {
    printf("%ls;", record->rTCIndicator);
}

if (record->rTCSessionID) {
    printf("%s;", record->rTCSessionID->buf);
}

if (record->rTCDefaultServiceHandling) {
    printf("%ln;", record->rTCDefaultServiceHandling);
}

if (record->rTCFailureIndicator) {
    printf("%s;", record->rTCFailureIndicator->buf);
}

if (record->rTCNotInvokedReason) {
    printf("%ln;", record->rTCNotInvokedReason);
}

if (record->calledDirectoryNumber) {
    printf("%s;", record->calledDirectoryNumber->buf);
}

if (record->outgoingPChargingVector) {
    printf("%s;", record->outgoingPChargingVector->buf);
}

if (record->iuCodec) {
    printf("%ln;", record->iuCodec);
}

if (record->bladeID) {
    char* hex_result = buffer_to_hex(record->bladeID->buf, record->bladeID->size);
    printf("%s;", hex_result);
    free(hex_result);
}

if (record->buddyBladeIndicator) {
    printf("%ls;", record->buddyBladeIndicator);
}

if (record->trafficIsolationIndicator) {
    printf("%ls;", record->trafficIsolationIndicator);
}


if (record->ccbsCallIndicator) {
    char* hex_result = buffer_to_hex(record->ccbsCallIndicator->buf, record->ccbsCallIndicator->size);
    printf("%s;", hex_result);
    free(hex_result);
}

if (record->originatedCode) {
    char* hex_result = buffer_to_hex((uint8_t*)&record->originatedCode, sizeof(record->originatedCode));
    printf("%s;", hex_result);
    free(hex_result);
    // printf("%ln;", record->originatedCode);
}

if (record->reroutingIndicator) {
    printf("%ls;", record->reroutingIndicator);
}

if (record->invocationOfCallHold) {
    printf("%ls;", record->invocationOfCallHold);
}

if (record->retrievalOfHeldCall) {
    printf("%ls;", record->retrievalOfHeldCall);
}

}


void process_mSTerminating(const MSTerminating_t *record){


    if(record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];

    printf("MSTerminating;");

if (record->tAC) {
        uint64_t hex_result = hexBufferToDecimal(record->tAC->buf,record->tAC->size);
        printf("%ld;", hex_result);
    }
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->typeOfCallingSubscriber) {
        uint64_t hex_result = hexBufferToDecimal(record->typeOfCallingSubscriber->buf, record->typeOfCallingSubscriber->size);
        printf("%ld;", hex_result);
    }
    if (record->callingPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingPartyNumber->buf, record->callingPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->calledPartyNumber) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->calledPartyNumber->buf, record->calledPartyNumber->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
    }
    if (record->calledSubscriberIMSI) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->calledSubscriberIMSI->buf, record->calledSubscriberIMSI->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
    }
    if (record->calledSubscriberIMEI) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->calledSubscriberIMEI->buf, record->calledSubscriberIMEI->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->mobileStationRoamingNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mobileStationRoamingNumber->buf, record->mobileStationRoamingNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
      if (record->disconnectingParty) {
        // char* hex_result = buffer_to_hex(record->disconnectingParty->buf, record->disconnectingParty->size);
        // printf("%s;", hex_result);
        if (record->disconnectingParty != NULL) {
        printf("%s;", getDisconnectingParty(*record->disconnectingParty));
        } else {
            printf(";");
        }

    }
    if (record->dateForStartOfCharge) {
        char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf, record->dateForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf, record->timeForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeForStopOfCharge) {
        char* hex_result = BCD(record->timeForStopOfCharge->buf, record->timeForStopOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->chargeableDuration) {
        char* hex_result = BCD(record->chargeableDuration->buf, record->chargeableDuration->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->interruptionTime) {
        char* hex_result = BCD(record->interruptionTime->buf, record->interruptionTime->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeFromRegisterSeizureToStartOfCharging) {
        char* hex_result = BCD(record->timeFromRegisterSeizureToStartOfCharging->buf, record->timeFromRegisterSeizureToStartOfCharging->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->chargedParty) {
        // char* hex_result = buffer_to_hex(record->chargedParty->buf, record->chargedParty->size);
        // printf("%s;", hex_result);
        if (record->chargedParty != NULL) {
        printf("%s;", getChargedparty(*record->chargedParty));
        } else {
            printf(";");
        }
    }
    if (record->originForCharging) {
        char* hex_result = buffer_to_hex(record->originForCharging->buf, record->originForCharging->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->tariffClass) {
        uint64_t hex_result = hexBufferToDecimal(record->tariffClass->buf, record->tariffClass->size);
        printf("%ld;", hex_result);
    }
    if (record->tariffSwitchInd) {
        // char* hex_result = buffer_to_hex(record->tariffSwitchInd->buf, record->tariffSwitchInd->size);
        // printf("%s;", hex_result);
        if (record->tariffSwitchInd != NULL) {
        printf("%s;", getTariffSwitchInd(*record->tariffSwitchInd));
        } else {
            printf(";");
        }
    }
    if (record->exchangeIdentity) {
        printf("%s;", record->exchangeIdentity->buf);
    }
    if (record->mSCIdentification) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCIdentification->buf, record->mSCIdentification->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->outgoingRoute) {
        printf("%s;", record->outgoingRoute->buf);
    }
    if (record->incomingRoute) {
        printf("%s;", record->incomingRoute->buf);
    }
    if (record->channelAllocationPriorityLevel) {
    printf("%s;", record->channelAllocationPriorityLevel->buf);
    }
    if (record->terminatingLocationNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->terminatingLocationNumber->buf, record->terminatingLocationNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->timeForTCSeizureCalled) {
        char* hex_result = BCD(record->timeForTCSeizureCalled->buf, record->timeForTCSeizureCalled->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->firstCalledLocationInformation){
        char* hex_result = decode_LocationInformation(record->firstCalledLocationInformation->buf, record->firstCalledLocationInformation->size);
        printf("%s;", hex_result);
    }
    if (record->lastCalledLocationInformation) {
        char* hex_result = decode_LocationInformation(record->lastCalledLocationInformation->buf, record->lastCalledLocationInformation->size);
        printf("%s;", hex_result);
    }
    if (record->teleServiceCode) {
        char* hex_result = buffer_to_hex(record->teleServiceCode->buf, record->teleServiceCode->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->bearerServiceCode) {
        printf("%s;", record->bearerServiceCode->buf);
    }
    if (record->transparencyIndicator) {
        printf("%ln;", record->transparencyIndicator);
    }
    if (record->firstRadioChannelUsed) {
        if (record->firstRadioChannelUsed != NULL) {
        printf("%s;", getFirstradiochannelused(*record->firstRadioChannelUsed));
        } else {
            printf(";");
        }
    }
    if (record->callPosition) {
        if (record->callPosition != NULL) {
        printf("%s;", getCallPositionString(*record->callPosition));
        } else {
            printf(";");
        }
    }
    if (record->eosInfo) {
        char* hex_result = buffer_to_hex(record->eosInfo->buf, record->eosInfo->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->internalCauseAndLoc) {
        char* hex_result = buffer_to_hex(record->internalCauseAndLoc->buf, record->internalCauseAndLoc->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->originalCalledNumber){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->originalCalledNumber->buf, record->originalCalledNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }

    if (record->redirectingNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->redirectingNumber->buf, record->redirectingNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->redirectionCounter) {
        uint64_t hex_result = hexBufferToDecimal(record->redirectionCounter->buf, record->redirectionCounter->size);
        printf("%ld;", hex_result);
    }
    if (record->selectedCodec) {
    printf("%ln;", record->selectedCodec);
    }
    if (record->userToUserInformation) {
        printf("%s;", record->userToUserInformation->buf);
    }
    if (record->restartDuringCall) {
        printf("%ls;", record->restartDuringCall);
    }

    // restartDuringOutputIndicator
    if (record->restartDuringOutputIndicator) {
        printf("%ls;", record->restartDuringOutputIndicator);
    }
    if (record->dTMFUsed) {
        printf("%ls;", record->dTMFUsed);
    }
    if (record->iCIOrdered) {
        printf("%ls;", record->iCIOrdered);
    }
    if (record->outputForSubscriber) {
        printf("%ln;", record->outputForSubscriber);
    }
    if (record->lastPartialOutput) {
        printf("%ls;", record->lastPartialOutput);
    }

    // partialOutputRecNum
    if (record->partialOutputRecNum) {
        printf("%s;", record->partialOutputRecNum->buf);
    }
    if (record->relatedCallNumber) {
        char* hex_result = buffer_to_hex(record->relatedCallNumber->buf, record->relatedCallNumber->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->acceptanceOfCallWaiting){
        printf("%ls;", record->acceptanceOfCallWaiting);
    }
    if (record->miscellaneousInformation) {
    char* hex_result = buffer_to_hex(record->miscellaneousInformation->buf,record->miscellaneousInformation->size);
    printf("s;", hex_result);
    free(hex_result);
    }
    if (record->cUGInterlockCode) {
        printf("%s;", record->cUGInterlockCode->buf);
    }

    // cUGIndex
    if (record->cUGIndex) {
        printf("%s;", record->cUGIndex->buf);
    }
    if (record->cUGIncomingAccessUsed) {
        printf("%ls;", record->cUGIncomingAccessUsed);
    }
    if (record->regionalServiceUsed) {
    printf("%ln;", record->regionalServiceUsed);
    }
    if (record->regionDependentChargingOrigin) {
        printf("%s;", record->regionDependentChargingOrigin->buf);
    }
    if (record->sSCode) {
        printf("%s;", record->sSCode->buf);
    }
    if (record->presentationAndScreeningIndicator) {
        uint64_t hex_result = hexBufferToDecimal(record->presentationAndScreeningIndicator->buf, record->presentationAndScreeningIndicator->size);
        printf("%ld;", hex_result);
    }
    if (record->radioChannelProperty) {
    if (record->radioChannelProperty != NULL) {
        printf("%s;", getRadiochannelproperty(*record->radioChannelProperty));
        } else {
            printf(";");
    }
    }
    if (record->faultCode) {
        char* hex_result = buffer_to_hex(record->faultCode->buf, record->faultCode->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->intermediateRate) {
        printf("%ln;", record->intermediateRate);
    }
    if (record->firstAssignedSpeechCoderVersion) {
        if (record->firstAssignedSpeechCoderVersion != NULL) {
        printf("%s;", getSpeechcoderversion(*record->firstAssignedSpeechCoderVersion));
        } else {
            printf(";");
        }
    }
    if (record->speechCoderPreferenceList) {
        char* hex_result = buffer_to_hex(record->speechCoderPreferenceList->buf, record->speechCoderPreferenceList->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->subscriptionType) {
        char* hex_result = buffer_to_hex(record->subscriptionType->buf, record->subscriptionType->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->incompleteCallDataIndicator) {
        printf("%ls;", record->incompleteCallDataIndicator);
    }
    if (record->mSCAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->mSCAddress->buf, record->mSCAddress->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
    }
    if (record->switchIdentity) {
    char* hex_result = buffer_to_hex(record->switchIdentity->buf, record->switchIdentity->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->networkCallReference) {
        char* hex_result = buffer_to_hex(record->networkCallReference->buf, record->networkCallReference->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->frequencyBandSupported) {
        char* hex_result = buffer_to_hex(record->frequencyBandSupported->buf, record->frequencyBandSupported->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->disconnectionDueToSystemRecovery) {
        printf("%ls;", record->disconnectionDueToSystemRecovery);
    }
    if (record->forloppDuringOutputIndicator) {
        printf("%ls;", record->forloppDuringOutputIndicator);
    }
    if (record->forloppReleaseDuringCall) {
        printf("%ls;", record->forloppReleaseDuringCall);
    }
    if (record->accountCode) {
        printf("%s;", record->accountCode->buf);
    }
    if (record->gSMCallReferenceNumber) {
    char* hex_result = buffer_to_hex(record->gSMCallReferenceNumber->buf, record->gSMCallReferenceNumber->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->eMLPPPriorityLevel) {
    printf("%s;", record->eMLPPPriorityLevel->buf);
    }

    if (record->positionAccuracy) {
        printf("%s;", record->positionAccuracy->buf);
    }

    if (record->userTerminalPosition) {
        printf("%s;", record->userTerminalPosition->buf);
    }

    if (record->acceptableChannelCodings) {
        printf("%s;", record->acceptableChannelCodings->buf);
    } 
    if (record->outgoingAssignedRoute){
        printf(" %s;",record->outgoingAssignedRoute->buf);
    }
    if (record->channelCodingUsed) {
    printf("%s;", record->channelCodingUsed->buf);
    }
    if (record->multimediaCall) {
    printf("%ls;", record->multimediaCall);
    }
    if (record->gsmSCFAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->gsmSCFAddress->buf, record->gsmSCFAddress->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
    }

    if (record->fNURRequested) {
        printf("%ln;", record->fNURRequested);
    }

    if (record->aIURRequested) {
        if (record->aIURRequested != NULL) {
        printf("%s;", getAirInterfaceUserRate(*record->aIURRequested));
        } else {
            printf(";");
    }
    }

    if (record->numberOfChannelsRequested) {
        printf("%ln;", record->numberOfChannelsRequested);
    }

    if (record->bSSMAPCauseCode) {
        printf("%s;", record->bSSMAPCauseCode->buf);
    }

    if (record->multimediaCall) {
        printf("%ls;", record->multimediaCall);
    }

    if (record->guaranteedBitRate) {
        printf("%s;", record->guaranteedBitRate->buf);
    }

    if (record->trafficClass) {
        uint64_t hex_result = hexBufferToDecimal(record->trafficClass->buf, record->trafficClass->size);
    printf("%ld;", hex_result);
    }
    if (record->rANAPCauseCode) {
    printf("%s;", record->rANAPCauseCode->buf);
    }
    if (record->rNCidOfFirstRNC) {
    char* hex_result = buffer_to_hex(record->rNCidOfFirstRNC->buf,record->rNCidOfFirstRNC->size);
    printf("%s;", hex_result);
    free(hex_result);
    }

    if (record->maxBitRateDownlink) {
        printf("%s;", record->maxBitRateDownlink->buf);
    }

    if (record->maxBitRateUplink) {
        printf("%s;", record->maxBitRateUplink->buf);
    }

    if (record->transferDelay) {
        printf("%s;", record->transferDelay->buf);
    }

    if (record->deliveryOfErroneousSDU1) {
        printf("%ln;", record->deliveryOfErroneousSDU1);
    }

    if (record->deliveryOfErroneousSDU2) {
        printf("%ln;", record->deliveryOfErroneousSDU2);
    }

    if (record->deliveryOfErroneousSDU3) {
        printf("%ln;", record->deliveryOfErroneousSDU3);
    }

    if (record->residualBitErrorRatio1) {
        printf("%s;", record->residualBitErrorRatio1->buf);
    }

    if (record->residualBitErrorRatio2) {
        printf("%s;", record->residualBitErrorRatio2->buf);
    }

    if (record->residualBitErrorRatio3) {
        printf("%s;", record->residualBitErrorRatio3->buf);
    }

    if (record->sDUErrorRatio1) {
        printf("%s;", record->sDUErrorRatio1->buf);
    }

    if (record->sDUErrorRatio2) {
        printf("%s;", record->sDUErrorRatio2->buf);
    }

    if (record->sDUErrorRatio3) {
        printf("%s;", record->sDUErrorRatio3->buf);
    }
    if (record->outputType) {
    if (record->outputType != NULL) {
        printf("%s;", getOutputType(*record->outputType));
        } else {
            printf(";");
    }
    }
    if (record->aCMChargingIndicator) {
    printf("%s;", record->aCMChargingIndicator->buf);
    }

    if (record->aNMChargingIndicator) {
        printf("%s;", record->aNMChargingIndicator->buf);
    }

    if (record->chargeInformation) {
        printf("%s;", record->chargeInformation->buf);
    }

    if (record->disconnectionDate) {
        printf("%s;", record->disconnectionDate->buf);
    }

    if (record->disconnectionTime) {
        char* hex_result = BCD(record->disconnectionTime->buf, record->disconnectionTime->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->internationalCallIndicator){
        printf("%ls;", record->internationalCallIndicator);
    }
    if (record->mobileUserClass1) {
        printf("%s;", record->mobileUserClass1->buf);
    }
    if (record->mobileUserClass2) {
        printf("%s;", record->mobileUserClass2->buf);
    }
    if (record->originatingCarrier) {
    printf("%s;", record->originatingCarrier->buf);
    }

    if (record->originatingChargeArea) {
        printf("%s;", record->originatingChargeArea->buf);
    }
    if (record->terminatingCarrier) {
        printf("%s;", record->terminatingCarrier->buf);
    }

    if (record->terminatingChargeArea) {
        printf("%s;", record->terminatingChargeArea->buf);
    }
    if (record->userClass){
        printf("%s;", record->userClass->buf);
    }
    if (record->calledSubscriberIMEISV)
    {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->calledSubscriberIMEISV->buf, record->calledSubscriberIMEISV->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    

}


void process_locationServices(const LocationServices_t *record){
    if(record == NULL) {
        return;
    }
    printf("LocationServices;")
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    if (record->tAC) {
        uint64_t hex_result = hexBufferToDecimal(record->tAC->buf,record->tAC->size);
        printf("%ld;", hex_result);
    }
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->typeOfCallingSubscriber) {
        uint64_t hex_result = hexBufferToDecimal(record->typeOfCallingSubscriber->buf, record->typeOfCallingSubscriber->size);
        printf("%ld;", hex_result);
    }
    if (record->targetMSISDN){
        char decoded_tbcd[OUTPUT_BUFFER_SIZE];
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->targetMSISDN->buf, record->targetMSISDN->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->targetIMSI){
        char decoded_tbcd[OUTPUT_BUFFER_SIZE];
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->targetIMSI->buf, record->targetIMSI->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->targetIMEI){
        char decoded_tbcd[OUTPUT_BUFFER_SIZE];
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->targetIMEI->buf, record->targetIMEI->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->dateForStartOfCharge) {
        char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf, record->dateForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf, record->timeForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->exchangeIdentity) {
    printf("%s;", record->exchangeIdentity->buf);
    }
    if (record->mSCIdentification) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCIdentification->buf, record->mSCIdentification->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->miscellaneousInformation) {
    char* hex_result = buffer_to_hex(record->miscellaneousInformation->buf,record->miscellaneousInformation->size);
    printf("s;", hex_result);
    free(hex_result);
    }
    if (record->restartDuringOutputIndicator) {
        printf("%ls;", record->restartDuringOutputIndicator);
    }
    if (record->iCIOrdered) {
        printf("%ls;", record->iCIOrdered);
    }
    if (record->outputForSubscriber) {
        printf("%ln;", record->outputForSubscriber);
    }
    if (record->incompleteCallDataIndicator) {
        printf("%ls;", record->incompleteCallDataIndicator);
    }
    if (record->switchIdentity) {
    char* hex_result = buffer_to_hex(record->switchIdentity->buf, record->switchIdentity->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->networkCallReference) {
        char* hex_result = buffer_to_hex(record->networkCallReference->buf, record->networkCallReference->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->forloppDuringOutputIndicator) {
    printf("%ls;", record->forloppDuringOutputIndicator);
    }
    if (record->positioningDelivery){
        printf("%s;", record->positioningDelivery->buf);
    }
    if(record->lCSClientIdentity){
        printf("%s;", record->lCSClientIdentity->buf);
    }
    if(record->lCSClientType){
        printf("%ln;", record->lCSClientType);
    }
    if(record->locationEstimate){
        printf("%s;", record->locationEstimate->buf);
    }
    if(record->ageOfLocationEstimate){
        printf("%s;", record->ageOfLocationEstimate->buf);
    }
    if(record->subscriberState){
        printf("%ln;", record->subscriberState);
    }
    if(record->mLCAddress){
        printf("%s;", record->mLCAddress->buf);
    }
    if(record->decipheringKeys){
        printf("%s;", record->decipheringKeys->buf);
    }
    if(record->typeOfLocationRequest){
        printf("%ln;", record->typeOfLocationRequest);
    }
    if(record->firstTargetLocationInformation){
        char* hex_result = decode_LocationInformation(record->firstTargetLocationInformation->buf, record->firstTargetLocationInformation->size);
        printf("%s;", hex_result);
    }
    if(record->horizontalAccuracy){
        printf("%s;", record->horizontalAccuracy->buf);
    }
    if(record->responseTimeCategory){
        printf("%ln;", record->responseTimeCategory);
    }
    if(record->verticalAccuracy){
        printf("%s;", record->verticalAccuracy->buf);
    }
    if(record->verticalCoordinateRequest){
        printf("%ls;", record->verticalCoordinateRequest);
    }
    if(record->unsuccessfulPositioningDataReason){
        printf("%ln;", record->unsuccessfulPositioningDataReason);
    }
    if (record->lCSDeferredEventType){
        printf("%ln;", record->lCSDeferredEventType);
    }
    if(record->targetIMEISV){
        printf("%s;", record->targetIMEISV->buf);
    }
    if (record->globalCallReference) {
    printf("%s;", record->globalCallReference->buf);
    }
    if (record->bladeID) {
    char* hex_result = buffer_to_hex(record->bladeID->buf, record->bladeID->size);
    printf("%s;", hex_result);
    free(hex_result);
    }

    if (record->buddyBladeIndicator) {
        printf("%ls;", record->buddyBladeIndicator);
    }

    if (record->trafficIsolationIndicator) {
        printf("%ls;", record->trafficIsolationIndicator);
    }
    if (record->outputType) {
    if (record->outputType != NULL) {
        printf("%s;", getOutputType(*record->outputType));
        } else {
            printf(";");
    }
    }
    return;
    printf("\n");
}

void process_msOriginatingSMSinMSC(const MSOriginatingSMSinMSC_t *record){
    if(record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    printf("msoriginatingsmsinmsc;");
    if (record->tAC) {
        uint64_t hex_result = hexBufferToDecimal(record->tAC->buf,record->tAC->size);
        printf("%ld;", hex_result);
    }
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->typeOfCallingSubscriber) {
        uint64_t hex_result = hexBufferToDecimal(record->typeOfCallingSubscriber->buf, record->typeOfCallingSubscriber->size);
        printf("%ld;", hex_result);
    }
    if (record->callingPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingPartyNumber->buf, record->callingPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->callingSubscriberIMSI) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingSubscriberIMSI->buf, record->callingSubscriberIMSI->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->callingSubscriberIMEI) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingSubscriberIMEI->buf, record->callingSubscriberIMEI->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->dateForStartOfCharge) {
    char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf,record->dateForStartOfCharge->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf,record->timeForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->chargedParty) {
        // char* hex_result = buffer_to_hex(record->chargedParty->buf, record->chargedParty->size);
        // printf("%s;", hex_result);
        if (record->chargedParty != NULL) {
        printf("%s;", getChargedparty(*record->chargedParty));
        } else {
            printf(";");
        }
    }
    if (record->originForCharging) {
        char* hex_result = buffer_to_hex(record->originForCharging->buf, record->originForCharging->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->exchangeIdentity) {
    printf("%s;", record->exchangeIdentity->buf);
    }
    if (record->mSCIdentification) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCIdentification->buf, record->mSCIdentification->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->incomingRoute) {
        printf("%s;", record->incomingRoute->buf);
    }
    if (record->firstCallingLocationInformation) {
        char* hex_result = decode_LocationInformation(record->firstCallingLocationInformation->buf, record->firstCallingLocationInformation->size);
        printf("%s;", hex_result);
    }
    if (record->teleServiceCode) {
        char* hex_result = buffer_to_hex(record->teleServiceCode->buf,record->teleServiceCode->size);
        printf("%s;", hex_result);
        free(hex_result);
    }    
    if (record->serviceCentreAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->serviceCentreAddress->buf, record->serviceCentreAddress->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
    }
    if (record->callingSubscriberIMEISV) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->callingSubscriberIMEISV->buf, record->callingSubscriberIMEISV->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
    }
    if (record->iCIOrdered) {
    printf("%ls;", record->iCIOrdered);
    }
    if (record->outputForSubscriber) {
    printf("%ln;", record->outputForSubscriber);
    }
    if (record->miscellaneousInformation) {
    char* hex_result = buffer_to_hex(record->miscellaneousInformation->buf,record->miscellaneousInformation->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->regionalServiceUsed) {
    printf("%ln;", record->regionalServiceUsed);
    }
    if (record->regionDependentChargingOrigin) {
        char* hex_result = buffer_to_hex(record->regionDependentChargingOrigin->buf,record->regionDependentChargingOrigin->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->channelAllocationPriorityLevel) {
    printf("%s;", record->channelAllocationPriorityLevel->buf);
    }
    if (record->frequencyBandSupported) {
    char* hex_result = buffer_to_hex(record->frequencyBandSupported->buf,record->frequencyBandSupported->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->incompleteCallDataIndicator) {
        printf("%ls;", record->incompleteCallDataIndicator);
    }
    if (record->restartDuringOutputIndicator) {
    printf("%ls;", record->restartDuringOutputIndicator);
    }
    if (record->forloppDuringOutputIndicator) {
        printf("%ls;", record->forloppDuringOutputIndicator);
    }
    if (record->positionAccuracy) {
        char* hex_result = buffer_to_hex(record->positionAccuracy->buf,record->positionAccuracy->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->userTerminalPosition) {
        char* hex_result = buffer_to_hex(record->userTerminalPosition->buf,record->userTerminalPosition->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->switchIdentity) {
    char* hex_result = buffer_to_hex(record->switchIdentity->buf,record->switchIdentity->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->destinationAddress) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_address_string_extended(record->destinationAddress->buf, record->destinationAddress->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->messageReference) {
        printf("%s;", record->messageReference->buf);
    }
    if (record->messageTypeIndicator) {
        if (record->messageTypeIndicator != NULL) {
        printf("%s;", getMessageTypeindicator(*record->messageTypeIndicator));
        } else {
            printf(";");
    }
    }
    if (record->rNCidOfFirstRNC) {
        char* hex_result = buffer_to_hex(record->rNCidOfFirstRNC->buf,record->rNCidOfFirstRNC->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->bCSMTDPData1) {
    char* hex_result = buffer_to_hex(record->bCSMTDPData1->serviceKey.buf,record->bCSMTDPData1->serviceKey.size);
    printf("%s;", hex_result);
    char* hex_result2 = buffer_to_hex(record->bCSMTDPData1->gsmSCFAddress.buf,record->bCSMTDPData1->gsmSCFAddress.size);
    printf("%s;", hex_result2);
    free(hex_result);
    }
    if (record->cAMELCallingPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->cAMELCallingPartyNumber->buf, record->cAMELCallingPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if(record->cAMELDestinationAddress){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_address_string_extended(record->cAMELDestinationAddress->buf, record->cAMELDestinationAddress->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if(record->cAMELSMSCAddress){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->cAMELSMSCAddress->buf, record->cAMELSMSCAddress->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if(record->defaultSMSHandling){
        printf("%ln;", record->defaultSMSHandling);
    }
    if (record->freeFormatData) {
    char* hex_result = buffer_to_hex(record->freeFormatData->buf,record->freeFormatData->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->sMSResult) {
        char* hex_result = buffer_to_hex(record->sMSResult->buf,record->sMSResult->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->sMSReferenceNumber) {
        char* hex_result = buffer_to_hex(record->sMSReferenceNumber->buf,record->sMSReferenceNumber->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->mSCAddress) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCAddress->buf, record->mSCAddress->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->rTCIndicator) {
    printf(" %ls;", record->rTCIndicator);
    }
    if (record->rTCSessionID) {
        char* hex_result = buffer_to_hex(record->rTCSessionID->buf,record->rTCSessionID->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->rTCDefaultServiceHandling) {
        printf("%ln;", record->rTCDefaultServiceHandling);
    }
    if (record->rTCFailureIndicator) {
        char* hex_result = buffer_to_hex(record->rTCFailureIndicator->buf,record->rTCFailureIndicator->size);
        printf(" %s;", hex_result);
        free(hex_result);
    }
    if (record->rTCNotInvokedReason) {
        printf("%ln;", record->rTCNotInvokedReason);
    }
    if (record->mCASMSIndicator){
        printf("%ls;", record->mCASMSIndicator);
    }
    if (record->reroutedToServiceCentreAddress){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->reroutedToServiceCentreAddress->buf, record->reroutedToServiceCentreAddress->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->bladeID) {
    char* hex_result = buffer_to_hex(record->bladeID->buf,record->bladeID->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->buddyBladeIndicator) {
        printf("%ls;", record->buddyBladeIndicator);
    }
    if (record->trafficIsolationIndicator) {
        printf("%ls;", record->trafficIsolationIndicator);
    }
    if (record->firstCallingLocationInformationExtension) {
        char* hex_result = decode_LocationInformationExtension(record->firstCallingLocationInformationExtension->buf, record->firstCallingLocationInformationExtension->size);
        printf("%s;", hex_result);
    }
    if (record->outputType != NULL) {
        printf("%s;", getOutputType(*record->outputType));
        } else {
            printf(";");
    }
    if (record->ccbsCallIndicator) {
    char* hex_result = buffer_to_hex(record->ccbsCallIndicator->buf,record->ccbsCallIndicator->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
}

void process_msOriginatingSMSinSMSIWMSC(const MSOriginatingSMSinSMS_IWMSC_t *record){
    if (record == NULL) {
        return;
    }
    
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];

    printf("recordType: MSOriginatigSMSinSMS-IWMSC;");

    if (record->tAC) {
        uint64_t hex_result = hexBufferToDecimal(record->tAC->buf,record->tAC->size);
        printf("%ld;", hex_result);
    }
    if(record->callIdentificationNumber){
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("%ld;", hex_result);
    }
    if(record->recordSequenceNumber){
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->callingPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingPartyNumber->buf, record->callingPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
     if (record->dateForStartOfCharge) {
    char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf,record->dateForStartOfCharge->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf,record->timeForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }   
    if (record->chargedParty) {
    if (record->chargedParty != NULL) {
        printf("%s;", getChargedparty(*record->chargedParty));
        } else {
            printf(";");
        }
    }
    if (record->exchangeIdentity) {
        printf("%s;", record->exchangeIdentity->buf);
    }
    if (record->mSCIdentification) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCIdentification->buf, record->mSCIdentification->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->teleServiceCode) {
        char* hex_result = buffer_to_hex(record->teleServiceCode->buf,record->teleServiceCode->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->serviceCentreAddress) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->serviceCentreAddress->buf, record->serviceCentreAddress->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->miscellaneousInformation) {
        char* hex_result = buffer_to_hex(record->miscellaneousInformation->buf,record->miscellaneousInformation->size);
        printf("%s;", hex_result);
        free(hex_result);
    }  
    if (record->incompleteCallDataIndicator) {
        printf("%ls;", record->incompleteCallDataIndicator);
    }
    if (record->restartDuringOutputIndicator) {
        printf("%ls;", record->restartDuringOutputIndicator);
    }  
     if (record->forloppDuringOutputIndicator) {
    printf("%ls;", record->forloppDuringOutputIndicator);
    }
    if (record->switchIdentity) {
        char* hex_result = buffer_to_hex(record->switchIdentity->buf, record->switchIdentity->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->bladeID) {
    char* hex_result = buffer_to_hex(record->bladeID->buf,record->bladeID->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if(record->outputType){
        if (record->outputType != NULL) {
        printf("%s;", getOutputType(*record->outputType));
        } else {
            printf(";");
    }
    }
}
void process_msTerminatingSMSinSMSGMSC(const MSTerminatingSMSinSMS_GMSC_t *record){
    if(record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    printf("MSTerminatingSMSinSMS-GMSC;");
    if (record->tAC) {
        uint64_t hex_result = hexBufferToDecimal(record->tAC->buf,record->tAC->size);
        printf("%ld;", hex_result);
    }
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->calledPartyNumber){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->calledPartyNumber->buf, record->calledPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->calledSubscriberIMSI) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->calledSubscriberIMSI->buf, record->calledSubscriberIMSI->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
    }
    if (record->mobileStationRoamingNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mobileStationRoamingNumber->buf, record->mobileStationRoamingNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->dateForStartOfCharge) {
    char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf,record->dateForStartOfCharge->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf,record->timeForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->chargedParty) {
    if (record->chargedParty != NULL) {
        printf("%s;", getChargedparty(*record->chargedParty));
        } else {
            printf(";");
        }
    }
    if (record->exchangeIdentity) {
    printf("%s;", record->exchangeIdentity->buf);
    }
    if (record->mSCIdentification) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCIdentification->buf, record->mSCIdentification->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->teleServiceCode) {
    char* hex_result = buffer_to_hex(record->teleServiceCode->buf,record->teleServiceCode->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->serviceCentreAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->serviceCentreAddress->buf, record->serviceCentreAddress->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
    }
    if(record->mSCNumber){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCNumber->buf, record->mSCNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->miscellaneousInformation) {
    char* hex_result = buffer_to_hex(record->miscellaneousInformation->buf,record->miscellaneousInformation->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->incompleteCallDataIndicator) {
        printf("%ls;", record->incompleteCallDataIndicator);
    }
    if (record->restartDuringOutputIndicator) {
    printf("%ls;", record->restartDuringOutputIndicator);
    }
    if (record->forloppDuringOutputIndicator) {
    printf("%ls;", record->forloppDuringOutputIndicator);
    }
    if (record->numberOfShortMessages){
    uint64_t decimalValue = hexBufferToDecimal(record->numberOfShortMessages->buf,record->numberOfShortMessages->size);
    printf("%lu;", decimalValue);
    }
    if (record->switchIdentity) {
    char* hex_result = buffer_to_hex(record->switchIdentity->buf,record->switchIdentity->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->bladeID) {
    char* hex_result = buffer_to_hex(record->bladeID->buf,record->bladeID->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->outputType) {
        if (record->outputType != NULL) {
        printf("%s;", getOutputType(*record->outputType));
        } else {
            printf(";");
    }
    }

}

void process_ssProcedure(const SSProcedure_t *record){
    if(record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    printf("SSProcedure;");
    if (record->tAC) {
        uint64_t hex_result = hexBufferToDecimal(record->tAC->buf,record->tAC->size);
        printf("%ld;", hex_result);
    }
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->typeOfCallingSubscriber) {
        uint64_t hex_result = hexBufferToDecimal(record->typeOfCallingSubscriber->buf, record->typeOfCallingSubscriber->size);
        printf("%ld;", hex_result);
    }
    if (record->callingPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingPartyNumber->buf, record->callingPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->callingSubscriberIMSI) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingSubscriberIMSI->buf, record->callingSubscriberIMSI->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->callingSubscriberIMEI) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingSubscriberIMEI->buf, record->callingSubscriberIMEI->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->dateForStartOfCharge) {
    char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf,record->dateForStartOfCharge->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf,record->timeForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->originForCharging) {
    char* hex_result = buffer_to_hex(record->originForCharging->buf,record->originForCharging->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->exchangeIdentity) {
        printf("%s;", record->exchangeIdentity->buf);
    }
    if (record->mSCIdentification) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCIdentification->buf, record->mSCIdentification->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->firstCallingLocationInformation) {
        char* hex_result = decode_LocationInformation(record->firstCallingLocationInformation->buf, record->firstCallingLocationInformation->size);
        printf("%s;", hex_result);
    }
    if (record->callingSubscriberIMEISV) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingSubscriberIMEISV->buf, record->callingSubscriberIMEISV->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }        
    if (record->iCIOrdered) {
        printf("%ls;", record->iCIOrdered);
    }
    if (record->outputForSubscriber) {
        printf("%ln;", record->outputForSubscriber);
    }
    if (record->sSCode) {
    printf("%s;", record->sSCode->buf);
    }
    if (record->sSRequest){
        printf("%ln;", record->sSRequest);
    }
    if (record->miscellaneousInformation) {
        char* hex_result = buffer_to_hex(record->miscellaneousInformation->buf,record->miscellaneousInformation->size);
        printf("%s;", hex_result);
        free(hex_result);
    }    
    if (record->regionalServiceUsed) {
        printf("%ln;", record->regionalServiceUsed);
    }
    if (record->regionDependentChargingOrigin) {
        char* hex_result = buffer_to_hex(record->regionDependentChargingOrigin->buf,record->regionDependentChargingOrigin->size);
        printf("%s;", hex_result);
        free(hex_result);
    }   
    if (record->relatedCallNumber) {
        char* hex_result = buffer_to_hex(record->relatedCallNumber->buf, record->relatedCallNumber->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->uSSDApplicationIdentifier) {
        printf("%s;", record->uSSDApplicationIdentifier->buf);
    }
    if (record->uSSDServiceCode) {
        printf("%s;", record->uSSDServiceCode->buf);
    }
    if (record ->uSSDProcedureCode) {
        printf("%s;", record->uSSDProcedureCode->buf);
    }
    if (record->networkInitiatedUSSDOperations) {
        printf("%s;", record->networkInitiatedUSSDOperations->buf);
    }
    if (record->uSSDOperationIdentifier){
        printf("%s;", record->uSSDOperationIdentifier->buf);
    }
    if (record->incompleteCallDataIndicator) {
    printf("%ls;", record->incompleteCallDataIndicator);
    }
    if (record->restartDuringOutputIndicator) {
    printf("%ls;", record->restartDuringOutputIndicator);
    }
    if (record->frequencyBandSupported) {
    char* hex_result = buffer_to_hex(record->frequencyBandSupported->buf,record->frequencyBandSupported->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->forloppDuringOutputIndicator) {
    printf("%ls;", record->forloppDuringOutputIndicator);
    }
    if (record->switchIdentity) {
    char* hex_result = buffer_to_hex(record->switchIdentity->buf, record->switchIdentity->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->networkCallReference) {
        char* hex_result = buffer_to_hex(record->networkCallReference->buf, record->networkCallReference->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->positionAccuracy) {
        char* hex_result = buffer_to_hex(record->positionAccuracy->buf,record->positionAccuracy->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->userTerminalPosition) {
        char* hex_result = buffer_to_hex(record->userTerminalPosition->buf,record->userTerminalPosition->size);
        printf("%s;", hex_result);
        free(hex_result);
    }    
    
    if (record->rNCidOfFirstRNC) {
        char* hex_result = buffer_to_hex(record->rNCidOfFirstRNC->buf,record->rNCidOfFirstRNC->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->globalCallReference) {
        printf("%s;", record->globalCallReference->buf);
    }
    if (record->bladeID) {
    char* hex_result = buffer_to_hex(record->bladeID->buf,record->bladeID->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->buddyBladeIndicator) {
        printf("%ls;", record->buddyBladeIndicator);
    }
    if (record->outputType) {
    if (record->outputType != NULL) {
        printf("%s;", getOutputType(*record->outputType));
        } else {
            printf(";");
    }
    }
    return;
}

void process_transit(const Transit_t *record){
    if (record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    printf("Transit;");
    if (record->tAC) {
        uint64_t hex_result = hexBufferToDecimal(record->tAC->buf,record->tAC->size);
        printf("%ld;", hex_result);
    }
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->typeOfCallingSubscriber) {
        uint64_t hex_result = hexBufferToDecimal(record->typeOfCallingSubscriber->buf, record->typeOfCallingSubscriber->size);
        printf("%ld;", hex_result);
    }
    if (record->callingPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingPartyNumber->buf, record->callingPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if(record->calledPartyNumber){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->calledPartyNumber->buf, record->calledPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->calledSubscriberIMSI) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->calledSubscriberIMSI->buf, record->calledSubscriberIMSI->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
        if (record->disconnectingParty) {
        // char* hex_result = buffer_to_hex(record->disconnectingParty->buf, record->disconnectingParty->size);
        // printf("%s;", hex_result);
        if (record->disconnectingParty != NULL) {
        printf("%s;", getDisconnectingParty(*record->disconnectingParty));
        } else {
            printf(";");
        }
    }
    if (record->dateForStartOfCharge) {
        char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf, record->dateForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf, record->timeForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeForStopOfCharge) {
        char* hex_result = BCD(record->timeForStopOfCharge->buf, record->timeForStopOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->chargeableDuration) {
        char* hex_result = BCD(record->chargeableDuration->buf, record->chargeableDuration->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->interruptionTime) {
        char* hex_result = BCD(record->interruptionTime->buf, record->interruptionTime->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeFromRegisterSeizureToStartOfCharging) {
        char* hex_result = BCD(record->timeFromRegisterSeizureToStartOfCharging->buf, record->timeFromRegisterSeizureToStartOfCharging->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->chargedParty) {
        // char* hex_result = buffer_to_hex(record->chargedParty->buf, record->chargedParty->size);
        // printf("%s;", hex_result);
        if (record->chargedParty != NULL) {
        printf("%s;", getChargedparty(*record->chargedParty));
        } else {
            printf(";");
        }
    }
    if (record->originForCharging) {
        char* hex_result = buffer_to_hex(record->originForCharging->buf, record->originForCharging->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    if (record->tariffClass) {
        uint64_t hex_result = hexBufferToDecimal(record->tariffClass->buf, record->tariffClass->size);
        printf("%ld;", hex_result);
    }
    if (record->tariffSwitchInd) {
        // char* hex_result = buffer_to_hex(record->tariffSwitchInd->buf, record->tariffSwitchInd->size);
        // printf("%s;", hex_result);
        if (record->tariffSwitchInd != NULL) {
        printf(" %s;", getTariffSwitchInd(*record->tariffSwitchInd));
        } else {
            printf(";");
        }
    }
        if (record->numberOfMeterPulses) {
        printf("%s;", record->numberOfMeterPulses->buf);
    }
    if (record->exchangeIdentity) {
        printf("%s;", record->exchangeIdentity->buf);
    }
    if (record->mSCIdentification) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCIdentification->buf, record->mSCIdentification->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->outgoingRoute) {
        printf("%s;", record->outgoingRoute->buf);
    }
    if (record->incomingRoute) {
        printf("%s;", record->incomingRoute->buf);
    }
    if (record->miscellaneousInformation) {
    char* hex_result = buffer_to_hex(record->miscellaneousInformation->buf,record->miscellaneousInformation->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->iNMarkingOfMS) {
        if (record->iNMarkingOfMS != NULL) {
        printf("%s;", getINmarkingofMS(*record->iNMarkingOfMS));
        } else {
            printf(";");
        }
    }
    if (record->callPosition) {
        if (record->callPosition != NULL) {
        printf("%s;", getCallPositionString(*record->callPosition));
        } else {
            printf(";");
        }
}
    if (record->eosInfo) {
        char* hex_result = buffer_to_hex(record->eosInfo->buf, record->eosInfo->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->internalCauseAndLoc) {
        char* hex_result = buffer_to_hex(record->internalCauseAndLoc->buf, record->internalCauseAndLoc->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->originalCalledNumber){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->originalCalledNumber->buf, record->originalCalledNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }

    if (record->redirectingNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->redirectingNumber->buf, record->redirectingNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->redirectionCounter) {
        uint64_t hex_result = hexBufferToDecimal(record->redirectionCounter->buf, record->redirectionCounter->size);
        printf("%ld;", hex_result);
    }
    if (record->redirectingDropBackNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->redirectingDropBackNumber->buf, record->redirectingDropBackNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->redirectingDropBack){
        printf("%ls;", record->redirectingDropBack);
    }
        if (record->restartDuringCall) {
        printf("%ls;", record->restartDuringCall);
    }

    // restartDuringOutputIndicator
    if (record->restartDuringOutputIndicator) {
        printf("%ls;", record->restartDuringOutputIndicator);
    }
    if (record->iCIOrdered) {
        printf("%ls;", record->iCIOrdered);
    }
    if (record->outputForSubscriber) {
        printf("%ln;", record->outputForSubscriber);
    }
    if (record->lastPartialOutput) {
        printf("%ls;", record->lastPartialOutput);
    }

    // partialOutputRecNum
    if (record->partialOutputRecNum) {
        printf("%s;", record->partialOutputRecNum->buf);
    }
    if (record->relatedCallNumber) {
        char* hex_result = buffer_to_hex(record->relatedCallNumber->buf, record->relatedCallNumber->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->faultCode) {
        printf("%s;", record->faultCode->buf);
    }
    if (record->subscriptionType) {
        char* hex_result = buffer_to_hex(record->subscriptionType->buf, record->subscriptionType->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->incompleteCallDataIndicator) {
        printf("%ls;", record->incompleteCallDataIndicator);
    }
    if (record->incompleteCompositeCDRIndicator) {
        printf("%ls;", record->incompleteCompositeCDRIndicator);
    }
    if (record->switchIdentity) {
    char* hex_result = buffer_to_hex(record->switchIdentity->buf,record->switchIdentity->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->networkCallReference) {
        printf("%s;", record->networkCallReference->buf);
    }
    if (record->disconnectionDueToSystemRecovery) {
        printf("%ls;", record->disconnectionDueToSystemRecovery);
    }
    if (record->forloppDuringOutputIndicator) {
        printf("%ls;", record->forloppDuringOutputIndicator);
    }
    if (record->forloppReleaseDuringCall) {
        printf("%ls;", record->forloppReleaseDuringCall);
    }
    if (record->translatedNumber) {
        printf("%s;", record->translatedNumber->buf);
    }
    // bCSMTDPData1
    if (record->bCSMTDPData1) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData1->serviceKey.buf,record->bCSMTDPData1->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData1->gsmSCFAddress.buf,record->bCSMTDPData1->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData2
    if (record->bCSMTDPData2) {
                char* hex_result = buffer_to_hex(record->bCSMTDPData2->serviceKey.buf,record->bCSMTDPData2->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData2->gsmSCFAddress.buf,record->bCSMTDPData2->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData3
    if (record->bCSMTDPData3) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData3->serviceKey.buf,record->bCSMTDPData3->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData3->gsmSCFAddress.buf,record->bCSMTDPData3->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData4
    if (record->bCSMTDPData4) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData4->serviceKey.buf,record->bCSMTDPData4->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData4->gsmSCFAddress.buf,record->bCSMTDPData4->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData5
    if (record->bCSMTDPData5) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData5->serviceKey.buf,record->bCSMTDPData5->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData5->gsmSCFAddress.buf,record->bCSMTDPData5->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData6
    if (record->bCSMTDPData6) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData6->serviceKey.buf,record->bCSMTDPData6->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData6->gsmSCFAddress.buf,record->bCSMTDPData6->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData7
    if (record->bCSMTDPData7) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData7->serviceKey.buf,record->bCSMTDPData7->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData7->gsmSCFAddress.buf,record->bCSMTDPData7->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData8
    if (record->bCSMTDPData8) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData8->serviceKey.buf,record->bCSMTDPData8->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData8->gsmSCFAddress.buf,record->bCSMTDPData8->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }
    // bCSMTDPData9
    if (record->bCSMTDPData9) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData9->serviceKey.buf,record->bCSMTDPData9->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData9->gsmSCFAddress.buf,record->bCSMTDPData9->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // bCSMTDPData10
    if (record->bCSMTDPData10) {
        char* hex_result = buffer_to_hex(record->bCSMTDPData10->serviceKey.buf,record->bCSMTDPData10->serviceKey.size);
        printf("%s;", hex_result);
        char* hex_result2 = buffer_to_hex(record->bCSMTDPData10->gsmSCFAddress.buf,record->bCSMTDPData10->gsmSCFAddress.size);
        printf("%s;", hex_result2);
        free(hex_result);
        free(hex_result2);
    }

    // gSMCallReferenceNumber
    if (record->gSMCallReferenceNumber) {
    char* hex_result = buffer_to_hex(record->gSMCallReferenceNumber->buf, record->gSMCallReferenceNumber->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->c7ChargingMessage) {
        printf("%s;", record->c7ChargingMessage->buf);
    }

    // c7FirstCHTMessage
    if (record->c7FirstCHTMessage) {
        printf("%s;", record->c7FirstCHTMessage->buf);
    }

    // c7SecondCHTMessage
    if (record->c7SecondCHTMessage) {
        printf("%s;", record->c7SecondCHTMessage->buf);
    }
    if (record->aCMChargingIndicator) {
    printf("%s;", record->aCMChargingIndicator->buf);
    }
    if (record->aNMChargingIndicator) { 
        printf("%s;", record->aNMChargingIndicator->buf);
    }
    if (record->mSCAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->mSCAddress->buf, record->mSCAddress->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
    }
    if (record->carrierInformationBackward) {
        printf("%s;", record->carrierInformationBackward->buf);
    }
    if (record->carrierInformationForward) {
        printf("%s;", record->carrierInformationForward->buf);
    }
    if (record->chargeInformation) {
        printf("%s;", record->chargeInformation->buf);
    }

    // disconnectionDate
    if (record->disconnectionDate) {
        printf("%s;", record->disconnectionDate->buf);
    }

    // disconnectionTime
    if (record->disconnectionTime) {
        char* hex_result = BCD(record->disconnectionTime->buf, record->disconnectionTime->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->entryPOICA){
        printf("%s;", record->entryPOICA->buf);
    }
    if (record->exitPOICA){
        printf("%s;", record->exitPOICA->buf);
    }
    if (record->internationalCallIndicator){
        printf("%ls;", record->internationalCallIndicator);
    }
    if (record->mobileUserClass1) {
        printf("%s;", record->mobileUserClass1->buf);
    }
    if (record->mobileUserClass2) {
        printf("%s;", record->mobileUserClass2->buf);
    }
    if (record->originatingAccessISDN) {
        printf("%ls;", record->originatingAccessISDN);
    }
    if (record->originatingCarrier) {
        printf("%s;", record->originatingCarrier->buf);
    }
    if (record->originatingChargeArea) {
        printf("%s;", record->originatingChargeArea->buf);
    }
    if (record->tDSCounter) {
        printf("%s;", record->tDSCounter->buf);
    }

    if (record->terminatingAccessISDN) {
        printf("%ls;", record->terminatingAccessISDN);
    }

    if (record->terminatingCarrier) {
        printf("%s;", record->terminatingCarrier->buf);
    }

    if (record->terminatingChargeArea) {
        printf("%s;", record->terminatingChargeArea->buf);
    }

    if (record->terminatingMobileUserClass1) {
        printf("%s;", record->terminatingMobileUserClass1->buf);
    }

    if (record->terminatingMobileUserClass2) {
        printf("%s;", record->terminatingMobileUserClass2->buf);
    }
    if (record->contractorNumber) {
        printf("%s;", record->contractorNumber->buf);
    }
    if (record->terminatingUserClass) {
        printf("%s;", record->terminatingUserClass->buf);
    }
    if (record->userClass) {
        printf("%s;", record->userClass->buf);
    }
    if (record->calledPartyMNPInfo) {
        printf("%s;", record->calledPartyMNPInfo->buf);
    }
    if (record->chargeNumber) {
        printf("%s;", record->chargeNumber->buf);
    }
    if (record->originatingLineInformation) {
        printf("%s;", record->originatingLineInformation->buf);
    }
    if (record->multimediaInformation) {
        printf("%ln;", record->multimediaInformation->userRate);
    }
    if (record->globalCallReference) {
        printf("%s;", record->globalCallReference->buf);
    }
    if (record->rTCIndicator) {
    printf(" %ls;", record->rTCIndicator);
    }
    if (record->rTCSessionID) {
    char* hex_result = buffer_to_hex(record->rTCSessionID->buf,record->rTCSessionID->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->rTCDefaultServiceHandling) {
        printf("%ln;", record->rTCDefaultServiceHandling);
    }
    if (record->rTCFailureIndicator) {
        char* hex_result = buffer_to_hex(record->rTCFailureIndicator->buf,record->rTCFailureIndicator->size);
        printf(" %s;", hex_result);
        free(hex_result);
    }
    if (record->rTCNotInvokedReason) {
        printf("%ln;", record->rTCNotInvokedReason);
    }
    if (record->calledDirectoryNumber) {
        printf("%s;", record->calledDirectoryNumber->buf);
    }
    if (record->incomingPChargingVector) {
        printf("%s;", record->incomingPChargingVector->buf);
    }
    if (record->outputType) {
    if (record->outputType != NULL) {
        printf(" %s;", getOutputType(*record->outputType));
        } else {
            printf(";");
    }
    }
    if (record->outgoingPChargingVector) {
        printf("%s;", record->outgoingPChargingVector->buf);
    }

    // bladeID
    if (record->bladeID) {
        char* hex_result = buffer_to_hex(record->bladeID->buf, record->bladeID->size);
        printf("%s;", hex_result);
        free(hex_result);
    }

    // buddyBladeIndicator
    if (record->buddyBladeIndicator) {
        printf("%ls;", record->buddyBladeIndicator);
    }

    // trafficIsolationIndicator
    if (record->trafficIsolationIndicator) {
        printf("%ls;", record->trafficIsolationIndicator);
    }
    if (record->carrierIdentificationCode) {
        printf("%s;", record->carrierIdentificationCode->buf);
    }

    // carrierInformation
    if (record->carrierInformation) {
        printf("%s;", record->carrierInformation->buf);
    }

    // carrierSelectionSubstitutionInformation
    if (record->carrierSelectionSubstitutionInformation) {
        printf("%s;", record->carrierSelectionSubstitutionInformation->buf);
    }
    if (record->interExchangeCarrierIndicator) {
        printf("%ls;", record->interExchangeCarrierIndicator);
    }
    if (record->originatedCode) {
    char* hex_result = buffer_to_hex((uint8_t*)&record->originatedCode, sizeof(record->originatedCode));
    printf("%s;", hex_result);
    free(hex_result);
    // printf("%ln;", record->originatedCode);
    }
    if (record->reroutingIndicator) {
    printf("%ls;", record->reroutingIndicator);
    }
    return;
}

void process_roamingCallForwarding(const RoamingCallForwarding_t *record){
    if (record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    printf("RoamingCallForwarding;\n");
    if (record->tAC) {
        uint64_t hex_result = hexBufferToDecimal(record->tAC->buf,record->tAC->size);
        printf("%ld", hex_result);
    }
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("%ld", hex_result);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("%ld", hex_result);
    }
    if (record->typeOfCallingSubscriber) {
        uint64_t hex_result = hexBufferToDecimal(record->typeOfCallingSubscriber->buf, record->typeOfCallingSubscriber->size);
        printf("%ld", hex_result);
    }
    if (record->callingPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingPartyNumber->buf, record->callingPartyNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if(record->calledPartyNumber){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->calledPartyNumber->buf, record->calledPartyNumber->size, decoded_tbcd);
        printf("%s", decoded_tbcd);
    }
    if (record->calledSubscriberIMSI) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->calledSubscriberIMSI->buf, record->calledSubscriberIMSI->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if(record->mobileStationRoamingNumber){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mobileStationRoamingNumber->buf, record->mobileStationRoamingNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->disconnectingParty) {
        // char* hex_result = buffer_to_hex(record->disconnectingParty->buf, record->disconnectingParty->size);
        // printf("disconnectingParty:%s;\n", hex_result);
        if (record->disconnectingParty != NULL) {
        printf("%s;", getDisconnectingParty(*record->disconnectingParty));
        } else {
            printf(";");
        }
    }
    if (record->dateForStartOfCharge) {
        char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf, record->dateForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf, record->timeForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeForStopOfCharge) {
        char* hex_result = BCD(record->timeForStopOfCharge->buf, record->timeForStopOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->chargeableDuration) {
        char* hex_result = BCD(record->chargeableDuration->buf, record->chargeableDuration->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->interruptionTime) {
        char* hex_result = BCD(record->interruptionTime->buf, record->interruptionTime->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeFromRegisterSeizureToStartOfCharging) {
        char* hex_result = BCD(record->timeFromRegisterSeizureToStartOfCharging->buf, record->timeFromRegisterSeizureToStartOfCharging->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->chargedParty) {
        // char* hex_result = buffer_to_hex(record->chargedParty->buf, record->chargedParty->size);
        // printf("chargedParty:%s;\n", hex_result);
        if (record->chargedParty != NULL) {
        printf("%s;", getChargedparty(*record->chargedParty));
        } else {
            printf(";");
        }
    }
    if (record->originForCharging) {
        char* hex_result = buffer_to_hex(record->originForCharging->buf, record->originForCharging->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->tariffClass) {
        uint64_t hex_result = hexBufferToDecimal(record->tariffClass->buf, record->tariffClass->size);
        printf("%ld;", hex_result);
    }
    if (record->tariffSwitchInd) {
        // char* hex_result = buffer_to_hex(record->tariffSwitchInd->buf, record->tariffSwitchInd->size);
        // printf("tariffSwitchInd:%s;\n", hex_result);
        if (record->tariffSwitchInd != NULL) {
        printf("%s;", getTariffSwitchInd(*record->tariffSwitchInd));
        } else {
            printf(";");
        }
    }
    if (record->exchangeIdentity) {
        printf("%s;", record->exchangeIdentity->buf);
    }
    if (record->mSCIdentification) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCIdentification->buf, record->mSCIdentification->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->outgoingRoute) {
        printf("%s;", record->outgoingRoute->buf);
    }
    if (record->incomingRoute) {
        printf("%s;", record->incomingRoute->buf);
    }
    if (record->miscellaneousInformation) {
    char* hex_result = buffer_to_hex(record->miscellaneousInformation->buf,record->miscellaneousInformation->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->subscriptionType) {
        char* hex_result = buffer_to_hex(record->subscriptionType->buf, record->subscriptionType->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->callPosition) {
        if (record->callPosition != NULL) {
        printf("%s;", getCallPositionString(*record->callPosition));
        } else {
            printf(";");
        }
    }
    if (record->eosInfo) {
        char* hex_result = buffer_to_hex(record->eosInfo->buf, record->eosInfo->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->internalCauseAndLoc) {
        char* hex_result = buffer_to_hex(record->internalCauseAndLoc->buf, record->internalCauseAndLoc->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->originalCalledNumber){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->originalCalledNumber->buf, record->originalCalledNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }

    if (record->redirectingNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->redirectingNumber->buf, record->redirectingNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->redirectionCounter) {
        uint64_t hex_result = hexBufferToDecimal(record->redirectionCounter->buf, record->redirectionCounter->size);
        printf("%ld;", hex_result);
    }
    if (record->restartDuringCall) {
        printf("%ls;", record->restartDuringCall);
    }

    // restartDuringOutputIndicator
    if (record->restartDuringOutputIndicator) {
        printf("%ls;", record->restartDuringOutputIndicator);
    }
    if (record->numberOfMeterPulses) {
        printf("%s;", record->numberOfMeterPulses->buf);
    }

    // c7ChargingMessage
    if (record->c7ChargingMessage) {
        printf("%s;", record->c7ChargingMessage->buf);
    }

    // c7FirstCHTMessage
    if (record->c7FirstCHTMessage) {
        printf("%s;", record->c7FirstCHTMessage->buf);
    }

    // c7SecondCHTMessage
    if (record->c7SecondCHTMessage) {
        printf("%s;", record->c7SecondCHTMessage->buf);
    }
    if (record->iCIOrdered) {
        printf("%ls;", record->iCIOrdered);
    }
    if (record->outputForSubscriber) {
        printf("%ln;", record->outputForSubscriber);
    }
    if (record->lastPartialOutput) {
        printf("%ls;", record->lastPartialOutput);
    }

    // partialOutputRecNum
    if (record->partialOutputRecNum) {
        printf("%s;", record->partialOutputRecNum->buf);
    }
    if (record->relatedCallNumber) {
        char* hex_result = buffer_to_hex(record->relatedCallNumber->buf, record->relatedCallNumber->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
     if (record->cUGInterlockCode) {
        printf("%s;", record->cUGInterlockCode->buf);
    }
    if (record->cUGOutgoingAccessIndicator) {
        printf("%ls;", record->cUGOutgoingAccessIndicator);
    }
    if (record->presentationAndScreeningIndicator) {
        uint64_t hex_result = hexBufferToDecimal(record->presentationAndScreeningIndicator->buf, record->presentationAndScreeningIndicator->size);
        printf("%ld;", hex_result);
    }
    if (record->faultCode) {
        printf("%s;", record->faultCode->buf);
    }
    if (record->incompleteCallDataIndicator) {
    printf("%ln;", record->incompleteCallDataIndicator);
    }
    if (record->multimediaInformation) {
        printf("%ln;", record->multimediaInformation->userRate);
    }
    if (record->switchIdentity) {
        char* hex_result = buffer_to_hex(record->switchIdentity->buf, record->switchIdentity->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->networkCallReference) {
        printf("%s;", record->networkCallReference->buf);
    }

    if (record->disconnectionDueToSystemRecovery) {
        printf("%ls;", record->disconnectionDueToSystemRecovery);
    }

    if (record->forloppDuringOutputIndicator) {
        printf("%ls;", record->forloppDuringOutputIndicator);
    }

    // forloppReleaseDuringCall
    if (record->forloppReleaseDuringCall) {
        printf("%ls;", record->forloppReleaseDuringCall);
    }
    if (record->gSMCallReferenceNumber) {
    char* hex_result = buffer_to_hex(record->gSMCallReferenceNumber->buf, record->gSMCallReferenceNumber->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->mSCAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->mSCAddress->buf, record->mSCAddress->size, decoded_tbcd);
    printf("%s;", decoded_tbcd);
    }
    if (record->carrierInformationBackward) {
        printf("%s;", record->carrierInformationBackward->buf);
    }
    if (record->originatingAccessISDN) {
        printf("%ls;", record->originatingAccessISDN);
    }
    if (record->originatingCarrier) {
        printf("%s;", record->originatingCarrier->buf);
    }

    if (record->originatingChargeArea) {
        printf("%s;", record->originatingChargeArea->buf);
    }

    if (record->terminatingAccessISDN) {
        printf("%ls;", record->terminatingAccessISDN);
    }

    if (record->terminatingCarrier) {
        printf("%s;", record->terminatingCarrier->buf);
    }

    if (record->terminatingChargeArea) {
        printf("%s;", record->terminatingChargeArea->buf);
    }
    if (record->contractorNumber) {
        printf("%s;", record->contractorNumber->buf);
    }

    if (record->carrierIdentificationCode) {
        printf("%s;", record->carrierIdentificationCode->buf);
    }

    // carrierInformation
    if (record->carrierInformation) {
        printf("%s;", record->carrierInformation->buf);
    }

    // carrierSelectionSubstitutionInformation
    if (record->carrierSelectionSubstitutionInformation) {
        printf("%s;", record->carrierSelectionSubstitutionInformation->buf);
    }

    // chargeNumber
    if (record->chargeNumber) {
        printf("%s;", record->chargeNumber->buf);
    }

    // interExchangeCarrierIndicator
    if (record->interExchangeCarrierIndicator) {
        printf("%ls;", record->interExchangeCarrierIndicator);
    }

    // originatingLineInformation
    if (record->originatingLineInformation) {
        printf("%s;", record->originatingLineInformation->buf);
    }
     if (record->userToUserInformation) {
        printf("%s;", record->userToUserInformation->buf);
    }
    if (record->globalCallReference) {
        printf("%s;", record->globalCallReference->buf);
    }

    // rTCIndicator
    if (record->rTCIndicator) {
        printf("%ls;", record->rTCIndicator);
    }

    // rTCSessionID
    if (record->rTCSessionID) {
        printf("%s;", record->rTCSessionID->buf);
    }

    // rTCDefaultServiceHandling
    if (record->rTCDefaultServiceHandling) {
        printf("%ln", record->rTCDefaultServiceHandling);
    }

    // rTCFailureIndicator
    if (record->rTCFailureIndicator) {
        printf("%s;", record->rTCFailureIndicator->buf);
    }

    // rTCNotInvokedReason
    if (record->rTCNotInvokedReason) {
        printf("%ln;", record->rTCNotInvokedReason);
    }
    if (record->mobileSubscriberNumberForHLRInterrogation) {
        printf("%s;", record->mobileSubscriberNumberForHLRInterrogation->buf);
    }
    if (record->outgoingPChargingVector) {
        printf("%s;", record->outgoingPChargingVector->buf);
    }
        if (record->trafficIsolationIndicator) {
        printf("%ls;", record->trafficIsolationIndicator);
    }
    if (record->bladeID) {
    char* hex_result = buffer_to_hex(record->bladeID->buf,record->bladeID->size);
    printf("%s;", hex_result);
    free(hex_result);
    }
    if (record->outputType) {
    if (record->outputType != NULL) {
        printf(" %s;", getOutputType(*record->outputType));
        } else {
            printf(";");
    }
    }
    if (record->reroutingIndicator) {
    printf("%ls;", record->reroutingIndicator);
    }
}

void process_transitINOutgoingCall(const TransitINOutgoingCall_t *record){
    if (record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    printf("\n\nrecordType: TransitINOutgoingCall;\n");
    if (record->tAC) {
        uint64_t hex_result = hexBufferToDecimal(record->tAC->buf,record->tAC->size);
        printf("tAC:%ld;\n", hex_result);
    }
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("callIdentificationNumber:%ld;\n", hex_result);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("recordSequenceNumber:%ld;\n", hex_result);
    }
    if(record->outgoingRoute){
    printf("outgoingRoute:%s;",record->outgoingRoute->buf);
    }
    if (record->subscriptionType) {
        char* hex_result = buffer_to_hex(record->subscriptionType->buf, record->subscriptionType->size);
        printf("subscriptionType:%s;\n", hex_result);
        free(hex_result);
    }
    if (record->incompleteCallDataIndicator) {
        printf("incompleteCallDataIndicator:%ls;\n", record->incompleteCallDataIndicator);
    }
    if (record->incompleteCompositeCDRIndicator) {
        printf("incompleteCompositeCDRIndicator:%ls;\n", record->incompleteCompositeCDRIndicator);
    }
    if (record->lastPartialOutput) {
        printf("lastPartialOutput:%ls;\n", record->lastPartialOutput);
    }

    // partialOutputRecNum
    if (record->partialOutputRecNum) {
        printf("partialOutputRecNum:%s;\n", record->partialOutputRecNum->buf);
    }
    if (record->restartDuringOutputIndicator) {
    printf("restartDuringOutputIndicator:%ls;\n", record->restartDuringOutputIndicator);
    }
    if (record->exchangeIdentity) {
        printf("exchangeIdentity:%s;\n", record->exchangeIdentity->buf);
    }
    if (record->restartDuringCall) {
        printf("restartDuringCall:%ls;\n", record->restartDuringCall);
    }
    if (record->networkCallReference) {
        printf("networkCallReference:%s;\n", record->networkCallReference->buf);
    }
    if (record->iCIOrdered) {
    printf("iCIOrdered:%ls;\n", record->iCIOrdered);
    }
    if (record->outputForSubscriber) {
    printf("outputForSubscriber:%ln;\n", record->outputForSubscriber);
    }
        if (record->switchIdentity) {
        char* hex_result = buffer_to_hex(record->switchIdentity->buf, record->switchIdentity->size);
        printf("switchIdentity:%s;\n", hex_result);
        free(hex_result);
    }
    // disconnectionDueToSystemRecovery
    if (record->disconnectionDueToSystemRecovery) {
        printf("disconnectionDueToSystemRecovery:%ls;\n", record->disconnectionDueToSystemRecovery);
    }

    // forloppDuringOutputIndicator
    if (record->forloppDuringOutputIndicator) {
        printf("forloppDuringOutputIndicator:%ls;\n", record->forloppDuringOutputIndicator);
    }
    if (record->tariffClass) {
        uint64_t hex_result = hexBufferToDecimal(record->tariffClass->buf, record->tariffClass->size);
        printf("tariffClass:%ld;\n", hex_result);
    }

    // forloppReleaseDuringCall
    if (record->forloppReleaseDuringCall) {
        printf("forloppReleaseDuringCall:%ls;\n", record->forloppReleaseDuringCall);
    }
    if (record->c7ChargingMessage) {
        printf("c7ChargingMessage:%s;\n", record->c7ChargingMessage->buf);
    }

    // c7FirstCHTMessage
    if (record->c7FirstCHTMessage) {
        printf("c7FirstCHTMessage:%s;\n", record->c7FirstCHTMessage->buf);
    }

    // c7SecondCHTMessage
    if (record->c7SecondCHTMessage) {
        printf("c7SecondCHTMessage:%s;\n", record->c7SecondCHTMessage->buf);
    }
    if (record->contractorNumber) {
        printf("contractorNumber:%s;\n", record->contractorNumber->buf);
    }

    // calledPartyMNPInfo
    if (record->calledPartyMNPInfo) {
        printf("calledPartyMNPInfo:%s;\n", record->calledPartyMNPInfo->buf);
    }
    if (record->globalCallReference) {
        printf("globalCallReference:%s;\n", record->globalCallReference->buf);
    }
    if (record->outgoingPChargingVector) {
        printf("outgoingPChargingVector:%s;\n", record->outgoingPChargingVector->buf);
    }

    // bladeID
    if (record->bladeID) {
        char* hex_result = buffer_to_hex(record->bladeID->buf, record->bladeID->size);
        printf("bladeID:%s;\n", hex_result);
        free(hex_result);
    }
    if (record->trafficIsolationIndicator) {
        printf("trafficIsolationIndicator:%ls;\n", record->trafficIsolationIndicator);
    }
    if (record->outputType) {
    if (record->outputType != NULL) {
        printf("outputType: %s;\n", getOutputType(*record->outputType));
        } else {
            printf("outputType: Invalid value;\n");
    }
    }
    return;
}

void process_isdnOriginating(const ISDNOriginating_t *record){
    if (record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    printf("\n\nrecordType: ISDNOriginating;\n");
    if (record->trafficActivityCode) {
        char* hex_result = buffer_to_hex(record->trafficActivityCode->buf, record->trafficActivityCode->size);
        printf("trafficActivityCode:%s;\n", hex_result);
        free(hex_result);
    }
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("callIdentificationNumber:%ld;\n", hex_result);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("recordSequenceNumber:%ld;\n", hex_result);
    }
    if (record->typeOfCallingSubscriber) {
        uint64_t hex_result = hexBufferToDecimal(record->typeOfCallingSubscriber->buf, record->typeOfCallingSubscriber->size);
        printf("typeOfCallingSubscriber:%ld;\n", hex_result);
    }
    if (record->chargedCallingPartyNumber){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->chargedCallingPartyNumber->buf, record->chargedCallingPartyNumber->size, decoded_tbcd);
        printf("chargedCallingPartyNumber:%s;\n", decoded_tbcd);
    }
    if (record->calledPartyNumber) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->calledPartyNumber->buf, record->calledPartyNumber->size, decoded_tbcd);
    printf("calledPartyNumber:%s;\n", decoded_tbcd);
    }
    if (record->disconnectingParty) {
        if (record->disconnectingParty != NULL) {
        printf("disconnectingParty: %s;\n", getDisconnectingParty(*record->disconnectingParty));
        } else {
            printf("disconnectingParty: Invalid value;\n");
        }
    }

    // dateForStartOfCharge
    if (record->dateForStartOfCharge) {
        char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf, record->dateForStartOfCharge->size);
        printf("dateForStartOfCharge:%s;\n", hex_result);
        free(hex_result);
    }

    // timeForStartOfCharge
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf, record->timeForStartOfCharge->size);
        printf("timeForStartOfCharge:%s;\n", hex_result);
        free(hex_result);
    }

    // timeForStopOfCharge
    if (record->timeForStopOfCharge) {
        char* hex_result = BCD(record->timeForStopOfCharge->buf, record->timeForStopOfCharge->size);
        printf("timeForStopOfCharge:%s;\n", hex_result);
        free(hex_result);
    }

    // chargeableDuration
    if (record->chargeableDuration) {
        char* hex_result = BCD(record->chargeableDuration->buf, record->chargeableDuration->size);
        printf("chargeableDuration:%s;\n", hex_result);
        free(hex_result);
    }

    // interruptionTime
    if (record->interruptionTime) {
        char* hex_result = BCD(record->interruptionTime->buf, record->interruptionTime->size);
        printf("interruptionTime:%s;\n", hex_result);
        free(hex_result);
    }
    if (record->tariffClass) {
        uint64_t hex_result = hexBufferToDecimal(record->tariffClass->buf, record->tariffClass->size);
        printf("tariffClass:%ld;\n", hex_result);
    }

    // tariffSwitchInd
    if (record->tariffSwitchInd) {
        if (record->tariffSwitchInd != NULL) {
        printf("tariffSwitchInd: %s;\n", getTariffSwitchInd(*record->tariffSwitchInd));
        } else {
            printf("tariffSwitchInd: Invalid value;\n");
        }
    }

    // exchangeIdentity
    if (record->exchangeIdentity) {
        printf("exchangeIdentity:%s;\n", record->exchangeIdentity->buf);
    }
    if(record->outgoingRoute){
    printf("outgoingRoute:%s;",record->outgoingRoute->buf);
    }
    if (record->callPosition) {
        if (record->callPosition != NULL) {
        printf("callPosition: %s;\n", getCallPositionString(*record->callPosition));
        } else {
            printf("callPosition: Invalid value;\n");
        }    
    }
    if (record->restartDuringCall) {
        printf("restartDuringCall:%ls;\n", record->restartDuringCall);
    }

    // restartDuringOutputIndicator
    if (record->restartDuringOutputIndicator) {
        printf("restartDuringOutputIndicator:%ls;\n", record->restartDuringOutputIndicator);
    }
    if (record->lastPartialOutput) {
        printf("lastPartialOutput:%ls;\n", record->lastPartialOutput);
    }

    // partialOutputRecNum
    if (record->partialOutputRecNum) {
        printf("partialOutputRecNum:%s;\n", record->partialOutputRecNum->buf);
    }
    if (record->cUGInterlockCode) {
        printf("cUGInterlockCode:%s;\n", record->cUGInterlockCode->buf);
    }

    // cUGIndex
    if (record->cUGIndex) {
        printf("cUGIndex:%s;\n", record->cUGIndex->buf);
    }
    if (record->presentationAndScreeningIndicator) {
        uint64_t hex_result = hexBufferToDecimal(record->presentationAndScreeningIndicator->buf, record->presentationAndScreeningIndicator->size);
        printf("presentationAndScreeningIndicator:%ld;\n", hex_result);
    }
    if (record->incompleteCallDataIndicator) {
    printf("incompleteCallDataIndicator:%ls; \n", record->incompleteCallDataIndicator);
    }
    if (record->networkCallReference) {
        printf("networkCallReference:%s;\n", record->networkCallReference->buf);
    }
    if (record->disconnectionDueToSystemRecovery) {
        printf("disconnectionDueToSystemRecovery:%ls;\n", record->disconnectionDueToSystemRecovery);
    }
    if (record->forloppDuringOutputIndicator) {
    printf("forloppDuringOutputIndicator:%ls;\n", record->forloppDuringOutputIndicator);
    }
    if (record->causeCode) {
        printf("causeCode:%s;\n", record->causeCode->buf);
    }
    if (record->locationCode) {
        printf("locationCode:%s;\n", record->locationCode->buf);
    }
    if (record->networkProvidedCallingPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->networkProvidedCallingPartyNumber->buf, record->networkProvidedCallingPartyNumber->size, decoded_tbcd);
        printf("networkProvidedCallingPartyNumber:%s;\n", decoded_tbcd);
    }
    if (record->calledPartyMNPInfo) {
        printf("calledPartyMNPInfo:%s;\n", record->calledPartyMNPInfo->buf);
    }
    if (record->callingPartyNumberSpecialArrangementInd) {
        printf("callingPartyNumberSpecialArrangementInd:%ls;\n", record->callingPartyNumberSpecialArrangementInd);
    }
    if (record->userProvidedCallingPartyNumber){   
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->userProvidedCallingPartyNumber->buf, record->userProvidedCallingPartyNumber->size, decoded_tbcd);
        printf("userProvidedCallingPartyNumber:%s;\n", decoded_tbcd);
    }
    if (record->forloppReleaseDuringCall) {
        printf("forloppReleaseDuringCall:%ls;\n", record->forloppReleaseDuringCall);
    }
    if (record->chargedParty) {
    if (record->chargedParty != NULL) {
        printf("chargedParty: %s;\n", getChargedparty(*record->chargedParty));
        } else {
            printf("chargedParty: Invalid value;\n");
        }
    }
    if (record->callAttemptIndicator) {
        printf("callAttemptIndicator:%ls;\n", record->callAttemptIndicator);
    }
    if (record->flexibleCounter1) {
        printf("flexibleCounter1:%s;\n", record->flexibleCounter1->buf);
    }
    if (record->flexibleCounter2) {
        printf("flexibleCounter2:%s;\n", record->flexibleCounter2->buf);
    }
    if (record->flexibleCounter3) {
        printf("flexibleCounter3:%s;\n", record->flexibleCounter3->buf);
    }
    if (record->flexibleCounter4) {
        printf("flexibleCounter4:%s;\n", record->flexibleCounter4->buf);
    }
    if (record->flexibleCounter5) {
        printf("flexibleCounter5:%s;\n", record->flexibleCounter5->buf);
    }
    if (record->flexibleCounter6) {
        printf("flexibleCounter6:%s;\n", record->flexibleCounter6->buf);
    }
    if (record->flexibleCounter7) {
        printf("flexibleCounter7:%s;\n", record->flexibleCounter7->buf);
    }
    if (record->flexibleCounter8) {
        printf("flexibleCounter8:%s;\n", record->flexibleCounter8->buf);
    }
    if (record->callAttemptState) {
        if (record->callAttemptState != NULL) {
        printf("callAttemptState: %s;\n", getCallAttemptState(*record->callAttemptState));
        } else {
            printf("callAttemptState: Invalid value;\n");
        }
    }
    if (record->typeOfSignalling) {
        printf("typeOfSignalling:%ln;\n", record->typeOfSignalling);
    }
    if (record->typeOfCalledSubscriber) {
        printf("typeOfCalledSubscriber:%ln;\n", record->typeOfCalledSubscriber);
    }
    if (record->endToEndAccessDataMap) {
        printf("endToEndAccessDataMap:%s;\n", record->endToEndAccessDataMap->buf);
    }
    if (record->userToUserService1Information) {
        printf("userToUserService1Information:%s;\n", record->userToUserService1Information->buf);
    }
    if (record->switchIdentity) {
    char* hex_result = buffer_to_hex(record->switchIdentity->buf,record->switchIdentity->size);
    printf("switchIdentity:%s;\n", hex_result);
    free(hex_result);
    }
    if (record->aoCCurrencyAmountSentToUser) {
        printf("aoCCurrencyAmountSentToUser:%s;\n", record->aoCCurrencyAmountSentToUser->buf);
    }
    if (record->globalCallReference) {
        printf("globalCallReference:%s;\n", record->globalCallReference->buf);
    }
    if (record->outgoingPChargingVector) {
        printf("outgoingPChargingVector:%s;\n", record->outgoingPChargingVector->buf);
    }
    if (record->bladeID) {
        char* hex_result = buffer_to_hex(record->bladeID->buf, record->bladeID->size);
        printf("bladeID:%s;\n", hex_result);
        free(hex_result);
    }
    if (record->outputType) {
    if (record->outputType != NULL) {
        printf("outputType: %s;\n", getOutputType(*record->outputType));
        } else {
            printf("outputType: Invalid value;\n");
    }
    }
    return;
}

void process_inIncomingCall(const INIncomingCall_t *record){
    if (record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    printf("\n\nrecordType: INIncomingCall;\n");
    if (record->callIdentificationNumber) {
    uint64_t decimalValue = hexBufferToDecimal(record->callIdentificationNumber->buf,record->callIdentificationNumber->size);
    printf("callIdentificationNumber: %lu ;\n", decimalValue);
    }
    if (record->switchIdentity) {
        char* hex_result = buffer_to_hex(record->switchIdentity->buf, record->switchIdentity->size);
        printf("switchIdentity:%s;\n", hex_result);
        free(hex_result);
    }
    if (record->networkCallReference) {
        printf("networkCallReference:%s;\n", record->networkCallReference->buf);
    }
    if (record->iNServiceTrigger) {
        printf("iNServiceTrigger:%s;\n", record->iNServiceTrigger->buf);
    }
    if (record->sSFChargingCase) {
        printf("sSFChargingCase:%s;\n", record->sSFChargingCase->buf);
    }
    if (record->triggerData0){
        printf("triggerData0:scpAddress:%s;", record->triggerData0->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData0->serviceKey.buf);
    }
    if (record->triggerData1){
        printf("triggerData1:scpAddress:%s;", record->triggerData1->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData1->serviceKey.buf);   
    }
    if (record->triggerData2){
        printf("triggerData2:scpAddress:%s;", record->triggerData2->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData2->serviceKey.buf);     
    }
    if (record->triggerData3){
        printf("triggerData3:scpAddress:%s;", record->triggerData3->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData3->serviceKey.buf);     
    }
    if (record->triggerData4){
        printf("triggerData4:scpAddress:%s;", record->triggerData4->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData4->serviceKey.buf);     
    }
    if (record->triggerData5){
        printf("triggerData5:scpAddress:%s;", record->triggerData5->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData5->serviceKey.buf);     
    }
    if (record->triggerData6){
        printf("triggerData6:scpAddress:%s;", record->triggerData6->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData6->serviceKey.buf);     
    }
    if (record->triggerData7){
        printf("triggerData7:scpAddress:%s;", record->triggerData7->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData7->serviceKey.buf);     
    }
    if (record->recordSequenceNumber) {
    uint64_t decimalValue = hexBufferToDecimal(record->recordSequenceNumber->buf,record->recordSequenceNumber->size);
    printf("recordSequenceNumber:%lu;\n", decimalValue);
    }
    if (record->disconnectionDueToSystemRecovery) {
        printf("disconnectionDueToSystemRecovery:%ls;\n", record->disconnectionDueToSystemRecovery);
    }
    if (record->incompleteCallDataIndicator) {
        printf("incompleteCallDataIndicator:%ls;\n", record->incompleteCallDataIndicator);
    }
    if (record->incompleteCompositeCDRIndicator) {
        printf("incompleteCompositeCDRIndicator:%ls;\n", record->incompleteCompositeCDRIndicator);
    }
    if (record->lastPartialOutput) {
        printf("lastPartialOutput:%ls;\n", record->lastPartialOutput);
    }

    // partialOutputRecNum
    if (record->partialOutputRecNum) {
        printf("partialOutputRecNum:%s;\n", record->partialOutputRecNum->buf);
    }
    if (record->restartDuringOutputIndicator) {
    printf("restartDuringOutputIndicator:%ls;\n", record->restartDuringOutputIndicator);
    }
    if (record->restartDuringCall) {
        printf("restartDuringCall:%ls;\n", record->restartDuringCall);
    }
    if (record->exchangeIdentity) {
        printf("exchangeIdentity:%s;\n", record->exchangeIdentity->buf);
    }
    if (record->forloppDuringOutputIndicator) {
        printf("forloppDuringOutputIndicator:%ls;\n", record->forloppDuringOutputIndicator);
    }

    // forloppReleaseDuringCall
    if (record->forloppReleaseDuringCall) {
        printf("forloppReleaseDuringCall:%ls;\n", record->forloppReleaseDuringCall);
    }
    if (record->gSMCallReferenceNumber) {
    char* hex_result = buffer_to_hex(record->gSMCallReferenceNumber->buf, record->gSMCallReferenceNumber->size);
    printf("gSMCallReferenceNumber:%s;\n", hex_result);
    free(hex_result);
    }
    if (record->mSCAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->mSCAddress->buf, record->mSCAddress->size, decoded_tbcd);
    printf("mSCAddress:%s;\n", decoded_tbcd);
    }
    if (record->defaultCallHandling) {
        printf("defaultCallHandling:%ln;\n", record->defaultCallHandling);
    }
    if (record->defaultCallHandling2) {
        printf("defaultCallHandling2:%ln;\n", record->defaultCallHandling2);
    }
    if (record->levelOfCAMELService){
        printf("levelOfCAMELService:%s;\n", record->levelOfCAMELService->buf);
    }
    if (record->globalCallReference) {
        printf("globalCallReference:%s;\n", record->globalCallReference->buf);
    }
    if (record->bladeID) {
        char* hex_result = buffer_to_hex(record->bladeID->buf,record->bladeID->size);
        printf("bladeID:%s;\n", hex_result);
        free(hex_result);
    }
    if (record->trafficIsolationIndicator) {
        printf("trafficIsolationIndicator:%ls;\n", record->trafficIsolationIndicator);
    }
    if (record->outputType) {
    if (record->outputType != NULL) {
        printf("outputType: %s;\n", getOutputType(*record->outputType));
        } else {
            printf("outputType: Invalid value;\n");
    }
    }
    return;
}

void process_inOutgoingCall(const INOutgoingCall_t *record){
    if (record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    printf("\n\nrecordType: INOutgoingCall;\n");
    if (record->callIdentificationNumber) {
    uint64_t decimalValue = hexBufferToDecimal(record->callIdentificationNumber->buf,record->callIdentificationNumber->size);
    printf("callIdentificationNumber: %lu ;\n", decimalValue);
    }
    if (record->switchIdentity) {
        char* hex_result = buffer_to_hex(record->switchIdentity->buf, record->switchIdentity->size);
        printf("switchIdentity:%s;\n", hex_result);
        free(hex_result);
    }
    if (record->networkCallReference) {
        printf("networkCallReference:%s;\n", record->networkCallReference->buf);
    }
    if (record->iNServiceTrigger) {
        printf("iNServiceTrigger:%s;\n", record->iNServiceTrigger->buf);
    }
    if (record->sSFChargingCase) {
        printf("sSFChargingCase:%s;\n", record->sSFChargingCase->buf);
    }
    if (record->triggerData0){
        printf("triggerData0:scpAddress:%s;", record->triggerData0->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData0->serviceKey.buf);
    }
    if (record->triggerData1){
        printf("triggerData1:scpAddress:%s;", record->triggerData1->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData1->serviceKey.buf);   
    }
    if (record->triggerData2){
        printf("triggerData2:scpAddress:%s;", record->triggerData2->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData2->serviceKey.buf);     
    }
    if (record->triggerData3){
        printf("triggerData3:scpAddress:%s;", record->triggerData3->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData3->serviceKey.buf);     
    }
    if (record->triggerData4){
        printf("triggerData4:scpAddress:%s;", record->triggerData4->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData4->serviceKey.buf);     
    }
    if (record->triggerData5){
        printf("triggerData5:scpAddress:%s;", record->triggerData5->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData5->serviceKey.buf);     
    }
    if (record->triggerData6){
        printf("triggerData6:scpAddress:%s;", record->triggerData6->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData6->serviceKey.buf);     
    }
    if (record->triggerData7){
        printf("triggerData7:scpAddress:%s;", record->triggerData7->sCPAddress.choice.globalTitle.buf);
        printf("serviceKey:%s;\n",record->triggerData7->serviceKey.buf);     
    }
    if (record->recordSequenceNumber) {
    uint64_t decimalValue = hexBufferToDecimal(record->recordSequenceNumber->buf,record->recordSequenceNumber->size);
    printf("recordSequenceNumber:%lu;\n", decimalValue);
    }
    if (record->disconnectionDueToSystemRecovery) {
        printf("disconnectionDueToSystemRecovery:%ls;\n", record->disconnectionDueToSystemRecovery);
    }
    if (record->incompleteCallDataIndicator) {
        printf("incompleteCallDataIndicator:%ls;\n", record->incompleteCallDataIndicator);
    }
    if (record->incompleteCompositeCDRIndicator) {
        printf("incompleteCompositeCDRIndicator:%ls;\n", record->incompleteCompositeCDRIndicator);
    }
    if (record->lastPartialOutput) {
        printf("lastPartialOutput:%ls;\n", record->lastPartialOutput);
    }

    // partialOutputRecNum
    if (record->partialOutputRecNum) {
        printf("partialOutputRecNum:%s;\n", record->partialOutputRecNum->buf);
    }
    if (record->restartDuringOutputIndicator) {
    printf("restartDuringOutputIndicator:%ls;\n", record->restartDuringOutputIndicator);
    }
    if (record->restartDuringCall) {
        printf("restartDuringCall:%ls;\n", record->restartDuringCall);
    }
    if (record->exchangeIdentity) {
        printf("exchangeIdentity:%s;\n", record->exchangeIdentity->buf);
    }
    if (record->forloppDuringOutputIndicator) {
        printf("forloppDuringOutputIndicator:%ls;\n", record->forloppDuringOutputIndicator);
    }

    // forloppReleaseDuringCall
    if (record->forloppReleaseDuringCall) {
        printf("forloppReleaseDuringCall:%ls;\n", record->forloppReleaseDuringCall);
    }
    if (record->gSMCallReferenceNumber) {
    char* hex_result = buffer_to_hex(record->gSMCallReferenceNumber->buf, record->gSMCallReferenceNumber->size);
    printf("gSMCallReferenceNumber:%s;\n", hex_result);
    free(hex_result);
    }
    if (record->mSCAddress) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->mSCAddress->buf, record->mSCAddress->size, decoded_tbcd);
    printf("mSCAddress:%s;\n", decoded_tbcd);
    }
    if (record->defaultCallHandling) {
        printf("defaultCallHandling:%ln;\n", record->defaultCallHandling);
    }
    if (record->defaultCallHandling2) {
        printf("defaultCallHandling2:%ln;\n", record->defaultCallHandling2);
    }
    if (record->levelOfCAMELService){
        printf("levelOfCAMELService:%s;\n", record->levelOfCAMELService->buf);
    }
    if (record->gsmSCFInitiatedCallIndicator) {
        printf("gsmSCFInitiatedCallIndicator:%ls;\n", record->gsmSCFInitiatedCallIndicator);
    }
    if (record->globalCallReference) {
        printf("globalCallReference:%s;\n", record->globalCallReference->buf);
    }
    if (record->bladeID) {
        char* hex_result = buffer_to_hex(record->bladeID->buf,record->bladeID->size);
        printf("bladeID:%s;\n", hex_result);
        free(hex_result);
    }
    if (record->trafficIsolationIndicator) {
        printf("trafficIsolationIndicator:%ls;\n", record->trafficIsolationIndicator);
    }
    if (record->outputType) {
    if (record->outputType != NULL) {
        printf("outputType: %s;\n", getOutputType(*record->outputType));
        } else {
            printf("outputType: Invalid value;\n");
    }
    }
    return;

}

void process_isdnCallForwarding(const ISDNCallForwarding_t *record){
    if (record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    printf("\n\nrecordType: ISDNCallForwarding;\n");
    if (record->trafficActivityCode) {
        char* hex_result = buffer_to_hex(record->trafficActivityCode->buf, record->trafficActivityCode->size);
        printf("trafficActivityCode:%s;\n", hex_result);
        free(hex_result);
    }
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("callIdentificationNumber:%ld;\n", hex_result);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("recordSequenceNumber:%ld;\n", hex_result);
    }
    if (record->typeOfCallingSubscriber) {
        uint64_t hex_result = hexBufferToDecimal(record->typeOfCallingSubscriber->buf, record->typeOfCallingSubscriber->size);
        printf("typeOfCallingSubscriber:%ld;\n", hex_result);
    }
    if (record->chargedCallingPartyNumber){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->chargedCallingPartyNumber->buf, record->chargedCallingPartyNumber->size, decoded_tbcd);
        printf("chargedCallingPartyNumber:%s;\n", decoded_tbcd);
    }
    if (record->calledPartyNumber) {
    memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
    decode_tbcd(record->calledPartyNumber->buf, record->calledPartyNumber->size, decoded_tbcd);
    printf("calledPartyNumber:%s;\n", decoded_tbcd);
    }
    if (record->disconnectingParty) {
        if (record->disconnectingParty != NULL) {
        printf("disconnectingParty: %s;\n", getDisconnectingParty(*record->disconnectingParty));
        } else {
            printf("disconnectingParty: Invalid value;\n");
        }
    }

    // dateForStartOfCharge
    if (record->dateForStartOfCharge) {
        char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf, record->dateForStartOfCharge->size);
        printf("dateForStartOfCharge:%s;\n", hex_result);
        free(hex_result);
    }

    // timeForStartOfCharge
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf, record->timeForStartOfCharge->size);
        printf("timeForStartOfCharge:%s;\n", hex_result);
        free(hex_result);
    }

    // timeForStopOfCharge
    if (record->timeForStopOfCharge) {
        char* hex_result = BCD(record->timeForStopOfCharge->buf, record->timeForStopOfCharge->size);
        printf("timeForStopOfCharge:%s;\n", hex_result);
        free(hex_result);
    }

    // chargeableDuration
    if (record->chargeableDuration) {
        char* hex_result = BCD(record->chargeableDuration->buf, record->chargeableDuration->size);
        printf("chargeableDuration:%s;\n", hex_result);
        free(hex_result);
    }

    // interruptionTime
    if (record->interruptionTime) {
        char* hex_result = BCD(record->interruptionTime->buf, record->interruptionTime->size);
        printf("disconnectionTime:%s;\n", hex_result);
        free(hex_result);
    }
    if (record->tariffClass) {
        uint64_t hex_result = hexBufferToDecimal(record->tariffClass->buf, record->tariffClass->size);
        printf("tariffClass:%ld;\n", hex_result);
    }

    // tariffSwitchInd
    if (record->tariffSwitchInd) {
        if (record->tariffSwitchInd != NULL) {
        printf("tariffSwitchInd: %s;\n", getTariffSwitchInd(*record->tariffSwitchInd));
        } else {
            printf("tariffSwitchInd: Invalid value;\n");
        }
    }

    // exchangeIdentity
    if (record->exchangeIdentity) {
        printf("exchangeIdentity:%s;\n", record->exchangeIdentity->buf);
    }
    if(record->outgoingRoute){
    printf("outgoingRoute:%s;",record->outgoingRoute->buf);
    }
    if (record->callPosition) {
        if (record->callPosition != NULL) {
        printf("callPosition: %s;\n", getCallPositionString(*record->callPosition));
        } else {
            printf("callPosition: Invalid value;\n");
        }
   }
    if (record->originalCalledNumber) {
        printf("originalCalledNumber:%s;\n", record->originalCalledNumber->buf);
    }

    // redirectingNumber
    if (record->redirectingNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->redirectingNumber->buf, record->redirectingNumber->size, decoded_tbcd);
        printf("redirectingNumber:%s;\n", decoded_tbcd);
    }
    if (record->restartDuringCall) {
        printf("restartDuringCall:%ls;\n", record->restartDuringCall);
    }

    // restartDuringOutputIndicator
    if (record->restartDuringOutputIndicator) {
        printf("restartDuringOutputIndicator:%ls;\n", record->restartDuringOutputIndicator);
    }
    if (record->lastPartialOutput) {
        printf("lastPartialOutput:%ls;\n", record->lastPartialOutput);
    }

    // partialOutputRecNum
    if (record->partialOutputRecNum) {
        printf("partialOutputRecNum:%s;\n", record->partialOutputRecNum->buf);
    }
    if (record->cUGInterlockCode) {
        printf("cUGInterlockCode:%s;\n", record->cUGInterlockCode->buf);
    }

    // cUGIndex
    if (record->cUGIndex) {
        printf("cUGIndex:%s;\n", record->cUGIndex->buf);
    }
    if (record->presentationAndScreeningIndicator) {
        uint64_t hex_result = hexBufferToDecimal(record->presentationAndScreeningIndicator->buf, record->presentationAndScreeningIndicator->size);
        printf("presentationAndScreeningIndicator:%ld;\n", hex_result);
    }
    if (record->incompleteCallDataIndicator) {
    printf("incompleteCallDataIndicator:%ls; \n", record->incompleteCallDataIndicator);
    }
    if (record->networkCallReference) {
        printf("networkCallReference:%s;\n", record->networkCallReference->buf);
    }
    if (record->disconnectionDueToSystemRecovery) {
        printf("disconnectionDueToSystemRecovery:%ls;\n", record->disconnectionDueToSystemRecovery);
    }
    if (record->forloppDuringOutputIndicator) {
    printf("forloppDuringOutputIndicator:%ls;\n", record->forloppDuringOutputIndicator);
    }
    if (record->causeCode) {
        printf("causeCode:%s;\n", record->causeCode->buf);
    }
    if (record->locationCode) {
        printf("locationCode:%s;\n", record->locationCode->buf);
    }
    if (record->networkProvidedCallingPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->networkProvidedCallingPartyNumber->buf, record->networkProvidedCallingPartyNumber->size, decoded_tbcd);
        printf("networkProvidedCallingPartyNumber:%s;\n", decoded_tbcd);
    }
    if (record->callingPartyNumber) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->callingPartyNumber->buf, record->callingPartyNumber->size, decoded_tbcd);
        printf("callingPartyNumber:%s;\n", decoded_tbcd);
    }
    if (record->calledPartyMNPInfo) {
        printf("calledPartyMNPInfo:%s;\n", record->calledPartyMNPInfo->buf);
    }
    if (record->forloppReleaseDuringCall) {
        printf("forloppReleaseDuringCall:%ls;\n", record->forloppReleaseDuringCall);
    }
    if (record->chargedParty) {
    if (record->chargedParty != NULL) {
        printf("chargedParty: %s;\n", getChargedparty(*record->chargedParty));
        } else {
            printf("chargedParty: Invalid value;\n");
        }
    }
    if (record->callAttemptIndicator) {
        printf("callAttemptIndicator:%ls;\n", record->callAttemptIndicator);
    }
    if (record->flexibleCounter1) {
        printf("flexibleCounter1:%s;\n", record->flexibleCounter1->buf);
    }
    if (record->flexibleCounter2) {
        printf("flexibleCounter2:%s;\n", record->flexibleCounter2->buf);
    }
    if (record->flexibleCounter3) {
        printf("flexibleCounter3:%s;\n", record->flexibleCounter3->buf);
    }
    if (record->flexibleCounter4) {
        printf("flexibleCounter4:%s;\n", record->flexibleCounter4->buf);
    }
    if (record->flexibleCounter5) {
        printf("flexibleCounter5:%s;\n", record->flexibleCounter5->buf);
    }
    if (record->flexibleCounter6) {
        printf("flexibleCounter6:%s;\n", record->flexibleCounter6->buf);
    }
    if (record->flexibleCounter7) {
        printf("flexibleCounter7:%s;\n", record->flexibleCounter7->buf);
    }
    if (record->flexibleCounter8) {
        printf("flexibleCounter8:%s;\n", record->flexibleCounter8->buf);
    }
    if (record->callAttemptState) {
        if (record->callAttemptState != NULL) {
        printf("callAttemptState: %s;\n", getCallAttemptState(*record->callAttemptState));
        } else {
            printf("callAttemptState: Invalid value;\n");
        }
    }
    if (record->typeOfSignalling) {
        printf("typeOfSignalling:%ln;\n", record->typeOfSignalling);
    }
    if (record->typeOfCalledSubscriber) {
        printf("typeOfCalledSubscriber:%ln;\n", record->typeOfCalledSubscriber);
    }
    if (record->endToEndAccessDataMap) {
        printf("endToEndAccessDataMap:%s;\n", record->endToEndAccessDataMap->buf);
    }
    if (record->userToUserService1Information) {
        printf("userToUserService1Information:%s;\n", record->userToUserService1Information->buf);
    }
    if (record->switchIdentity) {
    char* hex_result = buffer_to_hex(record->switchIdentity->buf,record->switchIdentity->size);
    printf("switchIdentity:%s;\n", hex_result);
    free(hex_result);
    }
    if (record->aoCCurrencyAmountSentToUser) {
        printf("aoCCurrencyAmountSentToUser:%s;\n", record->aoCCurrencyAmountSentToUser->buf);
    }
    if (record->globalCallReference) {
        printf("%s;", record->globalCallReference->buf);
    }
    if (record->outgoingPChargingVector) {
        printf("%s;", record->outgoingPChargingVector->buf);
    }
    if (record->bladeID) {
        char* hex_result = buffer_to_hex(record->bladeID->buf, record->bladeID->size);
        printf("bladeID:%s;\n", hex_result);
        free(hex_result);
    }
    if (record->outputType) {
    if (record->outputType != NULL) {
        printf("outputType: %s;\n", getOutputType(*record->outputType));
        } else {
            printf("outputType: Invalid value;\n");
    }
    }
    return;
}

void process_scfChargingOutput(const SCFChargingOutput_t *record){
    if (record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    printf("SCFChargingOutput;");
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->exchangeIdentity) {
        printf("%s;", record->exchangeIdentity->buf);
    }
    if (record->gSMCallReferenceNumber) {
        char* hex_result = buffer_to_hex(record->gSMCallReferenceNumber->buf, record->gSMCallReferenceNumber->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->restartDuringCall) {
        printf("%ls;", record->restartDuringCall);
    }
    if (record->restartDuringOutputIndicator) {
        printf("%ls;", record->restartDuringOutputIndicator);
    }
    if (record->lastPartialOutput) {
        printf("%ls;", record->lastPartialOutput);
    }
    if (record->partialOutputRecNum) {
        printf("%s;", record->partialOutputRecNum->buf);
    }
    if (record->switchIdentity) {
        char* hex_result = buffer_to_hex(record->switchIdentity->buf, record->switchIdentity->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->disconnectionDueToSystemRecovery) {
        printf("%ls;", record->disconnectionDueToSystemRecovery);
    }
    if (record->forloppDuringOutputIndicator) {
        printf("%ls;", record->forloppDuringOutputIndicator);
    }
    if (record->forloppReleaseDuringCall) {
        printf("%ls;", record->forloppReleaseDuringCall);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->incompleteCallDataIndicator) {
        printf("%ls;", record->incompleteCallDataIndicator);
    }
    if (record->mSCAddress) {
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->mSCAddress->buf, record->mSCAddress->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->date){
        printf("%s;", record->date->buf);
    }
    if (record->bladeID) {
        char* hex_result = buffer_to_hex(record->bladeID->buf, record->bladeID->size);
        printf("%s;", hex_result);
    }
    if (record->outputType) {
        if (record->outputType != NULL) {
            printf("%s;", getOutputType(*record->outputType));
        } else {
            printf(";");
        }
    }
    printf("\n");
    return;
}

void process_isdnSSProcedure(const ISDNSSProcedure_t *record){
    if (record == NULL) {
        return;
    }
    char decoded_tbcd[OUTPUT_BUFFER_SIZE];
    printf("\n\nISDNSSProcedure;");
    if (record->trafficActivityCode) {
        char* hex_result = buffer_to_hex(record->trafficActivityCode->buf, record->trafficActivityCode->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->callIdentificationNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->callIdentificationNumber->buf, record->callIdentificationNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->recordSequenceNumber) {
        uint64_t hex_result = hexBufferToDecimal(record->recordSequenceNumber->buf, record->recordSequenceNumber->size);
        printf("%ld;", hex_result);
    }
    if (record->typeOfCallingSubscriber) {
        uint64_t hex_result = hexBufferToDecimal(record->typeOfCallingSubscriber->buf, record->typeOfCallingSubscriber->size);
        printf("%ld;", hex_result);
    }
    if (record->dateForStartOfCharge) {
        char* hex_result = buffer_to_hex(record->dateForStartOfCharge->buf,record->dateForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->timeForStartOfCharge) {
        char* hex_result = BCD(record->timeForStartOfCharge->buf,record->timeForStartOfCharge->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->tariffClass) {
        uint64_t hex_result = hexBufferToDecimal(record->tariffClass->buf, record->tariffClass->size);
        printf("%ld;", hex_result);
    }
    if (record->exchangeIdentity) {
        printf("%s;", record->exchangeIdentity->buf);
    }
    if (record->restartDuringOutputIndicator) {
        printf("%ls;", record->restartDuringOutputIndicator);
    }
    if (record->incompleteCallDataIndicator) {
        printf("%ls;", record->incompleteCallDataIndicator);
    }
    if (record->forloppDuringOutputIndicator) {
        printf("%ls;", record->forloppDuringOutputIndicator);
    }
    if (record->servedSubscriberNumber){
        memset(decoded_tbcd, 0, sizeof(decoded_tbcd));
        decode_tbcd(record->servedSubscriberNumber->buf, record->servedSubscriberNumber->size, decoded_tbcd);
        printf("%s;", decoded_tbcd);
    }
    if (record->chargedParty) {
        if (record->chargedParty != NULL) {
            printf("%s;", getChargedparty(*record->chargedParty));
        } else {
            printf(";");
        }
    }
    if (record->switchIdentity) {
        char* hex_result = buffer_to_hex(record->switchIdentity->buf,record->switchIdentity->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->bladeID) {
        char* hex_result = buffer_to_hex(record->bladeID->buf,record->bladeID->size);
        printf("%s;", hex_result);
        free(hex_result);
    }
    if (record->outputType) {
        if (record->outputType != NULL) {
            printf("%s;", getOutputType(*record->outputType));
        } else {
            printf(";");
        }
    }
    printf("\n");
    return;
}

void initialise_gsmchar() {
    // Populate default GSM mappings
    for (int i = 0; i < GSM_CHAR_COUNT; i++) {
        GSMCHAR[i] = (i >= 32 && i < 128) ? (char)i : '?';
    }

    // Override with GSM-specific mappings
    GSMCHAR[0x24] = '\xa4';
    GSMCHAR[0x40] = '\xa1';
    GSMCHAR[0x5b] = '\xc4';
    GSMCHAR[0x5c] = '\xd6';
    GSMCHAR[0x5d] = '\xd1';
    GSMCHAR[0x5e] = '\xdc';
    GSMCHAR[0x5f] = '\xa7';
    GSMCHAR[0x60] = '\xbf';
    GSMCHAR[0x7b] = '\xe4';
    GSMCHAR[0x7c] = '\xf6';
    GSMCHAR[0x7d] = '\xf1';
    GSMCHAR[0x7e] = '\xfc';
    GSMCHAR[0x7f] = '\xe0';
    GSMCHAR[0x00] = '@';
    GSMCHAR[0x01] = '\xa3';
    GSMCHAR[0x02] = '$';
    GSMCHAR[0x03] = '\xa5';
    GSMCHAR[0x04] = '\xe8';
    GSMCHAR[0x05] = '\xe9';
    GSMCHAR[0x06] = '\xf9';
    GSMCHAR[0x07] = '\xec';
    GSMCHAR[0x08] = '\xf2';
    GSMCHAR[0x09] = '\xc7';
    GSMCHAR[0x0b] = '\xd8';
    GSMCHAR[0x0c] = '\xf8';
    GSMCHAR[0x0e] = '\xc5';
    GSMCHAR[0x0f] = '\xe5';
    GSMCHAR[0x1c] = '\xc6';
    GSMCHAR[0x1d] = '\xe6';
    GSMCHAR[0x1e] = '\xdf';
    GSMCHAR[0x1f] = '\xc9';
}

unsigned long Integer(const unsigned char* octets, size_t size) {
    unsigned long result = 0;
    for (size_t i = 0; i < size; ++i) {
        result = (result << 8) | octets[i];
    }
    return result;
}
