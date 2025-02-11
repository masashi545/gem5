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

  T_2_3_1_5_neg.cpp --

  Original Author: Martin Janssen, Synopsys, Inc., 2002-02-15

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

#include "systemc.h"

#define MYNAME T_2_3_1_5

const int WIDTH = 8;
typedef sc_bv<WIDTH> my_vector;
typedef sc_signal<my_vector> signal_vector;

#include "T_2_3_1.h"

void MYNAME::entry()
{
    my_vector a;
    my_vector b;

    a = x;
    b = y;
    z = a | b;
    wait();
    a = x.read() | y.read();
    b = x.read() ^ y.read();
    z = a & b;
    wait();
    a = x.read() & y.read();
    b = x.read() | y.read();
    z = a ^ b;
    wait();
    a = ~x.read();
    b = ~y.read();
    z = a | b;
    wait();
}

int sc_main(int, char *[])
{
    return 0;
}
