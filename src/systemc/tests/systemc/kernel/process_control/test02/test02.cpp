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

/*****************************************************************************

  test02.cpp -- Test of resume after dynamic event completion

  Original Author: Andy Goodrich

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

  Revision log at end of the file to let __LINE__ give the same results
  after a check-in.
 *****************************************************************************/

#include "systemc.h"

SC_MODULE(DUT)
{
    SC_CTOR(DUT)
    {
        SC_CTHREAD(cthread, m_clk.pos());
        reset_signal_is(m_reset, true);
        m_cthread = sc_get_current_process_handle();

        SC_METHOD(dynamic_method);
        m_dynamic_method = sc_get_current_process_handle();

        SC_THREAD(dynamic_thread);
        m_dynamic_thread = sc_get_current_process_handle();

        SC_METHOD(static_method);
        sensitive << m_event1 << m_event2;
        m_static_method = sc_get_current_process_handle();

        SC_THREAD(static_thread);
        sensitive << m_event1 << m_event2;
        m_static_thread = sc_get_current_process_handle();

        SC_CTHREAD(stimulus, m_clk.pos());
        reset_signal_is(m_reset, true);
    }
    void cthread()
    {
        for (;;)
        {
            wait();
            cout << sc_time_stamp() << ":      clocked thread (" << __LINE__
                 << ") after wait on m_clk.pos() " << endl;
        }
    }
    void dynamic_method()
    {
        static int state = 0;
        switch (state)
        {
        case 0:
            next_trigger(m_clk.posedge_event());
            cout << sc_time_stamp() << ":      dynamic method (" << __LINE__
                 << "," << state << ") initialization call " << endl;
            state = 1;
            break;
        default:
        case 1:
            next_trigger(m_event1 & m_event2);
            cout << sc_time_stamp() << ":      dynamic method (" << __LINE__
                 << "," << state << ") after wait on m_clk.posedge() " << endl;
            break;
        }
    }
    void dynamic_thread()
    {
        cout << sc_time_stamp() << ":      dynamic thread (" << __LINE__ << ")"
             << " initialization call " << endl;
        wait(m_clk.posedge_event());
        cout << sc_time_stamp() << ":      dynamic thread (" << __LINE__
             << ") after wait on m_clk.posedge_event() " << endl;
        for (;;)
        {
            wait(m_event1 & m_event2);
            cout << sc_time_stamp() << ":      dynamic thread (" << __LINE__
                 << ") after wait on m_event1 & m_event2 " << endl;
        }
    }
    void static_method()
    {
        static bool initialized = false;
        if (!initialized)
        {
            initialized = true;
            cout << sc_time_stamp() << ":      static method (" << __LINE__
                 << ")"
                 << " initialization call " << endl;
        }
        else
        {
            cout << sc_time_stamp() << ":      static method (" << __LINE__
                 << ") after wait on m_event1 | m_event2 " << endl;
        }
    }
    void static_thread()
    {
        cout << sc_time_stamp() << ":      static thread (" << __LINE__ << ")"
             << " initialization call " << endl;
        for (;;)
        {
            wait();
            cout << sc_time_stamp() << ":      static thread (" << __LINE__
                 << ") after wait on m_event1 | m_event2 " << endl;
        }
    }
    void stimulus()
    {
        for (;;)
        {
            wait();
            wait();
            cout << sc_time_stamp() << ": stimulus ("
                 << __LINE__ << ") - suspending all processes" << endl;
            m_cthread.suspend();
            m_dynamic_method.suspend();
            m_dynamic_thread.suspend();
            m_static_method.suspend();
            m_static_thread.suspend();
            wait();

            m_event1.notify(SC_ZERO_TIME);
            cout << sc_time_stamp() << ": stimulus ("
                 << __LINE__ << ") - firing event1 " << endl;
            wait();
            m_event2.notify(SC_ZERO_TIME);
            cout << sc_time_stamp() << ": stimulus ("
                 << __LINE__ << ") - firing event2 " << endl;
            wait();
            wait();

            m_cthread.resume();
            m_dynamic_method.resume();
            m_dynamic_thread.resume();
            m_static_method.resume();
            m_static_thread.resume();
            cout << endl
                 << sc_time_stamp() << ": stimulus ("
                 << __LINE__ << ") - resuming all processes" << endl;
            wait();
            wait();
            wait();
            sc_stop();
        }
    }
    sc_in<bool> m_clk;
    sc_process_handle m_cthread;
    sc_process_handle m_dynamic_method;
    sc_process_handle m_dynamic_thread;
    sc_event m_event1;
    sc_event m_event2;
    sc_event m_event3;
    sc_event m_event4;
    sc_in<bool> m_reset;
    sc_process_handle m_static_method;
    sc_process_handle m_static_thread;
};

int sc_main(int argc, char *argv[])
{
    sc_core::sc_allow_process_control_corners = true;
    sc_clock clock;
    DUT dut("dut");
    sc_signal<bool> reset;

    dut.m_clk(clock);
    dut.m_reset(reset);

    sc_core::sc_allow_process_control_corners = true;
    reset = true;
    sc_start(1, SC_NS);
    reset = false;
    sc_start(21, SC_NS);

    cout << "Program completed" << endl;
    return 0;
}

// $Log: test02.cpp,v $
// Revision 1.6  2011/04/02 00:08:27  acg
//  Andy Goodrich: turn off corner case error checking.
//
// Revision 1.5  2011/03/07 19:32:11  acg
//  Andy Goodrich: addition to set sc_core::sc_allow_process_control_corners
//  to true so that this test avoids corner case error messages.
//
// Revision 1.4  2011/02/20 13:43:58  acg
//  Andy Goodrich: updates for IEEE 1666 2011.
//
// Revision 1.3  2011/02/14 17:00:00  acg
//  Andy Goodrich: updated copyright and added cvs logging information inline.
//
// Revision 1.2  2011/01/20 16:55:23  acg
//  Andy Goodrich: changes for IEEE 1666 2011.
//
// Revision 1.1.1.1  2006/12/15 20:26:03  acg
// systemc_tests-2.3
//
// Revision 1.1  2006/12/14 21:40:06  acg
//  Andy Goodrich: moving test to new directory.
//
// Revision 1.2  2006/04/20 19:43:34  acg
//  Andy Goodrich: moved CVS log to end of file so that __LINE__ does not
//  change when a checkin is done.
//
// Revision 1.1  2006/04/17 20:11:02  acg
//  Andy Goodrich: First inclusion of test for suspend and resume support.
//
