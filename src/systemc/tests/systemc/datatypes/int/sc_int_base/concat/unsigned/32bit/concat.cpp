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

  concat.cpp --

  Original Author: Martin Janssen, Synopsys, Inc., 2002-02-15

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

#include "systemc.h"

#define WIDTH 32

int sc_main(int ac, char *av[])
{

    sc_uint_base a_su32(WIDTH), b_su32(WIDTH);

    for (int i = 0; i < WIDTH - 1; i++)
    {
        cout << "i = " << i << ": ";
        a_su32 = i;
        b_su32 = (a_su32.range(WIDTH - 1, i + 1), a_su32.range(i, 0));
        // Output variables to avoid erroneous optimization observed on RHEL6 with g++-4.4.6.
        cout << a_su32 << (a_su32 == b_su32 ? " == " : " != ") << b_su32 << endl;
        sc_assert(a_su32 == b_su32);
    }

    return 0;
}
