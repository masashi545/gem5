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

  test02.cpp --

  Original Author: Martin Janssen, Synopsys, Inc., 2002-02-15

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

// test of the sc_mutex_if interface

#include "systemc.h"

SC_MODULE(mod_a)
{
    sc_port<sc_mutex_if> mutex;

    void write(const char *msg)
    {
        cout << sc_time_stamp() << " " << msg << endl;
    }

    void proc_a()
    {
        while (true)
        {
            wait(1, SC_NS);
            write("proc_a - lock requested");
            mutex->lock();
            write("proc_a - lock obtained");
            wait(2, SC_NS);
            if (mutex->unlock() == 0)
            {
                write("proc_a - unlock successful");
            }
            else
            {
                write("proc_a - unlock failed");
            }
            wait(3, SC_NS);
            if (mutex->trylock() == 0)
            {
                write("proc_a - trylock successful");
            }
            else
            {
                write("proc_a - trylock failed");
            }
            if (mutex->unlock() == 0)
            {
                write("proc_a - unlock successful");
            }
            else
            {
                write("proc_a - unlock failed");
            }
        }
    }

    SC_CTOR(mod_a)
    {
        SC_THREAD(proc_a);
    }
};

SC_MODULE(mod_b)
{
    sc_port<sc_mutex_if> mutex;

    void write(const char *msg)
    {
        cout << sc_time_stamp() << " " << msg << endl;
    }

    void proc_b()
    {
        while (true)
        {
            wait(2, SC_NS);
            write("proc_b - lock requested");
            mutex->lock();
            write("proc_b - lock obtained");
            wait(4, SC_NS);
            if (mutex->unlock() == 0)
            {
                write("proc_b - unlock successful");
            }
            else
            {
                write("proc_b - unlock failed");
            }
            wait(3, SC_NS);
            if (mutex->trylock() == 0)
            {
                write("proc_b - trylock successful");
            }
            else
            {
                write("proc_b - trylock failed");
            }
            if (mutex->unlock() == 0)
            {
                write("proc_b - unlock successful");
            }
            else
            {
                write("proc_b - unlock failed");
            }
        }
    }

    SC_CTOR(mod_b)
    {
        SC_THREAD(proc_b);
    }
};

int sc_main(int, char *[])
{
    mod_a a("a");
    mod_b b("b");
    sc_mutex mutex("mutex");

    a.mutex(mutex);
    b.mutex(mutex);

    sc_start(40, SC_NS);

    return 0;
}
