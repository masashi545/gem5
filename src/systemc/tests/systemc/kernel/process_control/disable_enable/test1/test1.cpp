/*****************************************************************************

  Licensed to Accellera Systems Initiative Inc. (Accellera) under one or
  more contributor license agreements.  See the NOTICE file distributed
  with this work for additional information regarding copyright ownership.
  Accellera licenses this file to you under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with the
  License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
  implied.  See the License for the specific language governing
  permissions and limitations under the License.

 *****************************************************************************/

//*****************************************************************************
//
//  test01.cpp -- test self disables on processes
//
//  Original Author: Andy Goodrich, Forte Design Systems, Inc.
//
//  CVS MODIFICATION LOG - modifiers, enter your name, affiliation, date and
//  changes you are making here.
//
// $Log: test1.cpp,v $
// Revision 1.2  2009/07/28 01:09:48  acg
//  Andy Goodrich: replacement test using standardized environment.
//
//*****************************************************************************

#define SC_INCLUDE_DYNAMIC_PROCESSES
#include "systemc.h"

enum my_process_states
{
    ST_DISABLED,
    ST_NORMAL,
    ST_SUSPENDED
};

inline ostream &time_stamp(ostream &os)
{
    os << dec << sc_time_stamp() << "[" << sc_delta_count() << "]: ";
    return os;
}

SC_MODULE(top)
{
    // constructor:

    SC_CTOR(top) : m_state_cthread0(ST_NORMAL),
                   m_state_method0(ST_NORMAL),
                   m_state_thread0(ST_NORMAL)
    {
        SC_THREAD(stimulator0);

        SC_CTHREAD(target_cthread0, m_clk.pos());
        m_target_cthread0 = sc_get_current_process_handle();

        SC_METHOD(target_method0);
        sensitive << m_clk.pos();
        m_target_method0 = sc_get_current_process_handle();

        SC_THREAD(target_thread0);
        m_target_thread0 = sc_get_current_process_handle();
    }

    // processes:

    void stimulator0();
    void target_cthread0();
    void target_method0();
    void target_thread0();

    // Storage:

    sc_in<bool> m_clk;
    int m_state_cthread0;
    int m_state_method0;
    int m_state_thread0;
    sc_process_handle m_target_cthread0;
    sc_process_handle m_target_method0;
    sc_process_handle m_target_thread0;
};

void top::stimulator0()
{
    const char *name = "stimulator";
    wait(10, SC_NS);
    cout << endl;
    time_stamp(cout) << name << ": enabling target_cthread0" << endl;
    cout << endl;
    m_state_cthread0 = ST_NORMAL;
    m_target_cthread0.enable();
    wait(10, SC_NS);

    cout << endl;
    time_stamp(cout) << name << ": enabling target_method0" << endl;
    cout << endl;
    m_state_method0 = ST_NORMAL;
    m_target_method0.enable();
    wait(10, SC_NS);

    cout << endl;
    time_stamp(cout) << name << ": enabling target_thread0" << endl;
    cout << endl;
    m_state_thread0 = ST_NORMAL;
    m_target_thread0.enable();
    ::sc_core::wait(1000, SC_NS);

    cout << endl;
    time_stamp(cout) << name << ": terminating" << endl;
    sc_stop();
}

void top::target_cthread0()
{
    int i;
    const char *name = "target_cthread0";

    time_stamp(cout) << name << ": starting" << endl;
    time_stamp(cout) << name << ": issuing self disable" << endl;
    m_state_cthread0 = ST_DISABLED;
    m_target_cthread0.disable();
    time_stamp(cout) << name << ": after issuing self disable" << endl;
    cout << endl;
    for (i = 0; i < 100; i++)
    {
        wait();
        if (m_state_cthread0 == ST_DISABLED)
        {
            time_stamp(cout) << name << ": ERROR should not see this" << endl;
        }
    }
    time_stamp(cout) << name << ": terminating" << endl;
}

void top::target_method0()
{
    const char *name = "target_method0";
    static int state = 0;
    switch (state)
    {
    case 0:
        time_stamp(cout) << name << ": starting" << endl;
        time_stamp(cout) << name << ": issuing self disable" << endl;
        m_state_method0 = ST_DISABLED;
        m_target_method0.disable();
        time_stamp(cout) << name << ": after issuing self disable" << endl;
        cout << endl;
        break;
    default:
        if (m_state_method0 == ST_DISABLED)
        {
            time_stamp(cout) << name << ": ERROR should not see this" << endl;
        }
        break;
    case 99:
        time_stamp(cout) << name << ": terminating" << endl;
        break;
    }
    state++;
}

void top::target_thread0()
{
    const char *name = "target_thread0";

    time_stamp(cout) << name << ": starting" << endl;
    time_stamp(cout) << name << ": issuing self disable" << endl;
    m_state_thread0 = ST_DISABLED;
    m_target_thread0.disable();
    time_stamp(cout) << name << ": after issuing self disable" << endl;
    cout << endl;

    // We wait a long enough time that our event will not occur until
    // after we are re-enabled. Otherwise this thread will just go away
    // quietly when the disable cancels the event.

    ::sc_core::wait(80, SC_NS);
    if (m_state_thread0 == ST_DISABLED)
    {
        time_stamp(cout) << name << ": ERROR should not see this" << endl;
    }
    time_stamp(cout) << name << ": terminating" << endl;
}

int sc_main(int argc, char *argv[])
{
    sc_clock clock("clock", 1.0, SC_NS);

    top *top_p = new top("top");
    top_p->m_clk(clock);

    sc_start();
    return 0;
}
