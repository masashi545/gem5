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

  stimgen.cpp --

  Original Author: Martin Janssen, Synopsys, Inc., 2002-02-15

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

/*****************************************/
/* Implementation Filename:  stimgen.cc  */
/*****************************************/

#include "stimgen.h"

void stimgen::entry()
{
    int i;
    int j;

    ready.write(0);

    for (i = 0; i < 64; i++)
    { // integer in1 (6 bits of data)
        for (j = 0; j < 64; j++)
        { // integer in2 (6 bits of data)
            in1.write(i);
            in2.write(j);
            ready.write(1);
            wait();

            ready.write(0);
            wait();

            cout << in1.read().to_uint() << " + " << in2.read().to_uint()
                 << " = " << result.read().to_uint()
                 << " (" << result << ")" << endl;
        }
    }

    sc_stop();
}
