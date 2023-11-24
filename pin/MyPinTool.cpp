#include "pin.H"
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <sstream>

FILE* trace;
PIN_LOCK lock;
BOOL startRecording;

VOID findFirstThread(THREADID tid) {
    if (tid == 1 && !startRecording) {
        printf("Found First Thread :) ; Start Recording \n");
        startRecording = TRUE;
    }
}

VOID RecordMemRead(THREADID tid, ADDRINT addr)
{
    fprintf(trace, "Thread: %d Memory Access: R on ADDR: %p\n", tid, reinterpret_cast<void*>(addr));
}

VOID RecordMemWrite(THREADID tid, ADDRINT addr)
{
    fprintf(trace, "Thread: %d Memory Access: W on ADDR: %p\n", tid, reinterpret_cast<void*>(addr));
}

VOID RecordLockAcquisition(THREADID tid, ADDRINT flags_reg)
{
    // Determine if lock failed or not
    unsigned int zf_bit = 1 << 6;
    int result = flags_reg & zf_bit;

    if (!result) {
        // Failed
        fprintf(trace, "Thread: %d Lock Failed\n", tid);
    } else {
        // Acquired Lock
        fprintf(trace, "Thread: %d Lock Acquisition\n", tid);
    }
}

VOID Instruction(INS ins, VOID* v)
{   
    // Acquire Lock
    PIN_GetLock(&lock, 0);

    // Assuming the second thread has thread ID 1
    if (startRecording == FALSE) {   
        // First Thread Found

        if (INS_IsMemoryRead(ins) || INS_IsMemoryWrite(ins)) {
            INS_InsertPredicatedCall(ins, IPOINT_BEFORE, (AFUNPTR)findFirstThread, IARG_THREAD_ID, IARG_END);
        }
        
        // Do this such that we only start recording things after thread 2 starts doing things
        // meaning that we are capturing the region of interest :)
    }

    if (startRecording == TRUE) {
        // Log memory access events

        UINT32 memOperands = INS_MemoryOperandCount(ins);

        // Iterate over each memory operand of the instruction.
        for (UINT32 memOp = 0; memOp < memOperands; memOp++)
        {
            if (INS_MemoryOperandIsRead(ins, memOp))
            {   
                INS_InsertPredicatedCall(ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead, IARG_THREAD_ID, IARG_MEMORYOP_EA, memOp,IARG_END);
            }
            // Note that in some architectures a single memory operand can be
            // both read and written (for instance incl (%eax) on IA-32)
            // In that case we instrument it once for read and once for write.
            if (INS_MemoryOperandIsWritten(ins, memOp))
            {
               INS_InsertPredicatedCall(ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite, IARG_THREAD_ID, IARG_MEMORYOP_EA, memOp,IARG_END);
            }
        }

        // Log lock events; NOTE: Not sure if lock events measured in atomic reads and writes, but we assume that cause otherwise would be not worthwhile...
        OPCODE op = INS_Opcode(ins);
        bool cmpxchg = op == XED_ICLASS_CMPXCHG || op == XED_ICLASS_CMPXCHG16B || op == XED_ICLASS_CMPXCHG8B || op == XED_ICLASS_CMPXCHG_LOCK || op == XED_ICLASS_CMPXCHG16B_LOCK || op == XED_ICLASS_CMPXCHG8B_LOCK;

        if (INS_IsAtomicUpdate(ins)) {
            if (cmpxchg) {
                printf("Atomic Update :) with opcode: %d\n", op);
                INS_InsertPredicatedCall(
                ins, IPOINT_AFTER, (AFUNPTR) RecordLockAcquisition
                , IARG_THREAD_ID
                // must use REG_RFLAGS (although it is not documented)
                // REG_EFLAGS and REG_FLAGS produce failures
                // see http://tech.groups.yahoo.com/group/pinheads/message/6581
                , IARG_REG_VALUE, REG_RFLAGS
                , IARG_END
                );
            }
        } 
    }

    // Release Lock
    PIN_ReleaseLock(&lock);
}

VOID Fini(INT32 code, VOID* v)
{
    fclose(trace);
}

int main(int argc, char* argv[])
{
    PIN_Init(argc, argv);

    // Open Trace File Descriptor
    trace = fopen("output_mem_trace.log", "a");
    startRecording = FALSE;

    // Initialize the PIN lock
    PIN_InitLock(&lock);

    INS_AddInstrumentFunction(Instruction, 0);
    PIN_AddFiniFunction(Fini, 0);

    PIN_StartProgram();

    return 0;
}
